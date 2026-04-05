"""
Responsive CLI Progress Display - Adapts to terminal width.
"""

from __future__ import annotations

import os
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


class ResponsiveProgressDisplay:
    """Responsive progress display that adapts to terminal width."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._progress: Progress | None = None
        self._task_id: int | None = None
        self._min_width = 60
        self._compact_threshold = 80

    def _get_terminal_width(self) -> int:
        """Get terminal width."""
        try:
            return os.get_terminal_size().columns
        except Exception:
            return 80

    def _is_compact_mode(self) -> bool:
        """Check if should use compact mode."""
        width = self._get_terminal_width()
        return width < self._compact_threshold

    def create_progress(self) -> Progress:
        """
        Create progress bar adapted to terminal width.

        Returns:
            Rich Progress instance
        """
        width = self._get_terminal_width()
        
        if width < self._min_width:
            return self._create_minimal_progress()
        elif self._is_compact_mode():
            return self._create_compact_progress()
        else:
            return self._create_full_progress()

    def _create_minimal_progress(self) -> Progress:
        """Create minimal progress for narrow terminals."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description:<20}"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        )

    def _create_compact_progress(self) -> Progress:
        """Create compact progress for medium terminals."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description:<30}"),
            BarColumn(bar_width=20),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )

    def _create_full_progress(self) -> Progress:
        """Create full progress for wide terminals."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description:<40}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[speed]:.1f} tasks/min"),
            TextColumn("[blue]in:{task.fields[input_tokens]}[/blue] [green]out:{task.fields[output_tokens]}[/green]"),
            TextColumn("[magenta]{task.fields[token_speed]:.1f} tok/s"),
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
            input_tokens=0,
            output_tokens=0,
            token_speed=0.0,
        )
        # Refresh to ensure task is created
        self._progress.refresh()

    def update(
        self,
        progress: float,
        description: str | None = None,
        speed: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        token_speed: float = 0.0,
    ) -> None:
        """
        Update progress display.

        Args:
            progress: Progress percentage (0-100)
            description: Updated description (optional)
            speed: Current speed in tasks/min
            input_tokens: Total input tokens used
            output_tokens: Total output tokens used
            token_speed: Token generation speed in tokens/min
        """
        if self._progress and self._task_id is not None:
            update_kwargs = {"completed": progress}
            
            if description:
                if self._is_compact_mode():
                    update_kwargs["description"] = description[:30]
                else:
                    update_kwargs["description"] = description
            
            if not self._is_compact_mode():
                update_kwargs["speed"] = speed
                update_kwargs["input_tokens"] = input_tokens
                update_kwargs["output_tokens"] = output_tokens
                update_kwargs["token_speed"] = token_speed
            
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
                    description=f"[green]{message[:30]}[/green]",
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
        if self._is_compact_mode():
            summary = f"✓ {phase[:10]}: {duration:.1f}s"
            if tasks_completed > 0:
                summary += f" ({tasks_completed} tasks)"
            self.console.print(summary)
        else:
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
        if self._is_compact_mode():
            self.console.print(f"[red]✗ {message[:50]}[/red]")
        else:
            self.console.print(f"\n[bold red]✗ Error:[/bold red] {message}")
