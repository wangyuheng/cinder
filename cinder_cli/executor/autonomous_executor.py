"""
Autonomous Executor - Main coordinator for task execution.
"""

from __future__ import annotations

import questionary
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from cinder_cli.config import Config
from cinder_cli.database import DecisionDatabase
from cinder_cli.proxy_decision import ProxyDecisionMaker, ConfidenceScorer
from cinder_cli.executor.task_planner import TaskPlanner
from cinder_cli.executor.code_generator import CodeGenerator
from cinder_cli.executor.reflection_engine import ReflectionEngine
from cinder_cli.executor.file_operations import FileOperations
from cinder_cli.executor.execution_logger import ExecutionLogger

console = Console()


class AutonomousExecutor:
    """Main coordinator for autonomous task execution."""

    def __init__(self, config: Config):
        self.config = config
        self.task_planner = TaskPlanner(config)
        self.code_generator = CodeGenerator(config)
        self.reflection_engine = ReflectionEngine(config)
        self.file_operations = FileOperations(config)
        self.execution_logger = ExecutionLogger(config)
        self.decision_db = DecisionDatabase(config.database_path)
        self.soul_meta = self._load_soul_meta()

    def _load_soul_meta(self) -> dict[str, Any]:
        """Load soul metadata for decision making."""
        import yaml
        meta_path = self.config.get("meta_path", "")
        if not meta_path:
            soul_path = self.config.get("soul_path", "soul.md")
            meta_path = soul_path.replace(".md", ".meta.yaml")

        try:
            with open(meta_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {"traits": {}}

    def _make_proxy_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make a proxy decision and log it."""
        if not self.soul_meta.get("traits"):
            return options[0] if options else {}

        decision_maker = ProxyDecisionMaker(self.soul_meta)
        result = decision_maker.make_decision(context, options)

        if not result:
            return options[0] if options else {}

        decision_id = self.decision_db.insert_decision(
            context={"description": context},
            soul_rules={"traits": self.soul_meta.get("traits", {})},
            decision=result.get("decision", {}),
            confidence=result.get("confidence", 0.5),
            requires_human=result.get("requires_human", False),
        )

        console.print(f"[dim]决策 #{decision_id}: 置信度 {result.get('confidence', 0.5):.2f}[/dim]")

        return result.get("decision", options[0] if options else {})

    def execute(
        self,
        goal: str,
        mode: str = "auto",
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a goal autonomously.

        Args:
            goal: Natural language description of the goal
            mode: Execution mode (interactive, dry-run, auto)
            constraints: Optional constraints for execution

        Returns:
            Execution result with status, files created, and other metadata
        """
        console.print(f"\n[bold cyan]执行目标:[/bold cyan] {goal}")

        if mode == "dry-run":
            return self._dry_run(goal, constraints)

        if mode == "interactive":
            return self._interactive_run(goal, constraints)

        return self._auto_run(goal, constraints)

    def _auto_run(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Run in automatic mode with strict phase separation."""
        execution_flow = {
            "goal": goal,
            "phases": [],
            "status": "in_progress",
        }

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[bold blue]PHASE 1: PLAN[/bold blue]", total=None)

                plan_result = self._execute_plan_phase(goal, constraints, progress, task)
                execution_flow["phases"].append(plan_result)

                if not plan_result.get("success", False):
                    return self._create_failure_result(goal, "Plan phase failed", execution_flow)

                task = progress.add_task("[bold green]PHASE 2: GENERATION[/bold green]", total=None)
                generation_results = self._execute_generation_phase(plan_result["plan"], progress, task)
                execution_flow["phases"].extend(generation_results)

                task = progress.add_task("[bold yellow]PHASE 3: EVALUATION[/bold yellow]", total=None)
                evaluation_result = self._execute_evaluation_phase(generation_results, progress, task)
                execution_flow["phases"].append(evaluation_result)

                if not evaluation_result.get("all_approved", False):
                    return self._create_failure_result(goal, "Evaluation phase failed", execution_flow)

                task = progress.add_task("[bold magenta]PHASE 4: DECISION[/bold magenta]", total=None)
                decision_result = self._execute_decision_phase(evaluation_result, progress, task)
                execution_flow["phases"].append(decision_result)

                execution_result = self._execute_files_creation(decision_result, progress)

            execution_flow["status"] = "success"
            console.print("\n[green]✓ 执行完成[/green]")

            return {
                "status": "success",
                "goal": goal,
                "execution_flow": execution_flow,
                "results": execution_result,
            }

        except Exception as e:
            execution_flow["status"] = "error"
            execution_flow["error"] = str(e)
            console.print(f"\n[red]✗ 执行失败: {e}[/red]")
            return {
                "status": "error",
                "goal": goal,
                "execution_flow": execution_flow,
                "error": str(e),
            }

    def _execute_plan_phase(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
        progress: Progress,
        task: Any,
    ) -> dict[str, Any]:
        """Execute Plan phase with validation."""
        progress.update(task, description="[bold blue]PHASE 1: PLAN - Understanding goal...[/bold blue]")

        plan = self.task_planner.decompose_goal_with_validation(
            goal,
            constraints,
            max_retries=2,
            quality_threshold=0.7,
        )

        validation = plan.get("validation", {})
        quality_score = validation.get("quality_score", 0)

        progress.update(task, description=f"[bold blue]PHASE 1: PLAN - Quality: {quality_score:.2f}[/bold blue]")

        if quality_score < 0.7:
            console.print(f"[yellow]⚠ Plan quality low: {quality_score:.2f}[/yellow]")
            if validation.get("issues"):
                for issue in validation["issues"]:
                    console.print(f"  - {issue}")

        console.print(f"[dim]Plan phase complete: {len(plan.get('subtasks', []))} tasks, quality={quality_score:.2f}[/dim]")

        return {
            "phase": "plan",
            "success": quality_score >= 0.7,
            "plan": plan,
            "quality_score": quality_score,
            "attempts": plan.get("attempts", 1),
        }

    def _execute_generation_phase(
        self,
        plan: dict[str, Any],
        progress: Progress,
        task: Any,
    ) -> list[dict[str, Any]]:
        """Execute Generation phase with iterations."""
        results = []
        subtasks = plan.get("subtasks", [])

        for i, subtask in enumerate(subtasks, 1):
            progress.update(
                task,
                description=f"[bold green]PHASE 2: GENERATION - Task {i}/{len(subtasks)}[/bold green]"
            )

            generation_result = self.code_generator.generate_with_iterations(
                subtask["description"],
                subtask.get("language", "python"),
                subtask.get("constraints"),
                max_iterations=3,
                quality_threshold=0.8,
            )

            results.append({
                "phase": "generation",
                "subtask_id": subtask.get("id"),
                "subtask": subtask,
                "code": generation_result.get("code"),
                "iterations": generation_result.get("iterations", 1),
                "quality_score": generation_result.get("final_score", 0),
                "quality_threshold_met": generation_result.get("quality_threshold_met", False),
                "iteration_history": generation_result.get("iteration_history", []),
            })

            console.print(f"[dim]Task {i}: {generation_result.get('iterations', 1)} iterations, quality={generation_result.get('final_score', 0):.2f}[/dim]")

        return results

    def _execute_evaluation_phase(
        self,
        generation_results: list[dict[str, Any]],
        progress: Progress,
        task: Any,
    ) -> dict[str, Any]:
        """Execute Evaluation phase with comprehensive assessment."""
        progress.update(task, description="[bold yellow]PHASE 3: EVALUATION - Assessing quality...[/bold yellow]")

        evaluations = []
        all_approved = True

        for gen_result in generation_results:
            code = gen_result.get("code", "")
            subtask = gen_result.get("subtask", {})

            evaluation = self.reflection_engine.evaluate_comprehensive(
                code,
                subtask,
                self.soul_meta,
            )

            evaluations.append({
                "subtask_id": gen_result.get("subtask_id"),
                "evaluation": evaluation,
                "approved": evaluation.get("approved", False),
            })

            if not evaluation.get("approved", False):
                all_approved = False

            quality_score = evaluation.get("quality_score", 0)
            console.print(f"[dim]Evaluated {gen_result.get('subtask_id')}: quality={quality_score:.2f}, approved={evaluation.get('approved', False)}[/dim]")

        avg_quality = sum(e["evaluation"].get("quality_score", 0) for e in evaluations) / len(evaluations) if evaluations else 0

        return {
            "phase": "evaluation",
            "evaluations": evaluations,
            "all_approved": all_approved,
            "average_quality": round(avg_quality, 2),
        }

    def _execute_decision_phase(
        self,
        evaluation_result: dict[str, Any],
        progress: Progress,
        task: Any,
    ) -> dict[str, Any]:
        """Execute Decision phase based on Soul profile."""
        progress.update(task, description="[bold magenta]PHASE 4: DECISION - Making decisions...[/bold magenta]")

        decisions = []

        for eval_item in evaluation_result.get("evaluations", []):
            evaluation = eval_item.get("evaluation", {})
            quality_score = evaluation.get("quality_score", 0)

            if self.soul_meta.get("traits"):
                decision_options = [
                    {
                        "text": "接受代码",
                        "risk": "low",
                        "quality": quality_score,
                    },
                    {
                        "text": "请求修改",
                        "risk": "medium",
                        "quality": 0.6,
                    },
                    {
                        "text": "重新生成",
                        "risk": "high",
                        "quality": 0.5,
                    },
                ]

                decision = self._make_proxy_decision(
                    f"代码质量评分: {quality_score:.2f}，如何处理？",
                    decision_options,
                )

                decisions.append({
                    "subtask_id": eval_item.get("subtask_id"),
                    "decision": decision,
                    "accepted": decision.get("text") == "接受代码",
                })
            else:
                decisions.append({
                    "subtask_id": eval_item.get("subtask_id"),
                    "decision": {"text": "接受代码", "quality": quality_score},
                    "accepted": evaluation.get("approved", False),
                })

        accepted_count = sum(1 for d in decisions if d.get("accepted", False))

        console.print(f"[dim]Decision phase complete: {accepted_count}/{len(decisions)} accepted[/dim]")

        return {
            "phase": "decision",
            "decisions": decisions,
            "accepted_count": accepted_count,
        }

    def _execute_files_creation(
        self,
        decision_result: dict[str, Any],
        progress: Progress,
    ) -> list[dict[str, Any]]:
        """Execute file creation based on decisions."""
        results = []

        for decision in decision_result.get("decisions", []):
            if decision.get("accepted", False):
                subtask_id = decision.get("subtask_id")

                gen_result = next(
                    (r for r in decision_result.get("generation_results", []) if r.get("subtask_id") == subtask_id),
                    None
                )

                if gen_result:
                    file_result = self.file_operations.create_file(
                        gen_result.get("subtask", {}).get("file_path", "output.py"),
                        gen_result.get("code", ""),
                    )

                    results.append({
                        "subtask_id": subtask_id,
                        "file_result": file_result,
                        "code": gen_result.get("code"),
                    })

        return results

    def _create_failure_result(
        self,
        goal: str,
        reason: str,
        execution_flow: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a failure result."""
        console.print(f"\n[red]✗ 执行失败: {reason}[/red]")
        return {
            "status": "failed",
            "goal": goal,
            "reason": reason,
            "execution_flow": execution_flow,
        }

    def _interactive_run(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Run in interactive mode with user confirmation at each step."""
        console.print("\n[yellow]交互模式 - 每步需要确认[/yellow]\n")

        task_tree = self.task_planner.decompose_goal(goal, constraints)

        console.print("[bold]任务分解:[/bold]")
        for i, subtask in enumerate(task_tree.get("subtasks", []), 1):
            console.print(f"  {i}. {subtask['description']}")

        proceed = questionary.confirm(
            "是否继续执行?",
            default=True,
        ).ask()

        if not proceed:
            return {
                "status": "cancelled",
                "goal": goal,
                "task_tree": task_tree,
                "results": [],
            }

        results = []
        for subtask in task_tree.get("subtasks", []):
            console.print(f"\n[bold cyan]任务: {subtask['description']}[/bold cyan]")

            code = self.code_generator.generate_code(
                subtask["description"],
                subtask.get("language", "python"),
            )

            console.print(Panel(
                Syntax(code, subtask.get("language", "python"), theme="monokai"),
                title="生成的代码",
                border_style="blue",
            ))

            action = questionary.select(
                "如何处理此代码?",
                choices=[
                    "接受并创建文件",
                    "重新生成",
                    "跳过此任务",
                    "取消执行",
                ],
            ).ask()

            if action == "取消执行":
                break
            elif action == "跳过此任务":
                continue
            elif action == "重新生成":
                for _ in range(3):
                    code = self.code_generator.generate_code(
                        subtask["description"],
                        subtask.get("language", "python"),
                    )
                    console.print(Panel(
                        Syntax(code, subtask.get("language", "python"), theme="monokai"),
                        title="重新生成的代码",
                        border_style="blue",
                    ))
                    accept = questionary.confirm("接受此代码?", default=True).ask()
                    if accept:
                        break

            if action != "跳过此任务":
                file_result = self.file_operations.create_file(
                    subtask.get("file_path", "output.py"),
                    code,
                )
                results.append({
                    "subtask": subtask,
                    "code": code,
                    "file_result": file_result,
                })

        self.execution_logger.log_execution(goal, task_tree, results)

        console.print("\n[green]✓ 执行完成[/green]")
        return {
            "status": "success",
            "goal": goal,
            "task_tree": task_tree,
            "results": results,
        }

    def _dry_run(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Preview what would be done without executing."""
        console.print("\n[yellow]预览模式 - 不会创建实际文件[/yellow]\n")

        task_tree = self.task_planner.decompose_goal(goal, constraints)

        console.print("[bold]任务分解:[/bold]")
        for i, subtask in enumerate(task_tree.get("subtasks", []), 1):
            console.print(f"  {i}. {subtask['description']}")

        complexity = self.task_planner.estimate_complexity(task_tree.get("subtasks", []))
        console.print(f"\n[bold]复杂度估算:[/bold]")
        console.print(f"  总复杂度: {complexity['total']}")
        console.print(f"  预计时间: {complexity['estimated_time_minutes']} 分钟")

        return {
            "status": "dry-run",
            "goal": goal,
            "task_tree": task_tree,
            "complexity": complexity,
        }
