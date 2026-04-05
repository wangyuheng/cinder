"""
Decision Agent - The brain of the system that makes decisions.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from cinder_cli.agents.base import (
    AgentState,
    BaseAgent,
    Message,
    MessageType,
    Result,
    Task,
)
from cinder_cli.agents.context_manager import ContextManager
from cinder_cli.agents.worker_agent import WorkerAgent
from cinder_cli.config import Config
from cinder_cli.proxy_decision import ProxyDecisionMaker

logger = logging.getLogger(__name__)


class DecisionState(Enum):
    """States for decision agent state machine."""
    
    UNDERSTAND = "understand"
    ANALYZE = "analyze"
    DECIDE = "decide"
    DELEGATE = "delegate"
    EVALUATE = "evaluate"
    COMPLETE = "complete"


@dataclass
class Decision:
    """A decision made by the decision agent."""
    
    decision_id: str
    decision_type: str  # "code_accept", "tech_choice", "architecture", etc.
    context: str
    selected_option: dict[str, Any]
    confidence: float
    reasoning: str
    soul_rules_applied: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "context": self.context,
            "selected_option": self.selected_option,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "soul_rules_applied": self.soul_rules_applied,
            "timestamp": self.timestamp.isoformat(),
        }


class DecisionAgent(BaseAgent):
    """
    Decision agent that acts as the brain of the system.
    
    Responsibilities:
    - Understand user intent
    - Make decisions based on Soul profile
    - Delegate tasks to Worker
    - Evaluate results
    - Interact with user
    """
    
    def __init__(
        self,
        agent_id: str,
        config: Config,
        soul_meta: dict[str, Any],
        context_manager: ContextManager,
        max_decision_loops: int = 10,
    ):
        super().__init__(agent_id, "decision")
        
        self.config = config
        self.soul_meta = soul_meta
        self.context_manager = context_manager
        self.max_decision_loops = max_decision_loops
        
        self.decision_maker = ProxyDecisionMaker(soul_meta)
        
        self.state_machine = DecisionState.UNDERSTAND
        self.current_goal: str | None = None
        self.decision_history: list[Decision] = []
        self.decision_loop_count = 0
        
        self.worker: WorkerAgent | None = None
    
    def set_worker(self, worker: WorkerAgent) -> None:
        """Set the worker agent to delegate tasks to."""
        self.worker = worker
    
    def process_message(self, message: Message) -> Message | None:
        """Process incoming message."""
        if message.message_type == MessageType.ANSWER:
            answer = message.data.get("answer")
            self.context_manager.set("user_answer", answer)
            return None
        
        return None
    
    def execute(self, task: Task) -> Result:
        """Execute the decision loop for a goal."""
        self.current_goal = task.description
        self.set_state(AgentState.RUNNING)
        self.decision_loop_count = 0
        
        start_time = time.time()
        
        try:
            result = self._run_decision_loop()
            
            execution_time = time.time() - start_time
            
            return Result(
                task_id=task.task_id,
                output_type="decision_result",
                data=result,
                execution_time=execution_time,
            )
            
        except Exception as e:
            logger.error(f"Decision loop failed: {e}")
            self.set_state(AgentState.ERROR)
            
            return Result(
                task_id=task.task_id,
                output_type="error",
                data={"error": str(e)},
                execution_time=time.time() - start_time,
            )
    
    def _run_decision_loop(self) -> dict[str, Any]:
        """Run the main decision loop."""
        
        while self.decision_loop_count < self.max_decision_loops:
            self.decision_loop_count += 1
            
            if self.state_machine == DecisionState.UNDERSTAND:
                self._understand_intent()
            
            elif self.state_machine == DecisionState.ANALYZE:
                self._analyze_situation()
            
            elif self.state_machine == DecisionState.DECIDE:
                decision = self._make_decision()
                
                if decision.decision_type == "delegate":
                    self.state_machine = DecisionState.DELEGATE
                elif decision.decision_type == "ask_user":
                    self._ask_user(decision.context)
                    self.state_machine = DecisionState.ANALYZE
                else:
                    self.state_machine = DecisionState.EVALUATE
            
            elif self.state_machine == DecisionState.DELEGATE:
                worker_result = self._delegate_to_worker()
                self.context_manager.set("worker_result", worker_result)
                self.state_machine = DecisionState.EVALUATE
            
            elif self.state_machine == DecisionState.EVALUATE:
                should_continue = self._evaluate_result()
                
                if should_continue:
                    self.state_machine = DecisionState.ANALYZE
                else:
                    self.state_machine = DecisionState.COMPLETE
            
            elif self.state_machine == DecisionState.COMPLETE:
                return self._build_final_result()
        
        logger.warning(f"Max decision loops reached: {self.max_decision_loops}")
        return self._build_final_result()
    
    def _understand_intent(self) -> None:
        """Understand user intent."""
        self.context_manager.set("goal", self.current_goal)
        
        understanding = {
            "goal": self.current_goal,
            "key_requirements": [],
            "decision_points": [],
        }
        
        self.context_manager.set("understanding", understanding)
        self.state_machine = DecisionState.ANALYZE
        
        logger.info(f"Understood intent: {self.current_goal}")
    
    def _analyze_situation(self) -> None:
        """Analyze current situation."""
        worker_result = self.context_manager.get("worker_result")
        
        if worker_result is None:
            self.state_machine = DecisionState.DECIDE
            return
        
        analysis = {
            "quality_score": worker_result.get("quality_score", 0.0),
            "needs_improvement": worker_result.get("quality_score", 0.0) < 0.8,
            "issues": [],
        }
        
        self.context_manager.set("analysis", analysis)
        self.state_machine = DecisionState.DECIDE
        
        logger.info(f"Analyzed situation: quality={analysis['quality_score']}")
    
    def _make_decision(self) -> Decision:
        """Make a decision."""
        understanding = self.context_manager.get("understanding", {})
        analysis = self.context_manager.get("analysis", {})
        worker_result = self.context_manager.get("worker_result")
        
        if worker_result is None:
            return self._create_decision(
                decision_type="delegate",
                context="Initial task delegation",
                selected_option={"action": "execute"},
            )
        
        quality_score = analysis.get("quality_score", 0.0)
        
        if quality_score >= 0.8:
            return self._create_decision(
                decision_type="accept",
                context=f"Quality score {quality_score:.2f} meets threshold",
                selected_option={"action": "accept"},
            )
        elif quality_score >= 0.6:
            return self._create_decision(
                decision_type="improve",
                context=f"Quality score {quality_score:.2f} needs improvement",
                selected_option={"action": "improve"},
            )
        else:
            return self._create_decision(
                decision_type="regenerate",
                context=f"Quality score {quality_score:.2f} too low",
                selected_option={"action": "regenerate"},
            )
    
    def _create_decision(
        self,
        decision_type: str,
        context: str,
        selected_option: dict[str, Any],
    ) -> Decision:
        """Create a decision object."""
        decision_id = f"decision_{len(self.decision_history) + 1}"
        
        decision = Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            context=context,
            selected_option=selected_option,
            confidence=0.8,
            reasoning=f"Based on Soul profile and context analysis",
        )
        
        self.decision_history.append(decision)
        
        logger.info(f"Decision made: {decision_type} (confidence: {decision.confidence:.2f})")
        
        return decision
    
    def _delegate_to_worker(self) -> dict[str, Any]:
        """Delegate task to worker agent."""
        if self.worker is None:
            raise ValueError("No worker agent set")
        
        goal = self.context_manager.get("goal", "")
        
        task = Task(
            task_id=f"task_{self.decision_loop_count}",
            description=goal,
        )
        
        result = self.worker.execute(task)
        
        logger.info(f"Worker completed task: {result.task_id}")
        
        return result.to_dict()
    
    def _evaluate_result(self) -> bool:
        """Evaluate worker result and decide if should continue."""
        analysis = self.context_manager.get("analysis", {})
        
        needs_improvement = analysis.get("needs_improvement", False)
        
        if needs_improvement and self.decision_loop_count < self.max_decision_loops:
            logger.info("Result needs improvement, continuing loop")
            return True
        
        return False
    
    def _ask_user(self, question: str) -> None:
        """Ask user a question."""
        logger.info(f"Asking user: {question}")
        
        self.context_manager.set("pending_question", question)
    
    def _build_final_result(self) -> dict[str, Any]:
        """Build final result."""
        worker_result = self.context_manager.get("worker_result", {})
        
        return {
            "status": "complete",
            "goal": self.current_goal,
            "worker_result": worker_result,
            "decision_history": [d.to_dict() for d in self.decision_history],
            "total_loops": self.decision_loop_count,
        }
    
    def get_decision_history(self) -> list[Decision]:
        """Get decision history."""
        return self.decision_history
    
    def get_current_state(self) -> DecisionState:
        """Get current state machine state."""
        return self.state_machine
    
    def explain_decision(self, decision_id: str) -> dict[str, Any] | None:
        """Explain a decision."""
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                return {
                    "decision": decision.to_dict(),
                    "soul_profile": self.soul_meta.get("traits", {}),
                    "context": decision.context,
                    "reasoning": decision.reasoning,
                }
        return None
