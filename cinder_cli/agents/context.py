"""
Context management for agent execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ContextEntry:
    """A single entry in the context."""
    
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    scope: str = "session"  # session, user, project
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "scope": self.scope,
            "metadata": self.metadata,
        }


class BaseContextManager(ABC):
    """Base class for context management."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, scope: str = "session") -> None:
        """Set a value in context."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from context."""
        pass
    
    @abstractmethod
    def query(self, filter_dict: dict[str, Any]) -> list[ContextEntry]:
        """Query context entries matching filter."""
        pass
    
    @abstractmethod
    def clear(self, scope: str | None = None) -> None:
        """Clear context entries."""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Persist context to storage."""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """Load context from storage."""
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """Get size of context in bytes."""
        pass
    
    @abstractmethod
    def get_entry_count(self) -> int:
        """Get number of entries in context."""
        pass


class InMemoryContextManager(BaseContextManager):
    """In-memory context manager for short-term storage."""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.entries: dict[str, ContextEntry] = {}
        self.access_log: list[tuple[str, datetime]] = []
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context."""
        entry = self.entries.get(key)
        if entry is None:
            return default
        self.access_log.append((key, datetime.now()))
        return entry.value
    
    def set(self, key: str, value: Any, scope: str = "session") -> None:
        """Set a value in context."""
        entry = ContextEntry(
            key=key,
            value=value,
            scope=scope,
        )
        self.entries[key] = entry
        self._enforce_size_limit()
    
    def delete(self, key: str) -> bool:
        """Delete a value from context."""
        if key in self.entries:
            del self.entries[key]
            return True
        return False
    
    def query(self, filter_dict: dict[str, Any]) -> list[ContextEntry]:
        """Query context entries matching filter."""
        results = []
        for entry in self.entries.values():
            match = True
            for key, value in filter_dict.items():
                if key == "scope" and entry.scope != value:
                    match = False
                    break
                elif key == "key_pattern" and value not in entry.key:
                    match = False
                    break
                elif key == "after" and entry.timestamp < value:
                    match = False
                    break
                elif key == "before" and entry.timestamp > value:
                    match = False
                    break
            if match:
                results.append(entry)
        return results
    
    def clear(self, scope: str | None = None) -> None:
        """Clear context entries."""
        if scope is None:
            self.entries.clear()
        else:
            keys_to_delete = [
                key for key, entry in self.entries.items()
                if entry.scope == scope
            ]
            for key in keys_to_delete:
                del self.entries[key]
    
    def save(self) -> None:
        """Persist context to storage (no-op for in-memory)."""
        pass
    
    def load(self) -> None:
        """Load context from storage (no-op for in-memory)."""
        pass
    
    def get_size(self) -> int:
        """Get size of context in bytes."""
        import sys
        return sys.getsizeof(self.entries)
    
    def get_entry_count(self) -> int:
        """Get number of entries in context."""
        return len(self.entries)
    
    def _enforce_size_limit(self) -> None:
        """Enforce size limit by removing oldest entries."""
        while self.get_size() > self.max_size_bytes and self.entries:
            oldest_key = min(
                self.entries.keys(),
                key=lambda k: self.entries[k].timestamp
            )
            del self.entries[oldest_key]
    
    def get_access_frequency(self, key: str) -> int:
        """Get access frequency for a key."""
        return sum(1 for k, _ in self.access_log if k == key)
