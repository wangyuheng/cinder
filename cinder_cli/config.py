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
        "codex_integration": {
            "enabled": False,
            "fallback_on_error": True,
            "default_executor": "exec",
            "exec": {
                "model": "gpt-5.4",
                "sandbox_mode": "workspace-write",
                "approval_policy": "never",
                "skip_git_repo_check": True,
                "ephemeral": True,
                "timeout": 300,
            },
        },
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
    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()

    @property
    def codex(self) -> dict[str, Any]:
        """Get Codex integration configuration."""
        return self._config.get("codex_integration", self.DEFAULT_CONFIG["codex_integration"])

    def is_codex_enabled(self) -> bool:
        """Check if Codex integration is enabled."""
        return self.codex.get("enabled", False)

    def validate_codex_config(self) -> list[str]:
        """
        Validate Codex configuration.
        
        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors = []
        codex_config = self.codex
        
        if not codex_config.get("enabled", False):
            return errors
        
        default_executor = codex_config.get("default_executor", "exec")
        valid_executors = ["exec", "app_server", "mcp"]
        if default_executor not in valid_executors:
            errors.append(f"Invalid default_executor '{default_executor}'. Must be one of {valid_executors}")
        
        exec_config = codex_config.get("exec", {})
        
        valid_sandbox_modes = ["read-only", "workspace-write", "danger-full-access"]
        sandbox_mode = exec_config.get("sandbox_mode", "workspace-write")
        if sandbox_mode not in valid_sandbox_modes:
            errors.append(f"Invalid sandbox_mode '{sandbox_mode}'. Must be one of {valid_sandbox_modes}")
        
        valid_approval_policies = ["never", "on-request", "on-failure", "untrusted"]
        approval_policy = exec_config.get("approval_policy", "never")
        if approval_policy not in valid_approval_policies:
            errors.append(f"Invalid approval_policy '{approval_policy}'. Must be one of {valid_approval_policies}")
        
        timeout = exec_config.get("timeout", 300)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append(f"Invalid timeout '{timeout}'. Must be a positive number")
        
        return errors
