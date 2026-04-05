"""
Estimation Engine - Manages time estimation algorithms.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class EstimationEngine:
    """Manages time estimation for execution progress."""

    def __init__(self):
        self._historical_stats: dict[str, Any] = {}
        self._current_estimate: float = 0.0
        self._confidence: float = 0.0
        self._estimation_history: list[dict[str, Any]] = []

    def set_historical_stats(self, stats: dict[str, Any]) -> None:
        """
        Set historical execution statistics.

        Args:
            stats: Historical statistics from ExecutionLogger
        """
        self._historical_stats = stats

    def estimate_initial(self, tasks_count: int, goal_type: str = "") -> tuple[float, float]:
        """
        Estimate initial execution time.

        Args:
            tasks_count: Number of tasks to execute
            goal_type: Type of goal (optional)

        Returns:
            Tuple of (estimated_seconds, confidence)
        """
        if self._historical_stats.get("total", 0) > 0:
            avg_time_per_task = self._historical_stats.get("avg_tasks_count", 0)
            if avg_time_per_task > 0:
                avg_execution_time = self._historical_stats.get("avg_execution_time", 0)
                time_per_task = avg_execution_time / avg_time_per_task
                estimate = time_per_task * tasks_count
                confidence = 0.5
            else:
                estimate = tasks_count * 30
                confidence = 0.3
        else:
            estimate = tasks_count * 45
            confidence = 0.2
        
        self._current_estimate = estimate
        self._confidence = confidence
        self._record_estimation("initial", estimate, confidence)
        
        return estimate, confidence

    def estimate_remaining(
        self,
        elapsed: float,
        progress: float,
        tasks_completed: int,
        tasks_total: int,
    ) -> tuple[float, float]:
        """
        Estimate remaining execution time.

        Args:
            elapsed: Elapsed time in seconds
            progress: Progress percentage (0-100)
            tasks_completed: Number of completed tasks
            tasks_total: Total number of tasks

        Returns:
            Tuple of (estimated_remaining_seconds, confidence)
        """
        if progress <= 0:
            return self._current_estimate, self._confidence
        
        speed = progress / elapsed if elapsed > 0 else 0
        if speed <= 0:
            return self._current_estimate, self._confidence
        
        remaining_progress = 100.0 - progress
        remaining_time = remaining_progress / speed if speed > 0 else 0
        
        confidence = min(0.95, 0.3 + (progress / 100.0) * 0.65)
        
        self._current_estimate = remaining_time
        self._confidence = confidence
        self._record_estimation("dynamic", remaining_time, confidence)
        
        return remaining_time, confidence

    def estimate_phase(self, phase: str, tasks_in_phase: int = 0) -> float:
        """
        Estimate duration for a specific phase.

        Args:
            phase: Phase name
            tasks_in_phase: Number of tasks in phase (optional)

        Returns:
            Estimated duration in seconds
        """
        phase_stats = self._historical_stats.get("phase_statistics", {})
        
        if phase in phase_stats:
            return phase_stats[phase].get("avg_duration", 30.0)
        
        default_durations = {
            "plan": 15.0,
            "generation": tasks_in_phase * 20.0 if tasks_in_phase > 0 else 60.0,
            "evaluation": tasks_in_phase * 10.0 if tasks_in_phase > 0 else 30.0,
            "decision": 10.0,
        }
        
        return default_durations.get(phase, 30.0)

    def get_confidence_interval(self, estimate: float, confidence: float) -> tuple[float, float]:
        """
        Calculate confidence interval for estimate.

        Args:
            estimate: Estimated time in seconds
            confidence: Confidence level (0-1)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        uncertainty = 1.0 - confidence
        margin = estimate * uncertainty
        
        lower = max(0, estimate - margin)
        upper = estimate + margin
        
        return lower, upper

    def _record_estimation(self, method: str, estimate: float, confidence: float) -> None:
        """
        Record estimation for history tracking.

        Args:
            method: Estimation method used
            estimate: Estimated time
            confidence: Confidence level
        """
        self._estimation_history.append({
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "estimate": estimate,
            "confidence": confidence,
        })

    def get_estimation_history(self) -> list[dict[str, Any]]:
        """
        Get estimation history.

        Returns:
            List of estimation records
        """
        return list(self._estimation_history)

    def reset(self) -> None:
        """Reset estimation engine."""
        self._current_estimate = 0.0
        self._confidence = 0.0
        self._estimation_history = []
