"""
Tests for ExecutionLogger.
"""

import pytest
from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


@pytest.fixture
def logger(tmp_path):
    """Create an execution logger instance."""
    config = Config(tmp_path / ".cinder")
    return ExecutionLogger(config)


class TestExecutionLogger:
    """Test cases for ExecutionLogger."""

    def test_log_execution(self, logger):
        """Test logging an execution."""
        execution_id = logger.log_execution(
            goal="测试目标",
            task_tree={"subtasks": []},
            results=[{"status": "success"}],
        )

        assert execution_id is not None
        assert execution_id > 0

    def test_list_executions(self, logger):
        """Test listing executions."""
        logger.log_execution(
            goal="目标1",
            task_tree={},
            results=[],
        )
        logger.log_execution(
            goal="目标2",
            task_tree={},
            results=[],
        )

        executions = logger.list_executions(limit=10)

        assert len(executions) >= 2

    def test_list_executions_with_status_filter(self, logger):
        """Test listing executions with status filter."""
        logger.log_execution(
            goal="成功任务",
            task_tree={},
            results=[{"status": "success"}],
        )

        executions = logger.list_executions(status="success")

        assert all(e["status"] == "success" for e in executions)

    def test_get_execution(self, logger):
        """Test getting a specific execution."""
        execution_id = logger.log_execution(
            goal="特定任务",
            task_tree={"goal": "特定任务"},
            results=[{"task": "test"}],
        )

        execution = logger.get_execution(execution_id)

        assert execution is not None
        assert execution["goal"] == "特定任务"
        assert execution["task_tree"]["goal"] == "特定任务"

    def test_get_nonexistent_execution(self, logger):
        """Test getting a nonexistent execution."""
        execution = logger.get_execution(99999)

        assert execution is None

    def test_execution_has_timestamp(self, logger):
        """Test that execution has timestamp."""
        execution_id = logger.log_execution(
            goal="时间测试",
            task_tree={},
            results=[],
        )

        execution = logger.get_execution(execution_id)

        assert "timestamp" in execution
        assert execution["timestamp"] is not None

    def test_execution_has_created_files(self, logger):
        """Test that execution tracks created files."""
        execution_id = logger.log_execution(
            goal="文件创建测试",
            task_tree={},
            results=[
                {"file_result": {"file_path": "/tmp/test.py"}},
                {"file_result": {"file_path": "/tmp/main.py"}},
            ],
        )

        execution = logger.get_execution(execution_id)

        assert "created_files" in execution
        assert len(execution["created_files"]) == 2

    def test_list_executions_order(self, logger):
        """Test that executions are ordered by timestamp desc."""
        logger.log_execution(goal="第一", task_tree={}, results=[])
        logger.log_execution(goal="第二", task_tree={}, results=[])
        logger.log_execution(goal="第三", task_tree={}, results=[])

        executions = logger.list_executions(limit=10)

        goals = [e["goal"] for e in executions[:3]]
        assert "第三" in goals[0]
