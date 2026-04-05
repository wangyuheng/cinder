"""
Progress Tracker - Tracks execution progress and calculates percentages.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any


class ExecutionPhase(str, Enum):
    """Execution phases."""
    PLAN = "plan"
    GENERATION = "generation"
    EVALUATION = "evaluation"
    DECISION = "decision"
    COMPLETE = "complete"


class ProgressTracker:
    """Tracks execution progress and calculates metrics."""

    def __init__(self):
        self._lock = Lock()
        self._current_phase = ExecutionPhase.PLAN
        self._phase_progress: dict[ExecutionPhase, float] = {
            phase: 0.0 for phase in ExecutionPhase
        }
        self._start_time = datetime.now()
        self._phase_start_times: dict[ExecutionPhase, datetime] = {}
        self._tasks_total = 0
        self._tasks_completed = 0
        self._current_task = ""

    def start_phase(self, phase: ExecutionPhase) -> None:
        """
        Start a new execution phase.

        Args:
            phase: Phase to start
        """
        with self._lock:
            self._current_phase = phase
            self._phase_start_times[phase] = datetime.now()
            self._phase_progress[phase] = 0.0

    def update_phase_progress(self, progress: float) -> None:
        """
        Update progress for current phase.

        Args:
            progress: Progress percentage (0.0 to 100.0)
        """
        with self._lock:
            self._phase_progress[self._current_phase] = min(100.0, max(0.0, progress))

    def complete_phase(self, phase: ExecutionPhase) -> None:
        """
        Mark a phase as complete.

        Args:
            phase: Phase to complete
        """
        with self._lock:
            self._phase_progress[phase] = 100.0

    def set_tasks_total(self, total: int) -> None:
        """
        Set total number of tasks.

        Args:
            total: Total tasks count
        """
        with self._lock:
            self._tasks_total = total

    def update_tasks_completed(self, completed: int) -> None:
        """
        Update number of completed tasks.

        Args:
            completed: Completed tasks count
        """
        with self._lock:
            self._tasks_completed = completed

    def set_current_task(self, task: str) -> None:
        """
        Set current task description.

        Args:
            task: Task description
        """
        with self._lock:
            self._current_task = task

    def get_progress(self) -> dict[str, Any]:
        """
        Get current progress state.

        Returns:
            Progress state dictionary
        """
        with self._lock:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            
            overall_progress = self._calculate_overall_progress()
            
            return {
                "current_phase": self._current_phase.value,
                "phase_progress": {
                    phase.value: progress
                    for phase, progress in self._phase_progress.items()
                },
                "overall_progress": overall_progress,
                "elapsed_time": elapsed,
                "tasks_total": self._tasks_total,
                "tasks_completed": self._tasks_completed,
                "current_task": self._current_task,
                "start_time": self._start_time.isoformat(),
                "phase_start_times": {
                    phase.value: time.isoformat()
                    for phase, time in self._phase_start_times.items()
                },
            }

    def _calculate_overall_progress(self) -> float:
        """
        Calculate overall execution progress.

        Returns:
            Overall progress percentage
        """
        phase_weights = {
            ExecutionPhase.PLAN: 0.15,
            ExecutionPhase.GENERATION: 0.50,
            ExecutionPhase.EVALUATION: 0.25,
            ExecutionPhase.DECISION: 0.10,
            ExecutionPhase.COMPLETE: 0.0,
        }
        
        total_progress = 0.0
        for phase, weight in phase_weights.items():
            total_progress += (self._phase_progress[phase] / 100.0) * weight
        
        return min(100.0, total_progress * 100.0)

    def get_phase_elapsed_time(self, phase: ExecutionPhase) -> float | None:
        """
        Get elapsed time for a specific phase.

        Args:
            phase: Phase to check

        Returns:
            Elapsed time in seconds, or None if phase not started
        """
        with self._lock:
            if phase not in self._phase_start_times:
                return None
            
            start_time = self._phase_start_times[phase]
            if self._phase_progress[phase] >= 100.0:
                return None
            
            return (datetime.now() - start_time).total_seconds()

    def reset(self) -> None:
        """Reset progress tracker to initial state."""
        with self._lock:
            self._current_phase = ExecutionPhase.PLAN
            self._phase_progress = {
                phase: 0.0 for phase in ExecutionPhase
            }
            self._start_time = datetime.now()
            self._phase_start_times = {}
            self._tasks_total = 0
            self._tasks_completed = 0
            self._current_task = ""
