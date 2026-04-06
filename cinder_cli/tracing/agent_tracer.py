"""
Agent Tracer - Traces Agent execution with task aggregation.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator, Optional

from opentelemetry import trace

from .phoenix_tracer import PhoenixTracer


@dataclass
class TaskRecord:
    """Record of a single task execution."""
    
    task_id: str
    goal: str
    status: str = "running"
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseRecord:
    """Record of a single phase execution."""
    
    phase_id: str
    phase_name: str
    status: str = "running"
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentTracer:
    """Tracer for Agent execution with task aggregation."""
    
    def __init__(self, phoenix_tracer: Optional[PhoenixTracer] = None):
        """
        Initialize Agent Tracer.
        
        Args:
            phoenix_tracer: PhoenixTracer instance for OpenTelemetry integration
        """
        self.phoenix_tracer = phoenix_tracer
        self._task_records: list[TaskRecord] = []
        self._phase_records: list[PhaseRecord] = []
    
    @contextmanager
    def trace_agent_execution(
        self,
        agent_id: str,
        agent_role: str,
        goal: str,
        mode: str = "auto",
        **metadata: Any,
    ) -> Iterator[TaskRecord]:
        """
        Trace an agent execution with OpenTelemetry.
        
        This is a convenience method that wraps trace_task for agent execution.
        
        Args:
            agent_id: Agent identifier
            agent_role: Agent role (e.g., "coordinator", "worker")
            goal: Goal description
            mode: Execution mode (e.g., "auto", "interactive", "dry-run")
            **metadata: Additional metadata
            
        Yields:
            TaskRecord instance
        """
        task_id = f"agent_{agent_id}_{int(time.time() * 1000)}"
        
        with self.trace_task(
            goal=goal,
            task_id=task_id,
            agent_id=agent_id,
            agent_role=agent_role,
            mode=mode,
            **metadata,
        ) as record:
            yield record
    
    @contextmanager
    def trace_task(
        self,
        goal: str,
        task_id: Optional[str] = None,
        **metadata: Any,
    ) -> Iterator[TaskRecord]:
        """
        Trace a task execution with OpenTelemetry.
        
        Args:
            goal: Task goal description
            task_id: Task ID (auto-generated if not provided)
            **metadata: Additional metadata
            
        Yields:
            TaskRecord instance
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"
        
        start_time = time.time()
        
        record = TaskRecord(
            task_id=task_id,
            goal=goal,
            metadata=metadata,
        )
        
        if self.phoenix_tracer and self.phoenix_tracer.is_enabled():
            span_name = f"agent.task.{task_id}"
            
            attributes = {
                "openinference.span.kind": "AGENT",
                "agent.task.id": task_id,
                "agent.goal": goal,
            }
            
            for key, value in metadata.items():
                if value is not None:
                    attributes[f"agent.{key}"] = value
            
            with self.phoenix_tracer.tracer.start_as_current_span(
                span_name,
                kind=trace.SpanKind.INTERNAL,
                attributes=attributes,
            ) as span:
                try:
                    yield record
                    record.duration_ms = (time.time() - start_time) * 1000
                    record.end_time = time.time()
                    record.status = "completed"
                    
                    span.set_attribute("agent.status", "completed")
                    span.set_attribute("agent.duration_ms", record.duration_ms)
                    
                except Exception as e:
                    record.status = "failed"
                    record.error = str(e)
                    span.set_attribute("agent.status", "failed")
                    span.set_attribute("agent.error", str(e))
                    span.record_exception(e)
                    raise
        else:
            yield record
            record.duration_ms = (time.time() - start_time) * 1000
            record.end_time = time.time()
            record.status = "completed"
        
        self._task_records.append(record)
    
    @contextmanager
    def trace_phase(
        self,
        phase_name: str,
        phase_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        **metadata: Any,
    ) -> Iterator[PhaseRecord]:
        """
        Trace a phase execution with OpenTelemetry.
        
        Args:
            phase_name: Phase name (e.g., goal_understanding, task_decomposition)
            phase_id: Phase ID (auto-generated if not provided)
            parent_task_id: Parent task ID
            **metadata: Additional metadata
            
        Yields:
            PhaseRecord instance
        """
        if phase_id is None:
            phase_id = f"phase_{int(time.time() * 1000)}"
        
        start_time = time.time()
        
        record = PhaseRecord(
            phase_id=phase_id,
            phase_name=phase_name,
            metadata=metadata,
        )
        
        if self.phoenix_tracer and self.phoenix_tracer.is_enabled():
            span_name = f"agent.phase.{phase_name}"
            
            attributes = {
                "openinference.span.kind": "CHAIN",
                "agent.phase.id": phase_id,
                "agent.phase.name": phase_name,
            }
            
            if parent_task_id:
                attributes["agent.task.id"] = parent_task_id
            
            for key, value in metadata.items():
                if value is not None:
                    attributes[f"agent.{key}"] = value
            
            with self.phoenix_tracer.tracer.start_as_current_span(
                span_name,
                kind=trace.SpanKind.INTERNAL,
                attributes=attributes,
            ) as span:
                try:
                    yield record
                    record.duration_ms = (time.time() - start_time) * 1000
                    record.end_time = time.time()
                    record.status = "completed"
                    
                    span.set_attribute("agent.status", "completed")
                    span.set_attribute("agent.duration_ms", record.duration_ms)
                    
                except Exception as e:
                    record.status = "failed"
                    record.error = str(e)
                    span.set_attribute("agent.status", "failed")
                    span.set_attribute("agent.error", str(e))
                    span.record_exception(e)
                    raise
        else:
            yield record
            record.duration_ms = (time.time() - start_time) * 1000
            record.end_time = time.time()
            record.status = "completed"
        
        self._phase_records.append(record)
    
    def get_task_records(self) -> list[TaskRecord]:
        """
        Get all task records.
        
        Returns:
            List of TaskRecord instances
        """
        return self._task_records.copy()
    
    def get_phase_records(self) -> list[PhaseRecord]:
        """
        Get all phase records.
        
        Returns:
            List of PhaseRecord instances
        """
        return self._phase_records.copy()
    
    def clear_records(self) -> None:
        """Clear all records."""
        self._task_records.clear()
        self._phase_records.clear()
