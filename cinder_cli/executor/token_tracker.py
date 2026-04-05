"""
Token Tracker - Tracks token usage across LLM calls.
"""

from __future__ import annotations

import time
from typing import Any, Callable
from threading import Lock


class TokenTracker:
    """Thread-safe token usage tracker."""

    def __init__(self):
        self._lock = Lock()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._call_count = 0
        self._calls: list[dict[str, Any]] = []
        self._start_time: float | None = None
        self._callbacks: list[Callable[[int, int], None]] = []

    def add_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Add a callback to be called when tokens are recorded.
        
        Args:
            callback: Function that takes (input_tokens, output_tokens) as arguments
        """
        with self._lock:
            self._callbacks.append(callback)

    def start(self) -> None:
        """Start tracking and record start time."""
        with self._lock:
            self._start_time = time.time()

    def record_call(
        self,
        phase: str,
        input_tokens: int,
        output_tokens: int,
        model: str | None = None,
    ) -> None:
        """
        Record a single LLM call's token usage.

        Args:
            phase: Execution phase (plan, generation, evaluation, etc.)
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens
            model: Model name (optional)
        """
        with self._lock:
            if self._start_time is None:
                self._start_time = time.time()
            
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._call_count += 1
            
            self._calls.append({
                "phase": phase,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": model,
                "timestamp": time.time(),
            })
            
            current_input = self._total_input_tokens
            current_output = self._total_output_tokens
            callbacks = self._callbacks.copy()
        
        for callback in callbacks:
            try:
                callback(current_input, current_output)
            except Exception as e:
                pass

    def get_total_tokens(self) -> int:
        """Get total tokens used (input + output)."""
        with self._lock:
            return self._total_input_tokens + self._total_output_tokens

    def get_input_tokens(self) -> int:
        """Get total input tokens."""
        with self._lock:
            return self._total_input_tokens

    def get_output_tokens(self) -> int:
        """Get total output tokens."""
        with self._lock:
            return self._total_output_tokens

    def get_call_count(self) -> int:
        """Get total number of LLM calls."""
        with self._lock:
            return self._call_count

    def get_tokens_per_second(self) -> float:
        """
        Get token generation speed in tokens per second.

        Returns:
            Tokens per second rate
        """
        with self._lock:
            if self._start_time is None:
                return 0.0
            
            elapsed_time = time.time() - self._start_time
            if elapsed_time == 0:
                return 0.0
            
            total_tokens = self._total_input_tokens + self._total_output_tokens
            return total_tokens / elapsed_time

    def get_metrics(self) -> dict[str, Any]:
        """
        Get comprehensive token usage metrics.

        Returns:
            Dictionary with token usage statistics
        """
        with self._lock:
            elapsed_time = 0.0
            if self._start_time is not None:
                elapsed_time = time.time() - self._start_time
            
            total_tokens = self._total_input_tokens + self._total_output_tokens
            tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0.0
            
            return {
                "total_input_tokens": self._total_input_tokens,
                "total_output_tokens": self._total_output_tokens,
                "total_tokens": total_tokens,
                "call_count": self._call_count,
                "avg_input_tokens": self._total_input_tokens / self._call_count if self._call_count > 0 else 0,
                "avg_output_tokens": self._total_output_tokens / self._call_count if self._call_count > 0 else 0,
                "tokens_per_second": tokens_per_second,
                "elapsed_time": elapsed_time,
            }

    def get_phase_breakdown(self) -> dict[str, dict[str, int]]:
        """
        Get token usage breakdown by phase.

        Returns:
            Dictionary with token usage per phase
        """
        with self._lock:
            phase_stats: dict[str, dict[str, int]] = {}
            
            for call in self._calls:
                phase = call["phase"]
                if phase not in phase_stats:
                    phase_stats[phase] = {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "call_count": 0,
                    }
                
                phase_stats[phase]["input_tokens"] += call["input_tokens"]
                phase_stats[phase]["output_tokens"] += call["output_tokens"]
                phase_stats[phase]["total_tokens"] += call["total_tokens"]
                phase_stats[phase]["call_count"] += 1
            
            return phase_stats

    def reset(self) -> None:
        """Reset all tracking data."""
        with self._lock:
            self._total_input_tokens = 0
            self._total_output_tokens = 0
            self._call_count = 0
            self._calls = []
            self._start_time = None
