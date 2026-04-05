"""
Agent base classes and interfaces for the dual-agent architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Types of messages exchanged between agents."""
    
    TASK = "task"
    RESULT = "result"
    QUESTION = "question"
    ANSWER = "answer"
    OPTIONS = "options"
    DECISION = "decision"
    ERROR = "error"
    STATUS = "status"


class AgentState(Enum):
    """States for agent lifecycle."""
    
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class Message:
    """Message structure for agent communication."""
    
    message_type: MessageType
    sender: str
    receiver: str
    data: dict[str, Any]
    message_id: str = field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_type": self.message_type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "data": self.data,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """Create message from dictionary."""
        return cls(
            message_type=MessageType(data["message_type"]),
            sender=data["sender"],
            receiver=data["receiver"],
            data=data["data"],
            message_id=data.get("message_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Task:
    """Task structure for worker execution."""
    
    task_id: str
    description: str
    constraints: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "constraints": self.constraints,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class Result:
    """Result structure for worker output."""
    
    task_id: str
    output_type: str
    data: dict[str, Any]
    quality_score: float = 0.0
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "task_id": self.task_id,
            "output_type": self.output_type,
            "data": self.data,
            "quality_score": self.quality_score,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.message_history: list[Message] = []
        
    @abstractmethod
    def process_message(self, message: Message) -> Message | None:
        """Process an incoming message and optionally return a response."""
        pass
    
    @abstractmethod
    def execute(self, task: Task) -> Result:
        """Execute a task and return the result."""
        pass
    
    def send_message(self, receiver: str, message_type: MessageType, data: dict[str, Any]) -> Message:
        """Send a message to another agent."""
        message = Message(
            message_type=message_type,
            sender=self.agent_id,
            receiver=receiver,
            data=data,
        )
        self.message_history.append(message)
        return message
    
    def receive_message(self, message: Message) -> None:
        """Receive a message from another agent."""
        self.message_history.append(message)
    
    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state
    
    def set_state(self, state: AgentState) -> None:
        """Set agent state."""
        self.state = state
    
    def get_message_history(self, limit: int | None = None) -> list[Message]:
        """Get message history."""
        if limit is None:
            return self.message_history
        return self.message_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear message history."""
        self.message_history.clear()
