"""
Color-aware CLI Progress Display - Supports both color and no-color modes.
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


class ColorAwareProgressDisplay:
    """Progress display that adapts to color support."""

    def __init__(self, console: Console | None = None, force_color: bool | None = None):
        self.console = console or Console()
        self._force_color = force_color
        self._progress: Progress | None = None
        self._task_id: int | None = None

    def _supports_color(self) -> bool:
        """Check if terminal supports color."""
        if self._force_color is not None:
            return self._force_color
        
        return self.console.color_system is not None

    def _get_status_symbol(self, status: str) -> str:
        """Get status symbol based on color support."""
        if self._supports_color():
            color_map = {
                "success": "[green]✓[/green]",
                "error": "[red]✗[/red]",
                "active": "[blue]⏳[/blue]",
                "pending": "[gray]⏸[/gray]",
            }
            return color_map.get(status, "•")
        else:
            symbol_map = {
                "success": "[OK]",
                "error": "[ERR]",
                "active": "[...]",
                "pending": "[ ]",
            }
            return symbol_map.get(status, "[?]")

    def create_progress(self) -> Progress:
        """
        Create color-aware progress bar.

        Returns:
            Rich Progress instance
        """
        if self._supports_color():
            return self._create_color_progress()
        else:
            return self._create_no_color_progress()

    def _create_color_progress(self) -> Progress:
        """Create progress with color support."""
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

    def _create_no_color_progress(self) -> Progress:
        """Create progress without color."""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
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
                symbol = self._get_status_symbol("success")
                self._progress.update(
                    self._task_id,
                    completed=100,
                    description=f"{symbol} {message}",
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
        symbol = self._get_status_symbol("success")
        
        if self._supports_color():
            lines = [f"\n[bold green]{symbol} {phase.upper()} Phase Complete[/bold green]"]
            lines.append(f"  Duration: {duration:.1f}s")
            
            if tasks_completed > 0:
                lines.append(f"  Tasks: {tasks_completed}")
            
            if quality_score is not None:
                lines.append(f"  Quality: {quality_score:.2f}")
            
            self.console.print("\n".join(lines))
        else:
            summary = f"\n{symbol} {phase.upper()} Phase Complete"
            summary += f"\n  Duration: {duration:.1f}s"
            
            if tasks_completed > 0:
                summary += f"\n  Tasks: {tasks_completed}"
            
            if quality_score is not None:
                summary += f"\n  Quality: {quality_score:.2f}"
            
            self.console.print(summary)

    def display_error(self, message: str) -> None:
        """
        Display error message.

        Args:
            message: Error message
        """
        symbol = self._get_status_symbol("error")
        
        if self._supports_color():
            self.console.print(f"\n[bold red]{symbol} Error:[/bold red] {message}")
        else:
            self.console.print(f"\n{symbol} Error: {message}")

    def display_phase_status(self, phase: str, status: str) -> None:
        """
        Display phase status.

        Args:
            phase: Phase name
            status: Status (success, error, active, pending)
        """
        symbol = self._get_status_symbol(status)
        
        if self._supports_color():
            self.console.print(f"{symbol} {phase}")
        else:
            self.console.print(f"{symbol} {phase}")
