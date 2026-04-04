"""
Tests for AutonomousExecutor.
"""

import pytest
from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.executor import AutonomousExecutor


@pytest.fixture
def config(tmp_path):
    """Create a test configuration."""
    config = Config(tmp_path / ".cinder")
    config.set("model", "qwen3.5:9b")
    config.set("temperature", 0.2)
    return config


@pytest.fixture
def executor(config):
    """Create an executor instance."""
    return AutonomousExecutor(config)


class TestAutonomousExecutor:
    """Test cases for AutonomousExecutor."""

    def test_dry_run_mode(self, executor):
        """Test dry-run mode doesn't create files."""
        result = executor.execute(
            goal="创建一个Python脚本",
            mode="dry-run",
        )

        assert result["status"] == "dry-run"
        assert "task_tree" in result
        assert "subtasks" in result["task_tree"]

    def test_execution_with_constraints(self, executor):
        """Test execution with constraints."""
        result = executor.execute(
            goal="创建API",
            mode="dry-run",
            constraints={"framework": "fastapi", "language": "python"},
        )

        assert result["status"] == "dry-run"
        assert result["task_tree"]["constraints"]["framework"] == "fastapi"

    def test_task_decomposition(self, executor):
        """Test task decomposition."""
        result = executor.execute(
            goal="做个记账web应用",
            mode="dry-run",
        )

        subtasks = result["task_tree"]["subtasks"]
        assert len(subtasks) > 0
        assert all("description" in task for task in subtasks)
