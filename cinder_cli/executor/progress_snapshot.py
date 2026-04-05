"""
Progress Snapshot - Captures intermediate execution state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class ProgressSnapshot:
    """Captures execution state at a point in time."""

    def __init__(
        self,
        current_phase: str,
        overall_progress: float,
        elapsed_time: float,
        tasks_completed: int,
        tasks_total: int,
        current_task: str = "",
        phase_progress: dict[str, float] | None = None,
        speed_metrics: dict[str, Any] | None = None,
        estimation_data: dict[str, Any] | None = None,
    ):
        self.timestamp = datetime.now().isoformat()
        self.current_phase = current_phase
        self.overall_progress = overall_progress
        self.elapsed_time = elapsed_time
        self.tasks_completed = tasks_completed
        self.tasks_total = tasks_total
        self.current_task = current_task
        self.phase_progress = phase_progress or {}
        self.speed_metrics = speed_metrics or {}
        self.estimation_data = estimation_data or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert snapshot to dictionary.

        Returns:
            Snapshot as dictionary
        """
        return {
            "timestamp": self.timestamp,
            "current_phase": self.current_phase,
            "overall_progress": self.overall_progress,
            "elapsed_time": self.elapsed_time,
            "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total,
            "current_task": self.current_task,
            "phase_progress": self.phase_progress,
            "speed_metrics": self.speed_metrics,
            "estimation_data": self.estimation_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgressSnapshot:
        """
        Create snapshot from dictionary.

        Args:
            data: Dictionary data

        Returns:
            ProgressSnapshot instance
        """
        return cls(
            current_phase=data.get("current_phase", ""),
            overall_progress=data.get("overall_progress", 0.0),
            elapsed_time=data.get("elapsed_time", 0.0),
            tasks_completed=data.get("tasks_completed", 0),
            tasks_total=data.get("tasks_total", 0),
            current_task=data.get("current_task", ""),
            phase_progress=data.get("phase_progress"),
            speed_metrics=data.get("speed_metrics"),
            estimation_data=data.get("estimation_data"),
        )
