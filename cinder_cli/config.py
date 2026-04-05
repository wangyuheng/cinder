"""
Configuration management for Cinder CLI.
Supports multiple configuration sources with priority:
1. Project directory: .cinder/config.yaml or cinder.yaml
2. User directory: ~/.cinder/config.yaml
3. Default configuration
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Manages Cinder configuration with project-level support."""

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
        "ollama_base_url": "http://localhost:11434",
        "ollama_keep_alive": "10m",
        "ollama_stream": True,
        "ollama_debug": True,
        "plan_quality_threshold": 0.7,
        "code_quality_threshold": 0.8,
        "evaluation_quality_threshold": 0.7,
        "enable_iterative_generation": True,
        "enable_plan_validation": True,
        "enable_comprehensive_evaluation": True,
    }

    def __init__(self, config_dir: Path | None = None):
        self._config: dict[str, Any] = {}
        
        if config_dir:
            self.config_dir = config_dir
            self.config_file = self.config_dir / "config.yaml"
            self._config_source = "custom"
        else:
            self.config_file, self.config_dir = self._find_config_file()
        
        self._load()

    def _find_config_file(self) -> tuple[Path, Path]:
        """
        Find configuration file with priority:
        1. .cinder/config.yaml (project directory)
        2. cinder.yaml (project directory)
        3. ~/.cinder/config.yaml (user directory)
        
        Returns:
            Tuple of (config_file, config_dir)
        """
        cwd = Path.cwd()
        
        project_config = cwd / ".cinder" / "config.yaml"
        if project_config.exists():
            return project_config, project_config.parent
        
        project_simple_config = cwd / "cinder.yaml"
        if project_simple_config.exists():
            return project_simple_config, project_simple_config.parent
        
        user_config_dir = Path.home() / ".cinder"
        user_config = user_config_dir / "config.yaml"
        
        return user_config, user_config_dir

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
