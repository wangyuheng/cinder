"""
Refactored Autonomous Executor - Agent orchestrator with backward compatibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

from cinder_cli.config import Config
from cinder_cli.agents.decision_agent import DecisionAgent
from cinder_cli.agents.worker_agent import WorkerAgent
from cinder_cli.agents.orchestrator import AgentOrchestrator
from cinder_cli.agents.context_manager import ContextManager
from cinder_cli.agents.base import Task

console = Console()


class AutonomousExecutor:
    """
    Main coordinator for autonomous task execution.
    
    Refactored to use the dual-agent architecture while maintaining backward compatibility.
    """
    
    def __init__(self, config: Config, legacy_mode: bool = False):
        self.config = config
        self.legacy_mode = legacy_mode
        self.soul_meta = self._load_soul_meta()
        
        if legacy_mode:
            self._init_legacy_components()
        else:
            self._init_agent_components()
    
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
    
    def _init_legacy_components(self) -> None:
        """Initialize legacy components for backward compatibility."""
        from cinder_cli.executor.task_planner import TaskPlanner
        from cinder_cli.executor.code_generator import CodeGenerator
        from cinder_cli.executor.reflection_engine import ReflectionEngine
        from cinder_cli.executor.file_operations import FileOperations
        from cinder_cli.executor.execution_logger import ExecutionLogger
        from cinder_cli.database import DecisionDatabase
        from cinder_cli.executor.token_tracker import TokenTracker
        from cinder_cli.executor.progress_tracker import ProgressTracker
        from cinder_cli.executor.time_recorder import TimeRecorder
        from cinder_cli.executor.speed_calculator import SpeedCalculator
        from cinder_cli.executor.estimation_engine import EstimationEngine
        
        self.token_tracker = TokenTracker()
        self.task_planner = TaskPlanner(self.config, self.token_tracker)
        self.code_generator = CodeGenerator(self.config, self.token_tracker)
        self.reflection_engine = ReflectionEngine(self.config)
        self.file_operations = FileOperations(self.config)
        self.execution_logger = ExecutionLogger(self.config)
        self.decision_db = DecisionDatabase(self.config.database_path)
        
        self.progress_tracker = ProgressTracker()
        self.time_recorder = TimeRecorder()
        self.speed_calculator = SpeedCalculator()
        self.estimation_engine = EstimationEngine()
    
    def _init_agent_components(self) -> None:
        """Initialize agent-based components."""
        db_path = self.config.database_path.parent / "context.db"
        
        self.context_manager = ContextManager(
            db_path=db_path,
            user_id="default",
            project_id="default",
        )
        
        self.orchestrator = AgentOrchestrator(max_concurrent_workers=3)
        
        self.decision_agent = DecisionAgent(
            agent_id="decision_agent",
            config=self.config,
            soul_meta=self.soul_meta,
            context_manager=self.context_manager,
        )
        
        self.worker_agent = WorkerAgent(
            agent_id="worker_agent",
            config=self.config,
        )
        
        self.orchestrator.register_agent(self.decision_agent)
        self.orchestrator.register_agent(self.worker_agent)
    
    def execute(
        self,
        goal: str,
        mode: str = "auto",
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a goal autonomously.
        
        Args:
            goal: Natural language goal description
            mode: Execution mode ("auto" or "interactive")
            constraints: Optional constraints
        
        Returns:
            Execution result
        """
        if self.legacy_mode:
            return self._execute_legacy(goal, mode, constraints)
        else:
            return self._execute_with_agents(goal, mode, constraints)
    
    def _execute_legacy(
        self,
        goal: str,
        mode: str,
        constraints: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Execute using legacy flow (backward compatibility)."""
        console.print("[yellow]Using legacy execution mode[/yellow]")
        
        from cinder_cli.executor.autonomous_executor import AutonomousExecutor as LegacyExecutor
        
        legacy_executor = LegacyExecutor(self.config)
        return legacy_executor.execute(goal, mode, constraints)
    
    def _execute_with_agents(
        self,
        goal: str,
        mode: str,
        constraints: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Execute using new agent architecture."""
        console.print("[green]Using agent-based execution mode[/green]")
        
        task = Task(
            task_id=f"task_{goal[:20]}",
            description=goal,
            constraints=constraints or {},
            metadata={"mode": mode},
        )
        
        result = self.decision_agent.execute(task)
        
        return self._convert_result_format(result)
    
    def _convert_result_format(self, agent_result: dict[str, Any]) -> dict[str, Any]:
        """Convert agent result format to legacy format for compatibility."""
        return {
            "status": agent_result.get("status", "unknown"),
            "goal": agent_result.get("goal", ""),
            "execution_flow": {
                "phases": agent_result.get("decision_history", []),
            },
            "results": [agent_result.get("worker_result", {})],
            "decision": agent_result.get("decision", {}),
            "worker_result": agent_result.get("worker_result", {}),
            "metadata": {
                "architecture": "dual-agent",
                "decision_loops": agent_result.get("decision_loop_count", 0),
            },
        }
    
    def shutdown(self) -> None:
        """Shutdown the executor and cleanup resources."""
        if not self.legacy_mode:
            self.orchestrator.shutdown()
            self.context_manager.save()
    
    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        if self.legacy_mode:
            return {
                "mode": "legacy",
                "statistics": "not available in legacy mode",
            }
        
        return {
            "mode": "agent-based",
            "orchestrator": self.orchestrator.get_statistics(),
            "context": self.context_manager.get_statistics(),
            "decision_agent": self.decision_agent.get_statistics(),
        }
