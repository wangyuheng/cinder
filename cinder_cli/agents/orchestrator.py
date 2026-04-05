"""
Agent orchestration system for managing agent communication and lifecycle.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, Future
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

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates communication and lifecycle between agents.
    """
    
    def __init__(
        self,
        max_concurrent_workers: int = 3,
        message_timeout_seconds: int = 300,
        enable_message_logging: bool = True,
    ):
        self.agents: dict[str, BaseAgent] = {}
        self.message_queue: list[Message] = []
        self.message_log: list[dict[str, Any]] = []
        
        self.max_concurrent_workers = max_concurrent_workers
        self.message_timeout = message_timeout_seconds
        self.enable_message_logging = enable_message_logging
        
        self.thread_pool = ThreadPoolExecutor(max_workers=max_concurrent_workers)
        self.active_tasks: dict[str, Future] = {}
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} (type: {agent.agent_type})")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the orchestrator."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False
    
    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        data: dict[str, Any],
    ) -> Message:
        """Send a message from one agent to another."""
        if sender_id not in self.agents:
            raise ValueError(f"Unknown sender: {sender_id}")
        if receiver_id not in self.agents:
            raise ValueError(f"Unknown receiver: {receiver_id}")
        
        sender = self.agents[sender_id]
        receiver = self.agents[receiver_id]
        
        message = sender.send_message(receiver_id, message_type, data)
        receiver.receive_message(message)
        
        if self.enable_message_logging:
            self._log_message(message)
        
        logger.debug(f"Message sent: {sender_id} -> {receiver_id} ({message_type.value})")
        return message
    
    def broadcast_message(
        self,
        sender_id: str,
        message_type: MessageType,
        data: dict[str, Any],
        exclude: list[str] | None = None,
    ) -> list[Message]:
        """Broadcast a message to all agents except excluded ones."""
        exclude = exclude or []
        messages = []
        
        for agent_id in self.agents:
            if agent_id != sender_id and agent_id not in exclude:
                message = self.send_message(sender_id, agent_id, message_type, data)
                messages.append(message)
        
        return messages
    
    def delegate_task(
        self,
        delegator_id: str,
        worker_id: str,
        task: Task,
    ) -> Future:
        """Delegate a task to a worker agent asynchronously."""
        if worker_id not in self.agents:
            raise ValueError(f"Unknown worker: {worker_id}")
        
        worker = self.agents[worker_id]
        worker.set_state(AgentState.RUNNING)
        
        future = self.thread_pool.submit(self._execute_task, worker, task)
        self.active_tasks[task.task_id] = future
        
        logger.info(f"Task delegated: {delegator_id} -> {worker_id} (task: {task.task_id})")
        return future
    
    def _execute_task(self, worker: BaseAgent, task: Task) -> Result:
        """Execute a task and return the result."""
        try:
            result = worker.execute(task)
            worker.set_state(AgentState.COMPLETE)
            logger.info(f"Task completed: {task.task_id}")
            return result
        except Exception as e:
            worker.set_state(AgentState.ERROR)
            logger.error(f"Task failed: {task.task_id} - {e}")
            raise
    
    def get_task_result(self, task_id: str, timeout: float | None = None) -> Result:
        """Get the result of a delegated task."""
        if task_id not in self.active_tasks:
            raise ValueError(f"Unknown task: {task_id}")
        
        future = self.active_tasks[task_id]
        timeout = timeout or self.message_timeout
        
        return future.result(timeout=timeout)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id not in self.active_tasks:
            return False
        
        future = self.active_tasks[task_id]
        cancelled = future.cancel()
        
        if cancelled:
            logger.info(f"Task cancelled: {task_id}")
        
        return cancelled
    
    def get_agent_state(self, agent_id: str) -> AgentState | None:
        """Get the current state of an agent."""
        if agent_id not in self.agents:
            return None
        return self.agents[agent_id].get_state()
    
    def get_all_agent_states(self) -> dict[str, AgentState]:
        """Get the states of all agents."""
        return {
            agent_id: agent.get_state()
            for agent_id, agent in self.agents.items()
        }
    
    def _log_message(self, message: Message) -> None:
        """Log a message for debugging and auditing."""
        log_entry = {
            "message_id": message.message_id,
            "type": message.message_type.value,
            "sender": message.sender,
            "receiver": message.receiver,
            "timestamp": message.timestamp.isoformat(),
            "data_size": len(str(message.data)),
        }
        self.message_log.append(log_entry)
    
    def get_message_log(
        self,
        agent_id: str | None = None,
        message_type: MessageType | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get message log with optional filtering."""
        logs = self.message_log
        
        if agent_id is not None:
            logs = [
                log for log in logs
                if log["sender"] == agent_id or log["receiver"] == agent_id
            ]
        
        if message_type is not None:
            logs = [
                log for log in logs
                if log["type"] == message_type.value
            ]
        
        return logs[-limit:]
    
    def clear_message_log(self) -> None:
        """Clear the message log."""
        self.message_log.clear()
        logger.info("Message log cleared")
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the orchestrator and all agents."""
        logger.info("Shutting down orchestrator")
        
        for agent_id, agent in self.agents.items():
            agent.set_state(AgentState.IDLE)
            logger.debug(f"Agent stopped: {agent_id}")
        
        self.thread_pool.shutdown(wait=wait)
        self.agents.clear()
        self.active_tasks.clear()
    
    def get_statistics(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "message_log_size": len(self.message_log),
            "max_concurrent_workers": self.max_concurrent_workers,
            "agent_states": {
                agent_id: state.value
                for agent_id, state in self.get_all_agent_states().items()
            },
        }
