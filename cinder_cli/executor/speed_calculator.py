"""
Speed Calculator - Calculates execution speed metrics.
"""

from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any


class SpeedCalculator:
    """Calculates execution speed metrics."""

    def __init__(self):
        self._lock = Lock()
        self._tasks_completed = 0
        self._start_time: datetime | None = None
        self._task_times: list[float] = []
        self._phase_speeds: dict[str, list[float]] = {}

    def start(self) -> None:
        """Start speed calculation."""
        with self._lock:
            self._start_time = datetime.now()

    def record_task_completed(self, duration: float | None = None) -> None:
        """
        Record a completed task.

        Args:
            duration: Task duration in seconds (optional)
        """
        with self._lock:
            self._tasks_completed += 1
            if duration is not None:
                self._task_times.append(duration)

    def record_phase_progress(self, phase: str, progress: float, elapsed: float) -> None:
        """
        Record phase progress for speed calculation.

        Args:
            phase: Phase name
            progress: Progress percentage (0-100)
            elapsed: Elapsed time in seconds
        """
        with self._lock:
            if phase not in self._phase_speeds:
                self._phase_speeds[phase] = []
            
            if progress > 0 and elapsed > 0:
                speed = progress / elapsed
                self._phase_speeds[phase].append(speed)

    def get_tasks_per_minute(self) -> float:
        """
        Calculate tasks completed per minute.

        Returns:
            Tasks per minute, or 0 if no time elapsed
        """
        with self._lock:
            if not self._start_time or self._tasks_completed == 0:
                return 0.0
            
            elapsed = (datetime.now() - self._start_time).total_seconds()
            if elapsed == 0:
                return 0.0
            
            return (self._tasks_completed / elapsed) * 60.0

    def get_average_task_time(self) -> float:
        """
        Calculate average task completion time.

        Returns:
            Average time in seconds, or 0 if no tasks
        """
        with self._lock:
            if not self._task_times:
                return 0.0
            return sum(self._task_times) / len(self._task_times)

    def get_phase_speed(self, phase: str) -> float:
        """
        Get average speed for a phase.

        Args:
            phase: Phase name

        Returns:
            Average speed (progress per second), or 0 if no data
        """
        with self._lock:
            if phase not in self._phase_speeds or not self._phase_speeds[phase]:
                return 0.0
            return sum(self._phase_speeds[phase]) / len(self._phase_speeds[phase])

    def get_speed_metrics(self) -> dict[str, Any]:
        """
        Get all speed metrics.

        Returns:
            Speed metrics dictionary
        """
        with self._lock:
            return {
                "tasks_per_minute": self.get_tasks_per_minute(),
                "average_task_time": self.get_average_task_time(),
                "tasks_completed": self._tasks_completed,
                "phase_speeds": {
                    phase: sum(speeds) / len(speeds) if speeds else 0.0
                    for phase, speeds in self._phase_speeds.items()
                },
            }

    def reset(self) -> None:
        """Reset all speed calculations."""
        with self._lock:
            self._tasks_completed = 0
            self._start_time = None
            self._task_times = []
            self._phase_speeds = {}
