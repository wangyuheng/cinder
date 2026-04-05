"""
Unit tests for CodexExecutor.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cinder_cli.executor.codex_executor import (
    CodexExecExecutor,
    CodexTask,
    CodexResult,
)
from cinder_cli.executor.codex_exceptions import (
    CodexError,
    CodexNotInstalledError,
    CodexTimeoutError,
    CodexExecutionError,
)


class TestCodexTask:
    """Test CodexTask dataclass."""
    
    def test_task_creation_minimal(self):
        """Test creating a task with minimal parameters."""
        task = CodexTask(description="Test task")
        
        assert task.description == "Test task"
        assert task.model is None
        assert task.sandbox_mode is None
        assert task.timeout == 300
        assert task.skip_git_repo_check is True
        assert task.ephemeral is True
    
    def test_task_creation_full(self):
        """Test creating a task with all parameters."""
        task = CodexTask(
            description="Test task",
            model="gpt-5.4",
            sandbox_mode="workspace-write",
            approval_policy="never",
            full_auto=True,
            output_schema={"type": "object"},
            cwd=Path("/tmp"),
            timeout=600,
            skip_git_repo_check=False,
            ephemeral=False,
        )
        
        assert task.description == "Test task"
        assert task.model == "gpt-5.4"
        assert task.sandbox_mode == "workspace-write"
        assert task.approval_policy == "never"
        assert task.full_auto is True
        assert task.output_schema == {"type": "object"}
        assert task.cwd == Path("/tmp")
        assert task.timeout == 600
        assert task.skip_git_repo_check is False
        assert task.ephemeral is False


class TestCodexResult:
    """Test CodexResult dataclass."""
    
    def test_result_success(self):
        """Test creating a successful result."""
        result = CodexResult(
            success=True,
            output="Test output",
            exit_code=0,
        )
        
        assert result.success is True
        assert result.output == "Test output"
        assert result.error is None
        assert result.exit_code == 0
    
    def test_result_failure(self):
        """Test creating a failed result."""
        result = CodexResult(
            success=False,
            output="",
            error="Test error",
            exit_code=1,
        )
        
        assert result.success is False
        assert result.output == ""
        assert result.error == "Test error"
        assert result.exit_code == 1


class TestCodexExecExecutor:
    """Test CodexExecExecutor class."""
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_init_codex_not_installed(self, mock_is_installed):
        """Test initialization when Codex is not installed."""
        mock_is_installed.return_value = False
        
        with pytest.raises(RuntimeError, match="Codex CLI is not installed"):
            CodexExecExecutor()
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_init_success(self, mock_is_installed):
        """Test successful initialization."""
        mock_is_installed.return_value = True
        
        executor = CodexExecExecutor()
        assert executor is not None
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    @patch('cinder_cli.executor.codex_executor.subprocess.run')
    def test_execute_success(self, mock_run, mock_is_installed):
        """Test successful execution."""
        mock_is_installed.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"text": "Generated code"}',
            stderr=""
        )
        
        executor = CodexExecExecutor()
        task = CodexTask(description="Test task")
        result = executor.execute(task)
        
        assert result.success is True
        assert result.exit_code == 0
        mock_run.assert_called_once()
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    @patch('cinder_cli.executor.codex_executor.subprocess.run')
    def test_execute_timeout(self, mock_run, mock_is_installed):
        """Test execution timeout."""
        mock_is_installed.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="codex", timeout=60)
        
        executor = CodexExecExecutor()
        task = CodexTask(description="Test task", timeout=60)
        result = executor.execute(task)
        
        assert result.success is False
        assert "timed out" in result.error.lower()
        assert result.exit_code == -1
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_build_command_minimal(self, mock_is_installed):
        """Test building command with minimal options."""
        mock_is_installed.return_value = True
        
        executor = CodexExecExecutor()
        task = CodexTask(description="Test task")
        cmd = executor._build_command(task)
        
        assert "codex" in cmd
        assert "exec" in cmd
        assert "--json" in cmd
        assert "--skip-git-repo-check" in cmd
        assert "--ephemeral" in cmd
        assert "Test task" in cmd
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_build_command_full(self, mock_is_installed):
        """Test building command with all options."""
        mock_is_installed.return_value = True
        
        executor = CodexExecExecutor()
        task = CodexTask(
            description="Test task",
            model="gpt-5.4",
            sandbox_mode="workspace-write",
            full_auto=True,
        )
        cmd = executor._build_command(task)
        
        assert "--model" in cmd
        assert "gpt-5.4" in cmd
        assert "--sandbox" in cmd
        assert "workspace-write" in cmd
        assert "--full-auto" in cmd
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_parse_jsonl_output(self, mock_is_installed):
        """Test parsing JSONL output."""
        mock_is_installed.return_value = True
        
        executor = CodexExecExecutor()
        
        jsonl_output = '{"text": "Line 1"}\n{"content": "Line 2"}\n{"message": "Line 3"}'
        parsed = executor._parse_jsonl_output(jsonl_output)
        
        assert "Line 1" in parsed
        assert "Line 2" in parsed
        assert "Line 3" in parsed
    
    @patch('cinder_cli.executor.codex_executor.is_codex_installed')
    def test_parse_jsonl_output_invalid(self, mock_is_installed):
        """Test parsing invalid JSONL output."""
        mock_is_installed.return_value = True
        
        executor = CodexExecExecutor()
        
        invalid_output = "Not JSON\nAnother line"
        parsed = executor._parse_jsonl_output(invalid_output)
        
        assert "Not JSON" in parsed
        assert "Another line" in parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
