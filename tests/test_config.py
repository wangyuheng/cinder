"""
Tests for configuration management.
"""

import tempfile
from pathlib import Path

import pytest

from cinder_cli.config import Config


class TestConfig:
    """Test cases for Config."""

    @pytest.fixture
    def config(self):
        """Create a temporary config for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Config(Path(tmpdir))

    def test_default_config(self, config):
        """Test default configuration values."""
        assert config.get("backend") == "ollama"
        assert config.get("model") == "qwen3.5:9b"
        assert config.get("temperature") == 0.2

    def test_set_and_get(self, config):
        """Test setting and getting values."""
        config.set("backend", "claude")
        assert config.get("backend") == "claude"

    def test_update(self, config):
        """Test updating multiple values."""
        config.update({
            "backend": "claude",
            "temperature": 0.5,
        })

        assert config.get("backend") == "claude"
        assert config.get("temperature") == 0.5

    def test_reset(self, config):
        """Test resetting to defaults."""
        config.set("backend", "claude")
        config.reset()

        assert config.get("backend") == "ollama"

    def test_database_path(self, config):
        """Test database path property."""
        db_path = config.database_path
        assert db_path.name == "decisions.db"
        assert db_path.parent.name == ".cinder"
