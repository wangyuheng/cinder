"""
Worker Agent - Executes tasks without making decisions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from cinder_cli.agents.base import (
    AgentState,
    BaseAgent,
    Message,
    MessageType,
    Result,
    Task,
)
from cinder_cli.config import Config
from cinder_cli.executor.task_planner import TaskPlanner
from cinder_cli.executor.code_generator import CodeGenerator
from cinder_cli.executor.reflection_engine import ReflectionEngine
from cinder_cli.executor.token_tracker import TokenTracker


@dataclass
class WorkerOutput:
    """Output from worker execution."""
    
    output_type: str  # "code", "options", "report"
    data: dict[str, Any]
    quality_score: float = 0.0
    execution_time: float = 0.0
    iterations: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output_type": self.output_type,
            "data": self.data,
            "quality_score": self.quality_score,
            "execution_time": self.execution_time,
            "iterations": self.iterations,
            "metadata": self.metadata,
        }


class WorkerAgent(BaseAgent):
    """
    Worker agent that executes tasks without making decisions.
    
    Responsibilities:
    - Execute Plan → Generate → Evaluation flow
    - Return objective data (no decisions)
    - Support outputting options for decision-making
    - Report execution status
    """
    
    def __init__(
        self,
        agent_id: str,
        config: Config,
        max_iterations: int = 3,
    ):
        super().__init__(agent_id, "worker")
        
        self.config = config
        self.max_iterations = max_iterations
        
        self.token_tracker = TokenTracker()
        self.planner = TaskPlanner(config, self.token_tracker)
        self.generator = CodeGenerator(config, self.token_tracker)
        self.evaluator = ReflectionEngine(config)
        
        self.current_task: Task | None = None
        self.execution_history: list[WorkerOutput] = []
    
    def process_message(self, message: Message) -> Message | None:
        """Process incoming message."""
        if message.message_type == MessageType.TASK:
            task = Task(
                task_id=message.data.get("task_id", ""),
                description=message.data.get("description", ""),
                constraints=message.data.get("constraints", {}),
                priority=message.data.get("priority", 5),
                metadata=message.data.get("metadata", {}),
            )
            
            result = self.execute(task)
            
            return Message(
                message_type=MessageType.RESULT,
                sender=self.agent_id,
                receiver=message.sender,
                data=result.to_dict(),
            )
        
        return None
    
    def execute(self, task: Task) -> Result:
        """Execute a task and return the result."""
        start_time = time.time()
        self.current_task = task
        self.set_state(AgentState.RUNNING)
        
        try:
            output = self._execute_task(task)
            
            execution_time = time.time() - start_time
            
            result = Result(
                task_id=task.task_id,
                output_type=output.output_type,
                data=output.data,
                quality_score=output.quality_score,
                execution_time=execution_time,
                metadata=output.metadata,
            )
            
            self.execution_history.append(output)
            self.set_state(AgentState.COMPLETE)
            
            return result
            
        except Exception as e:
            self.set_state(AgentState.ERROR)
            
            return Result(
                task_id=task.task_id,
                output_type="error",
                data={"error": str(e)},
                quality_score=0.0,
                execution_time=time.time() - start_time,
            )
    
    def _execute_task(self, task: Task) -> WorkerOutput:
        """Execute the Plan → Generate → Evaluation flow."""
        
        plan = self._plan(task)
        
        if plan.get("type") == "options":
            return WorkerOutput(
                output_type="options",
                data={
                    "context": plan.get("context", ""),
                    "options": plan.get("options", []),
                },
                metadata={"phase": "plan"},
            )
        
        generation_result = self._generate(plan, task)
        
        if generation_result.get("type") == "options":
            return WorkerOutput(
                output_type="options",
                data={
                    "context": generation_result.get("context", ""),
                    "options": generation_result.get("options", []),
                },
                metadata={"phase": "generate"},
            )
        
        best_output = None
        best_score = 0.0
        iterations = 0
        
        for iteration in range(self.max_iterations):
            iterations = iteration + 1
            
            evaluation = self._evaluate(
                generation_result.get("code", ""),
                task,
                plan,
            )
            
            quality_score = evaluation.get("quality_score", 0.0)
            
            if quality_score > best_score:
                best_score = quality_score
                best_output = WorkerOutput(
                    output_type="code",
                    data={
                        "code": generation_result.get("code", ""),
                        "plan": plan,
                        "evaluation": evaluation,
                    },
                    quality_score=quality_score,
                    iterations=iterations,
                    metadata={
                        "phase": "complete",
                        "iteration": iteration + 1,
                    },
                )
            
            if quality_score >= 0.8:
                break
            
            if iteration < self.max_iterations - 1:
                generation_result = self._regenerate(
                    plan,
                    task,
                    generation_result.get("code", ""),
                    evaluation,
                )
        
        return best_output or WorkerOutput(
            output_type="code",
            data={"code": "", "plan": plan, "evaluation": {}},
            quality_score=0.0,
            iterations=iterations,
        )
    
    def _plan(self, task: Task) -> dict[str, Any]:
        """Plan phase - decompose task."""
        plan_result = self.planner.decompose_goal_with_validation(
            task.description,
            task.constraints,
            max_retries=2,
            quality_threshold=0.7,
        )
        
        return {
            "type": "tasks",
            "goal": plan_result.get("goal", ""),
            "subtasks": plan_result.get("subtasks", []),
            "quality_score": plan_result.get("validation", {}).get("quality_score", 0.0),
        }
    
    def _generate(
        self,
        plan: dict[str, Any],
        task: Task,
    ) -> dict[str, Any]:
        """Generate phase - create code."""
        subtasks = plan.get("subtasks", [])
        
        if not subtasks:
            return {
                "type": "code",
                "code": "",
            }
        
        code_parts = []
        
        for subtask in subtasks:
            generation_result = self.generator.generate_with_iterations(
                subtask.get("description", ""),
                subtask.get("language", "python"),
                subtask.get("constraints"),
                max_iterations=3,
                quality_threshold=0.8,
            )
            
            code_parts.append(generation_result.get("code", ""))
        
        return {
            "type": "code",
            "code": "\n\n".join(code_parts),
            "iterations": len(subtasks),
        }
    
    def _evaluate(
        self,
        code: str,
        task: Task,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate phase - assess code quality."""
        evaluation = self.evaluator.evaluate_execution(
            code,
            {"description": task.description, "plan": plan},
        )
        
        return {
            "quality_score": evaluation.get("quality_score", 0.0),
            "approved": evaluation.get("approved", False),
            "suggestions": evaluation.get("suggestions", []),
            "risks": evaluation.get("risks", []),
        }
    
    def _regenerate(
        self,
        plan: dict[str, Any],
        task: Task,
        previous_code: str,
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        """Regenerate code based on evaluation feedback."""
        feedback_prompt = f"""
Previous code:
{previous_code}

Evaluation feedback:
- Quality score: {evaluation.get('quality_score', 0.0)}
- Suggestions: {evaluation.get('suggestions', [])}
- Risks: {evaluation.get('risks', [])}

Please improve the code based on this feedback.
"""
        
        return self._generate(plan, task)
    
    def get_execution_history(self, limit: int | None = None) -> list[WorkerOutput]:
        """Get execution history."""
        if limit is None:
            return self.execution_history
        return self.execution_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
    
    def get_status(self) -> dict[str, Any]:
        """Get current worker status."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "execution_count": len(self.execution_history),
            "max_iterations": self.max_iterations,
        }
