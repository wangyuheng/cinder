"""
Configuration management for Cinder CLI.
Manages ~/.cinder/config.yaml and related settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Config:
    """Manages Cinder configuration stored in ~/.cinder/config.yaml."""

    DEFAULT_CONFIG = {
        "backend": "ollama",
        "model": "qwen3.5:0.8b",
        "claude_command": "claude",
        "soul_path": "soul.md",
        "meta_path": "",
        "temperature": 0.2,
        "reflection_loop": False,
        "max_iterations": 3,
        "sleep_seconds": 1.0,
        "proxy_mode": False,
        "decision_logging": True,
        "log_retention_days": 90,
        "encryption": False,
        "workspace_dir": "",
        "ollama_keep_alive": "10m",
        "ollama_stream": True,
        "ollama_debug": True,
    }

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or Path.home() / ".cinder"
        self.config_file = self.config_dir / "config.yaml"
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self._save()

    def _save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self._config[key] = value
        self._save()

    def update(self, values: dict[str, Any]) -> None:
        """Update multiple configuration values and save."""
        self._config.update(values)
        self._save()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._save()

    @property
    def database_path(self) -> Path:
        """Get the path to the SQLite database."""
        return self.config_dir / "decisions.db"

    @property
    def all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
