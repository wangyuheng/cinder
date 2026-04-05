"""
Integration with AutonomousExecutor for progress tracking.
"""

from __future__ import annotations

import signal
from typing import Any

from cinder_cli.executor.progress_tracker import ExecutionPhase
from cinder_cli.executor.progress_snapshot import ProgressSnapshot


class ExecutorProgressIntegration:
    """Integrates progress tracking with AutonomousExecutor."""

    def __init__(self, executor):
        self.executor = executor
        self._setup_interrupt_handler()

    def _setup_interrupt_handler(self) -> None:
        """Setup handler for execution interruption."""
        def interrupt_handler(signum, frame):
            self._save_progress_on_interrupt()
            raise KeyboardInterrupt("Execution interrupted by user")

        signal.signal(signal.SIGINT, interrupt_handler)

    def _save_progress_on_interrupt(self) -> None:
        """Save progress state when execution is interrupted."""
        if not self.executor._execution_id:
            return

        try:
            progress_data = self.executor.progress_tracker.get_progress()
            speed_metrics = self.executor.speed_calculator.get_speed_metrics()
            phase_timestamps = self.executor.time_recorder.get_phase_timestamps()

            self.executor.execution_logger.update_progress(
                self.executor._execution_id,
                {
                    "interrupted": True,
                    "progress": progress_data,
                    "speed_metrics": speed_metrics,
                    "phase_timestamps": phase_timestamps,
                }
            )
        except Exception:
            pass

    def start_execution(self, goal: str) -> None:
        """Initialize progress tracking for execution."""
        if not self.executor._progress_enabled:
            return

        self.executor.time_recorder.start_execution()
        self.executor.speed_calculator.start()

        stats = self.executor.execution_logger.get_execution_statistics()
        self.executor.estimation_engine.set_historical_stats(stats)

    def start_phase(self, phase: ExecutionPhase) -> None:
        """Start tracking a phase."""
        if not self.executor._progress_enabled:
            return

        self.executor.progress_tracker.start_phase(phase)
        self.executor.time_recorder.start_phase(phase.value)
        self.executor.progress_broadcaster.broadcast(
            self.executor.progress_tracker.get_progress()
        )

    def update_phase_progress(self, progress: float) -> None:
        """Update current phase progress."""
        if not self.executor._progress_enabled:
            return

        self.executor.progress_tracker.update_phase_progress(progress)
        
        progress_data = self.executor.progress_tracker.get_progress()
        self.executor.progress_broadcaster.broadcast(progress_data)

    def complete_phase(self, phase: ExecutionPhase) -> None:
        """Complete a phase."""
        if not self.executor._progress_enabled:
            return

        self.executor.progress_tracker.complete_phase(phase)
        self.executor.time_recorder.end_phase(phase.value)

        duration = self.executor.time_recorder.get_phase_elapsed_time(phase)
        if duration:
            self.executor.speed_calculator.record_phase_progress(
                phase.value, 100.0, duration
            )

    def start_task(self, task_id: str, description: str) -> None:
        """Start tracking a task."""
        if not self.executor._progress_enabled:
            return

        self.executor.progress_tracker.set_current_task(description)
        self.executor.time_recorder.start_task(task_id, description)

    def complete_task(self, task_id: str) -> None:
        """Complete a task."""
        if not self.executor._progress_enabled:
            return

        self.executor.time_recorder.end_task(task_id)
        
        timestamps = self.executor.time_recorder.get_task_timestamps()
        if task_id in timestamps and "duration" in timestamps[task_id]:
            duration = timestamps[task_id]["duration"]
            self.executor.speed_calculator.record_task_completed(duration)

        tasks_completed = self.executor.progress_tracker.get_progress()["tasks_completed"] + 1
        self.executor.progress_tracker.update_tasks_completed(tasks_completed)

    def end_execution(self, success: bool = True) -> dict[str, Any]:
        """Finalize progress tracking."""
        if not self.executor._progress_enabled:
            return {}

        self.executor.time_recorder.end_execution()
        
        progress_data = self.executor.progress_tracker.get_progress()
        phase_timestamps = self.executor.time_recorder.get_phase_timestamps()
        speed_metrics = self.executor.speed_calculator.get_speed_metrics()
        estimation_history = self.executor.estimation_engine.get_estimation_history()

        duration = self.executor.time_recorder.get_execution_duration()

        return {
            "progress_data": progress_data,
            "phase_timestamps": phase_timestamps,
            "speed_metrics": speed_metrics,
            "estimation_data": {
                "history": estimation_history,
                "final_estimate": progress_data.get("elapsed_time", 0),
            },
            "execution_time": duration,
            "success": success,
        }

    def get_current_snapshot(self) -> ProgressSnapshot | None:
        """Get current progress snapshot."""
        if not self.executor._progress_enabled:
            return None

        progress = self.executor.progress_tracker.get_progress()
        speed = self.executor.speed_calculator.get_speed_metrics()
        
        return ProgressSnapshot(
            current_phase=progress["current_phase"],
            overall_progress=progress["overall_progress"],
            elapsed_time=progress["elapsed_time"],
            tasks_completed=progress["tasks_completed"],
            tasks_total=progress["tasks_total"],
            current_task=progress["current_task"],
            phase_progress=progress["phase_progress"],
            speed_metrics=speed,
        )
