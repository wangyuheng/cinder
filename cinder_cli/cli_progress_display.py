"""
CLI Progress Display - Enhanced Rich progress display.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class CLIProgressDisplay:
    """Enhanced CLI progress display with time and speed information."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._progress: Progress | None = None
        self._task_id: int | None = None

    def create_progress(self) -> Progress:
        """
        Create enhanced progress bar.

        Returns:
            Rich Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[speed]:.1f} tasks/min"),
            console=self.console,
        )

    def start(self, description: str = "Executing...") -> None:
        """
        Start progress display.

        Args:
            description: Initial description
        """
        self._progress = self.create_progress()
        self._progress.start()
        self._task_id = self._progress.add_task(
            description,
            total=100,
            speed=0.0,
        )

    def update(
        self,
        progress: float,
        description: str | None = None,
        speed: float = 0.0,
    ) -> None:
        """
        Update progress display.

        Args:
            progress: Progress percentage (0-100)
            description: Updated description (optional)
            speed: Current speed in tasks/min
        """
        if self._progress and self._task_id is not None:
            update_kwargs = {
                "completed": progress,
                "speed": speed,
            }
            if description:
                update_kwargs["description"] = description
            
            self._progress.update(self._task_id, **update_kwargs)

    def stop(self, message: str = "Complete") -> None:
        """
        Stop progress display.

        Args:
            message: Completion message
        """
        if self._progress:
            if self._task_id is not None:
                self._progress.update(
                    self._task_id,
                    completed=100,
                    description=f"[green]{message}[/green]",
                )
            self._progress.stop()

    def display_phase_summary(
        self,
        phase: str,
        duration: float,
        tasks_completed: int = 0,
        quality_score: float | None = None,
    ) -> None:
        """
        Display phase completion summary.

        Args:
            phase: Phase name
            duration: Phase duration in seconds
            tasks_completed: Number of tasks completed
            quality_score: Quality score (optional)
        """
        lines = [f"\n[bold green]✓ {phase.upper()} Phase Complete[/bold green]"]
        lines.append(f"  Duration: {duration:.1f}s")
        
        if tasks_completed > 0:
            lines.append(f"  Tasks: {tasks_completed}")
        
        if quality_score is not None:
            lines.append(f"  Quality: {quality_score:.2f}")
        
        self.console.print("\n".join(lines))

    def display_error(self, message: str) -> None:
        """
        Display error message.

        Args:
            message: Error message
        """
        self.console.print(f"\n[bold red]✗ Error:[/bold red] {message}")
