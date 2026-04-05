"""
Time Recorder - Records phase and task timestamps.
"""

from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any


class TimeRecorder:
    """Records timestamps for phases and tasks."""

    def __init__(self):
        self._lock = Lock()
        self._phase_timestamps: dict[str, dict[str, Any]] = {}
        self._task_timestamps: dict[str, dict[str, Any]] = {}
        self._execution_start: datetime | None = None
        self._execution_end: datetime | None = None

    def start_execution(self) -> None:
        """Record execution start time."""
        with self._lock:
            self._execution_start = datetime.now()

    def end_execution(self) -> None:
        """Record execution end time."""
        with self._lock:
            self._execution_end = datetime.now()

    def start_phase(self, phase: str) -> None:
        """
        Record phase start time.

        Args:
            phase: Phase name
        """
        with self._lock:
            if phase not in self._phase_timestamps:
                self._phase_timestamps[phase] = {}
            self._phase_timestamps[phase]["start"] = datetime.now().isoformat()

    def end_phase(self, phase: str) -> None:
        """
        Record phase end time and calculate duration.

        Args:
            phase: Phase name
        """
        with self._lock:
            if phase not in self._phase_timestamps:
                self._phase_timestamps[phase] = {}
            
            end_time = datetime.now()
            self._phase_timestamps[phase]["end"] = end_time.isoformat()
            
            if "start" in self._phase_timestamps[phase]:
                start_time = datetime.fromisoformat(self._phase_timestamps[phase]["start"])
                duration = (end_time - start_time).total_seconds()
                self._phase_timestamps[phase]["duration"] = duration

    def start_task(self, task_id: str, description: str = "") -> None:
        """
        Record task start time.

        Args:
            task_id: Task identifier
            description: Task description
        """
        with self._lock:
            if task_id not in self._task_timestamps:
                self._task_timestamps[task_id] = {}
            self._task_timestamps[task_id]["start"] = datetime.now().isoformat()
            self._task_timestamps[task_id]["description"] = description

    def end_task(self, task_id: str) -> None:
        """
        Record task end time and calculate duration.

        Args:
            task_id: Task identifier
        """
        with self._lock:
            if task_id not in self._task_timestamps:
                self._task_timestamps[task_id] = {}
            
            end_time = datetime.now()
            self._task_timestamps[task_id]["end"] = end_time.isoformat()
            
            if "start" in self._task_timestamps[task_id]:
                start_time = datetime.fromisoformat(self._task_timestamps[task_id]["start"])
                duration = (end_time - start_time).total_seconds()
                self._task_timestamps[task_id]["duration"] = duration

    def get_phase_timestamps(self) -> dict[str, Any]:
        """
        Get all phase timestamps.

        Returns:
            Phase timestamps dictionary
        """
        with self._lock:
            return dict(self._phase_timestamps)

    def get_task_timestamps(self) -> dict[str, Any]:
        """
        Get all task timestamps.

        Returns:
            Task timestamps dictionary
        """
        with self._lock:
            return dict(self._task_timestamps)

    def get_execution_duration(self) -> float | None:
        """
        Get total execution duration.

        Returns:
            Duration in seconds, or None if execution not complete
        """
        with self._lock:
            if self._execution_start and self._execution_end:
                return (self._execution_end - self._execution_start).total_seconds()
            return None

    def reset(self) -> None:
        """Reset all recorded timestamps."""
        with self._lock:
            self._phase_timestamps = {}
            self._task_timestamps = {}
            self._execution_start = None
            self._execution_end = None
