"""
Configuration management for progress tracking.
"""

from __future__ import annotations

from typing import Any


class ProgressConfig:
    """Configuration for progress tracking system."""

    DEFAULT_CONFIG = {
        "progress_tracking": {
            "enabled": True,
            "update_interval": 1,
            "batch_updates": True,
            "batch_interval": 5,
        },
        "estimation": {
            "enabled": True,
            "min_confidence": 0.2,
            "max_confidence": 0.95,
            "historical_weight": 0.7,
        },
        "database": {
            "wal_mode": True,
            "connection_pool": 5,
            "data_retention_days": 30,
        },
        "web": {
            "max_sse_connections": 10,
            "sse_timeout": 30,
            "heartbeat_interval": 15,
        },
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        for section, values in self.DEFAULT_CONFIG.items():
            if section not in self._config:
                self._config[section] = {}
            for key, value in values.items():
                if key not in self._config[section]:
                    self._config[section][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def is_progress_enabled(self) -> bool:
        """Check if progress tracking is enabled."""
        return self.get("progress_tracking.enabled", True)

    def is_estimation_enabled(self) -> bool:
        """Check if time estimation is enabled."""
        return self.get("estimation.enabled", True)

    def get_update_interval(self) -> int:
        """Get progress update interval in seconds."""
        return self.get("progress_tracking.update_interval", 1)

    def get_batch_interval(self) -> int:
        """Get batch update interval in seconds."""
        return self.get("progress_tracking.batch_interval", 5)

    def get_max_sse_connections(self) -> int:
        """Get maximum SSE connections."""
        return self.get("web.max_sse_connections", 10)

    def get_data_retention_days(self) -> int:
        """Get data retention period in days."""
        return self.get("database.data_retention_days", 30)

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return dict(self._config)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> ProgressConfig:
        """Create configuration from dictionary."""
        return cls(config)
