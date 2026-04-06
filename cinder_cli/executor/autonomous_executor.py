"""
Autonomous Executor - Main coordinator for task execution.
"""

from __future__ import annotations

import time
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
from cinder_cli.executor.progress_tracker import ProgressTracker, ExecutionPhase
from cinder_cli.executor.progress_broadcaster import ProgressBroadcaster
from cinder_cli.executor.time_recorder import TimeRecorder
from cinder_cli.executor.speed_calculator import SpeedCalculator
from cinder_cli.executor.estimation_engine import EstimationEngine
from cinder_cli.executor.progress_snapshot import ProgressSnapshot
from cinder_cli.executor.token_tracker import TokenTracker
from cinder_cli.executor.ollama_health_checker import OllamaHealthChecker
from cinder_cli.tracing import AgentTracer, LLMTracer, PhoenixTracer, TracingConfig
from cinder_cli.agents.decision_agent import DecisionAgent
from cinder_cli.agents.context_manager import ContextManager
from cinder_cli.agents.base import Task

console = Console()


class AutonomousExecutor:
    """Main coordinator for autonomous task execution."""

    def __init__(self, config: Config):
        self.config = config
        self.token_tracker = TokenTracker()
        
        self.tracing_config = TracingConfig.from_dict(config.to_dict())
        self.phoenix_tracer = PhoenixTracer.initialize(self.tracing_config)
        self.llm_tracer = LLMTracer(self.phoenix_tracer)
        self.agent_tracer = AgentTracer(self.phoenix_tracer)
        
        self.task_planner = TaskPlanner(config, self.token_tracker, self.llm_tracer)
        self.code_generator = CodeGenerator(config, self.token_tracker, self.llm_tracer)
        self.reflection_engine = ReflectionEngine(config, self.llm_tracer)
        self.file_operations = FileOperations(config)
        self.execution_logger = ExecutionLogger(config)
        self.decision_db = DecisionDatabase(config.database_path)
        self.soul_meta = self._load_soul_meta()
        
        self.progress_tracker = ProgressTracker()
        self.progress_broadcaster = ProgressBroadcaster()
        self.time_recorder = TimeRecorder()
        self.speed_calculator = SpeedCalculator()
        self.estimation_engine = EstimationEngine()
        
        self.ollama_base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.health_checker = OllamaHealthChecker(self.ollama_base_url)
        
        context_db_path = config.database_path.parent / "context.db"
        self.context_manager = ContextManager(
            db_path=context_db_path,
            user_id=config.get("user_id", "default"),
            project_id=config.get("project_id", "default"),
        )
        
        self.decision_agent = DecisionAgent(
            agent_id="main_decision_agent",
            config=config,
            soul_meta=self.soul_meta,
            context_manager=self.context_manager,
        )
        
        self._execution_id: int | None = None
        self._progress_enabled = config.get("progress_tracking", True)

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

        if not result or result.get("decision") is None:
            return options[0] if options else {}

        decision_id = self.decision_db.insert_decision(
            context={"description": context},
            soul_rules={"traits": self.soul_meta.get("traits", {})},
            decision=result.get("decision", {}),
            confidence=result.get("confidence", 0.5),
            requires_human=result.get("requires_human", False),
        )

        console.print(f"[dim]决策 #{decision_id}: 置信度 {result.get('confidence', 0.5):.2f}[/dim]")

        decision = result.get("decision")
        return decision if decision is not None else (options[0] if options else {})

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
        
        project_name = self.task_planner.infer_project_name(goal, constraints)
        project_dir = self.file_operations.working_dir / project_name
        
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[dim]✓ 创建项目目录: {project_dir}[/dim]")
        else:
            console.print(f"[dim]✓ 使用现有项目目录: {project_dir}[/dim]")
        
        self.file_operations = FileOperations(self.config, project_dir)

        with self.agent_tracer.trace_agent_execution(
            agent_id="autonomous_executor",
            agent_role="coordinator",
            goal=goal,
            mode=mode,
        ):
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
        from cinder_cli.cli_responsive_progress import ResponsiveProgressDisplay
        
        model_name = self.config.get("model", "qwen3.5:0.8b")
        health_status = self.health_checker.full_health_check(model_name)
        
        if not health_status["healthy"]:
            console.print(f"\n[bold red]✗ Ollama 健康检查失败[/bold red]")
            
            connection = health_status.get("connection", {})
            if connection:
                console.print(f"[red]{connection.get('message', 'Unknown error')}[/red]")
            
            model_info = health_status.get("model")
            if model_info:
                console.print(f"[red]{model_info.get('message', '')}[/red]")
            
            console.print(f"\n[yellow]建议: {health_status['recommendation']}[/yellow]")
            return {
                "status": "error",
                "goal": goal,
                "error": "Ollama health check failed",
                "health_status": health_status,
            }
        
        console.print(f"[dim]✓ Ollama 服务正常 ({model_name})[/dim]")
        
        execution_flow = {
            "goal": goal,
            "phases": [],
            "status": "in_progress",
        }

        try:
            self.time_recorder.start_execution()
            self.speed_calculator.start()
            self.token_tracker.start()
            
            stats = self.execution_logger.get_execution_statistics()
            self.estimation_engine.set_historical_stats(stats)
            
            progress_display = ResponsiveProgressDisplay(console)
            progress_display.start("Initializing...")
            
            def update_progress_with_tokens(input_tokens: int, output_tokens: int) -> None:
                """Callback to update progress display when tokens change."""
                try:
                    if progress_display._progress and progress_display._task_id is not None:
                        elapsed = time.time() - self.token_tracker._start_time if self.token_tracker._start_time else 1
                        token_speed = (input_tokens + output_tokens) / elapsed if elapsed > 0 else 0
                        
                        progress_display._progress.update(
                            progress_display._task_id,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            token_speed=token_speed
                        )
                        progress_display._progress.refresh()
                except Exception as e:
                    pass
            
            self.token_tracker.add_callback(update_progress_with_tokens)
            
            progress_display.update(
                10,
                "PHASE 1: PLAN - Understanding goal...",
                input_tokens=self.token_tracker.get_input_tokens(),
                output_tokens=self.token_tracker.get_output_tokens(),
                token_speed=self.token_tracker.get_tokens_per_second()
            )
            self.time_recorder.start_phase("plan")
            self.progress_tracker.start_phase(ExecutionPhase.PLAN)
            
            plan_result = self._execute_plan_phase(goal, constraints, None, None)
            execution_flow["phases"].append(plan_result)
            
            self.time_recorder.end_phase("plan")
            self.progress_tracker.complete_phase(ExecutionPhase.PLAN)
            
            if not plan_result.get("success", False):
                progress_display.stop("Plan phase failed")
                return self._create_failure_result(goal, "Plan phase failed", execution_flow)
            
            tasks_count = len(plan_result["plan"].get("subtasks", []))
            self.progress_tracker.set_tasks_total(tasks_count)
            estimate, confidence = self.estimation_engine.estimate_initial(tasks_count)
            
            progress_display.display_phase_summary(
                "PLAN",
                self.time_recorder.get_phase_timestamps().get("plan", {}).get("duration", 0),
                tasks_count,
                plan_result.get("quality_score", 0)
            )
            
            progress_display.update(
                25,
                f"PHASE 2: GENERATION - Creating {tasks_count} tasks...",
                input_tokens=self.token_tracker.get_input_tokens(),
                output_tokens=self.token_tracker.get_output_tokens(),
                token_speed=self.token_tracker.get_tokens_per_second()
            )
            self.time_recorder.start_phase("generation")
            self.progress_tracker.start_phase(ExecutionPhase.GENERATION)
            
            generation_results = self._execute_generation_phase_with_progress(
                plan_result["plan"], progress_display
            )
            execution_flow["phases"].extend(generation_results)
            
            self.time_recorder.end_phase("generation")
            self.progress_tracker.complete_phase(ExecutionPhase.GENERATION)
            
            progress_display.display_phase_summary(
                "GENERATION",
                self.time_recorder.get_phase_timestamps().get("generation", {}).get("duration", 0),
                len(generation_results)
            )
            
            progress_display.update(
                60,
                "PHASE 3: EVALUATION - Reviewing code...",
                input_tokens=self.token_tracker.get_input_tokens(),
                output_tokens=self.token_tracker.get_output_tokens(),
                token_speed=self.token_tracker.get_tokens_per_second()
            )
            self.time_recorder.start_phase("evaluation")
            self.progress_tracker.start_phase(ExecutionPhase.EVALUATION)
            
            evaluation_result = self._execute_evaluation_phase(generation_results, None, None)
            execution_flow["phases"].append(evaluation_result)
            
            self.time_recorder.end_phase("evaluation")
            self.progress_tracker.complete_phase(ExecutionPhase.EVALUATION)
            
            if not evaluation_result.get("all_approved", False):
                progress_display.stop("Evaluation phase failed")
                return self._create_failure_result(goal, "Evaluation phase failed", execution_flow)
            
            progress_display.display_phase_summary(
                "EVALUATION",
                self.time_recorder.get_phase_timestamps().get("evaluation", {}).get("duration", 0),
                len(evaluation_result.get("evaluations", []))
            )
            
            progress_display.update(
                85,
                "PHASE 4: DECISION - Making decisions...",
                input_tokens=self.token_tracker.get_input_tokens(),
                output_tokens=self.token_tracker.get_output_tokens(),
                token_speed=self.token_tracker.get_tokens_per_second()
            )
            self.time_recorder.start_phase("decision")
            self.progress_tracker.start_phase(ExecutionPhase.DECISION)
            
            decision_result = self._execute_decision_phase(evaluation_result, generation_results, None, None)
            execution_flow["phases"].append(decision_result)
            
            self.time_recorder.end_phase("decision")
            self.progress_tracker.complete_phase(ExecutionPhase.DECISION)
            
            progress_display.display_phase_summary(
                "DECISION",
                self.time_recorder.get_phase_timestamps().get("decision", {}).get("duration", 0)
            )
            
            progress_display.update(
                95,
                "Creating files...",
                input_tokens=self.token_tracker.get_input_tokens(),
                output_tokens=self.token_tracker.get_output_tokens(),
                token_speed=self.token_tracker.get_tokens_per_second()
            )
            execution_result = self._execute_files_creation(decision_result, None)
            
            self.time_recorder.end_execution()
            progress_display.stop("Execution complete!")
            
            console.print()
            
            execution_flow["status"] = "success"
            
            speed_metrics = self.speed_calculator.get_speed_metrics()
            phase_timestamps = self.time_recorder.get_phase_timestamps()
            token_metrics = self.token_tracker.get_metrics()
            
            return {
                "status": "success",
                "goal": goal,
                "execution_flow": execution_flow,
                "results": execution_result,
                "phase_timestamps": phase_timestamps,
                "speed_metrics": speed_metrics,
                "token_metrics": token_metrics,
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
        progress: Progress | None,
        task: Any | None,
    ) -> dict[str, Any]:
        """Execute Plan phase with validation."""
        with self.agent_tracer.trace_phase(
            phase_name="plan",
            parent_task_id="autonomous_executor",
        ):
            if progress and task is not None:
                progress.update(task, description="[bold blue]PHASE 1: PLAN - Understanding goal...[/bold blue]")

            plan = self.task_planner.decompose_goal_with_validation(
                goal,
                constraints,
                max_retries=2,
                quality_threshold=0.7,
            )

            validation = plan.get("validation", {})
            quality_score = validation.get("quality_score", 0)

            if progress and task is not None:
                progress.update(task, description=f"[bold blue]PHASE 1: PLAN - Quality: {quality_score:.2f}[/bold blue]")

            if quality_score < 0.7:
                console.print(f"[yellow]⚠ Plan quality low: {quality_score:.2f}[/yellow]")
                if validation.get("issues"):
                    for issue in validation["issues"]:
                        console.print(f"  - {issue}")
                
                decision_result = self._handle_low_quality_plan(
                    goal, constraints, plan, validation
                )
                
                if decision_result.get("action") == "proceed":
                    plan = decision_result.get("plan", plan)
                    quality_score = decision_result.get("quality_score", quality_score)
                elif decision_result.get("action") == "abort":
                    return {
                        "phase": "plan",
                        "success": False,
                        "plan": plan,
                        "quality_score": quality_score,
                        "attempts": plan.get("attempts", 1),
                        "decision": decision_result,
                    }

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
        progress: Progress | None,
        task: Any | None,
    ) -> list[dict[str, Any]]:
        """Execute Generation phase with iterations."""
        results = []
        subtasks = plan.get("subtasks", [])

        with self.agent_tracer.trace_phase(
            phase_name="generation",
            parent_task_id="autonomous_executor",
        ):
            for i, subtask in enumerate(subtasks, 1):
                if progress and task is not None:
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

    def _execute_generation_phase_with_progress(
        self,
        plan: dict[str, Any],
        progress_display: Any,
    ) -> list[dict[str, Any]]:
        """Execute Generation phase with progress display."""
        results = []
        subtasks = plan.get("subtasks", [])
        
        with self.agent_tracer.trace_phase(
            phase_name="generation",
            parent_task_id="autonomous_executor",
        ):
            for i, subtask in enumerate(subtasks, 1):
                progress_display.update(
                    25 + (i / len(subtasks)) * 30,
                    f"PHASE 2: GENERATION - Task {i}/{len(subtasks)}",
                    input_tokens=self.token_tracker.get_input_tokens(),
                    output_tokens=self.token_tracker.get_output_tokens(),
                    token_speed=self.token_tracker.get_tokens_per_second()
                )
                
                self.time_recorder.start_task(f"task_{i}", subtask["description"])
                
                generation_result = self.code_generator.generate_with_iterations(
                    subtask["description"],
                    subtask.get("language", "python"),
                    subtask.get("constraints"),
                    max_iterations=3,
                    quality_threshold=0.8,
                )
                
                self.time_recorder.end_task(f"task_{i}")
                self.speed_calculator.record_task_completed()
                
                results.append({
                    "phase": "generation",
                    "subtask_id": subtask.get("id"),
                    "subtask": subtask,
                    "code": generation_result.get("code"),
                    "iterations": generation_result.get("iterations", 1),
                    "quality_score": generation_result.get("final_score", 0),
                })
                
                console.print(f"[dim]Task {i}: {generation_result.get('iterations', 1)} iterations, quality={generation_result.get('final_score', 0):.2f}[/dim]")
        
        return results

    def _execute_evaluation_phase(
        self,
        generation_results: list[dict[str, Any]],
        progress: Progress | None,
        task: Any | None,
    ) -> dict[str, Any]:
        """Execute Evaluation phase with comprehensive assessment."""
        with self.agent_tracer.trace_phase(
            phase_name="evaluation",
            parent_task_id="autonomous_executor",
        ):
            if progress and task is not None:
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
        generation_results: list[dict[str, Any]] | None,
        progress: Progress | None,
        task: Any | None,
    ) -> dict[str, Any]:
        """Execute Decision phase based on Soul profile."""
        if progress and task is not None:
            progress.update(task, description="[bold magenta]PHASE 4: DECISION - Making decisions...[/bold magenta]")

        decisions = []
        force_file_creation = self.config.get("force_file_creation", False)

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
                    "accepted": decision.get("text") == "接受代码" or force_file_creation,
                })
            else:
                decisions.append({
                    "subtask_id": eval_item.get("subtask_id"),
                    "decision": {"text": "接受代码", "quality": quality_score},
                    "accepted": evaluation.get("approved", False) or force_file_creation,
                })

        accepted_count = sum(1 for d in decisions if d.get("accepted", False))

        console.print(f"[dim]Decision phase complete: {accepted_count}/{len(decisions)} accepted[/dim]")

        return {
            "phase": "decision",
            "decisions": decisions,
            "accepted_count": accepted_count,
            "generation_results": generation_results,
        }

    def _execute_files_creation(
        self,
        decision_result: dict[str, Any],
        progress: Progress,
    ) -> list[dict[str, Any]]:
        """Execute file creation based on decisions."""
        results = []
        force_file_creation = self.config.get("force_file_creation", False)

        if force_file_creation:
            console.print("[dim]强制文件生成模式已启用[/dim]")

        for decision in decision_result.get("decisions", []):
            should_create = decision.get("accepted", False) or force_file_creation
            
            if should_create:
                subtask_id = decision.get("subtask_id")

                gen_result = next(
                    (r for r in decision_result.get("generation_results", []) if r.get("subtask_id") == subtask_id),
                    None
                )

                if gen_result:
                    file_path = gen_result.get("subtask", {}).get("file_path", "output.py")
                    code = gen_result.get("code", "")
                    
                    if code and code.strip():
                        file_result = self.file_operations.create_file(
                            file_path,
                            code,
                        )

                        results.append({
                            "subtask_id": subtask_id,
                            "file_result": file_result,
                            "code": code,
                            "file_path": file_path,
                        })
                        console.print(f"[dim]创建文件: {file_path}[/dim]")
                    else:
                        console.print(f"[yellow]跳过空代码文件: {file_path}[/yellow]")

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
