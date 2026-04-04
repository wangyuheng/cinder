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
        """Run in automatic mode with proxy decision making."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("分解任务...", total=None)
            task_tree = self.task_planner.decompose_goal(goal, constraints)
            progress.remove_task(task)

            results = []
            for subtask in task_tree.get("subtasks", []):
                task = progress.add_task(f"执行: {subtask['description']}", total=None)

                code = self.code_generator.generate_code(
                    subtask["description"],
                    subtask.get("language", "python"),
                )

                reflection = self.reflection_engine.evaluate_execution(
                    code,
                    subtask,
                )

                approved = reflection.get("approved", True)
                quality_score = reflection.get("quality_score", 0.8)

                if self.soul_meta.get("traits"):
                    decision_options = [
                        {"text": "接受代码", "risk": "low", "quality": quality_score},
                        {"text": "重新生成", "risk": "medium", "quality": 0.5},
                    ]
                    decision = self._make_proxy_decision(
                        f"代码质量评分: {quality_score:.2f}，应该接受还是重新生成？",
                        decision_options,
                    )
                    approved = decision.get("text") == "接受代码"

                if approved:
                    file_result = self.file_operations.create_file(
                        subtask.get("file_path", "output.py"),
                        code,
                    )
                    results.append({
                        "subtask": subtask,
                        "code": code,
                        "reflection": reflection,
                        "file_result": file_result,
                    })
                else:
                    console.print(f"[yellow]代理决策: 跳过低质量代码[/yellow]")

                progress.remove_task(task)

            self.execution_logger.log_execution(goal, task_tree, results)

        console.print("\n[green]✓ 执行完成[/green]")
        return {
            "status": "success",
            "goal": goal,
            "task_tree": task_tree,
            "results": results,
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
