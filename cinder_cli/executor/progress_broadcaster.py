"""
Progress Broadcaster - Supports listener registration and broadcasting.
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Callable
from weakref import WeakSet


ProgressListener = Callable[[dict[str, Any]], None]


class ProgressBroadcaster:
    """Manages progress listeners and broadcasts updates."""

    def __init__(self):
        self._lock = Lock()
        self._listeners: WeakSet[ProgressListener] = WeakSet()

    def add_listener(self, listener: ProgressListener) -> None:
        """
        Add a progress listener.

        Args:
            listener: Callback function to receive progress updates
        """
        with self._lock:
            self._listeners.add(listener)

    def remove_listener(self, listener: ProgressListener) -> None:
        """
        Remove a progress listener.

        Args:
            listener: Callback function to remove
        """
        with self._lock:
            self._listeners.discard(listener)

    def broadcast(self, progress_data: dict[str, Any]) -> None:
        """
        Broadcast progress update to all listeners.

        Args:
            progress_data: Progress data to broadcast
        """
        with self._lock:
            listeners = list(self._listeners)
        
        for listener in listeners:
            try:
                listener(progress_data)
            except Exception:
                pass

    def clear_listeners(self) -> None:
        """Remove all listeners."""
        with self._lock:
            self._listeners.clear()

    def listener_count(self) -> int:
        """
        Get number of registered listeners.

        Returns:
            Number of listeners
        """
        with self._lock:
            return len(self._listeners)
