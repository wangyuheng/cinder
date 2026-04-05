"""
Performance monitoring and metrics collection.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent execution."""
    
    execution_id: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    
    llm_calls: int = 0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    llm_total_tokens: int = 0
    
    decision_loops: int = 0
    worker_iterations: int = 0
    
    context_size_bytes: int = 0
    context_entries: int = 0
    
    quality_score: float = 0.0
    
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "llm_calls": self.llm_calls,
            "llm_input_tokens": self.llm_input_tokens,
            "llm_output_tokens": self.llm_output_tokens,
            "llm_total_tokens": self.llm_total_tokens,
            "decision_loops": self.decision_loops,
            "worker_iterations": self.worker_iterations,
            "context_size_bytes": self.context_size_bytes,
            "context_entries": self.context_entries,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
        }


class PerformanceMonitor:
    """Monitor and collect performance metrics."""
    
    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self.current_execution: PerformanceMetrics | None = None
    
    def start_execution(self, execution_id: str) -> None:
        """Start monitoring an execution."""
        self.current_execution = PerformanceMetrics(
            execution_id=execution_id,
            start_time=datetime.now(),
        )
    
    def record_llm_call(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Record an LLM call."""
        if self.current_execution:
            self.current_execution.llm_calls += 1
            self.current_execution.llm_input_tokens += input_tokens
            self.current_execution.llm_output_tokens += output_tokens
            self.current_execution.llm_total_tokens += input_tokens + output_tokens
    
    def record_decision_loop(self) -> None:
        """Record a decision loop iteration."""
        if self.current_execution:
            self.current_execution.decision_loops += 1
    
    def record_worker_iteration(self) -> None:
        """Record a worker iteration."""
        if self.current_execution:
            self.current_execution.worker_iterations += 1
    
    def record_context_metrics(
        self,
        size_bytes: int,
        entries: int,
    ) -> None:
        """Record context metrics."""
        if self.current_execution:
            self.current_execution.context_size_bytes = size_bytes
            self.current_execution.context_entries = entries
    
    def record_quality_score(self, score: float) -> None:
        """Record final quality score."""
        if self.current_execution:
            self.current_execution.quality_score = score
    
    def end_execution(self) -> PerformanceMetrics | None:
        """End monitoring and return metrics."""
        if self.current_execution:
            self.current_execution.end_time = datetime.now()
            self.current_execution.duration_seconds = (
                self.current_execution.end_time - self.current_execution.start_time
            ).total_seconds()
            
            self.metrics.append(self.current_execution)
            
            result = self.current_execution
            self.current_execution = None
            return result
        
        return None
    
    def get_statistics(self) -> dict[str, Any]:
        """Get aggregate statistics."""
        if not self.metrics:
            return {
                "total_executions": 0,
                "avg_duration": 0,
                "avg_llm_calls": 0,
                "avg_quality": 0,
            }
        
        total = len(self.metrics)
        
        return {
            "total_executions": total,
            "avg_duration": sum(m.duration_seconds for m in self.metrics) / total,
            "avg_llm_calls": sum(m.llm_calls for m in self.metrics) / total,
            "avg_llm_tokens": sum(m.llm_total_tokens for m in self.metrics) / total,
            "avg_decision_loops": sum(m.decision_loops for m in self.metrics) / total,
            "avg_worker_iterations": sum(m.worker_iterations for m in self.metrics) / total,
            "avg_quality": sum(m.quality_score for m in self.metrics) / total,
            "total_llm_tokens": sum(m.llm_total_tokens for m in self.metrics),
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to JSON file."""
        with open(filepath, 'w') as f:
            json.dump([m.to_dict() for m in self.metrics], f, indent=2)
    
    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
