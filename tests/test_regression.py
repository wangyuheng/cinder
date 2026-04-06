"""
Regression tests to ensure existing functionality is not affected by progress tracking.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from cinder_cli.config import Config
from cinder_cli.executor import AutonomousExecutor, ExecutionLogger
from cinder_cli.executor.autonomous_executor import ExecutionPhase


def test_executor_basic_functionality_unchanged():
    """Test that basic executor functionality remains unchanged."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config.project_root = Path(tmpdir)
        
        executor = AutonomousExecutor(config)
        
        assert hasattr(executor, 'execute')
        assert hasattr(executor, 'goal')
        assert hasattr(executor, 'config')
        
        assert executor.config == config


def test_execution_logger_backward_compatibility():
    """Test that ExecutionLogger maintains backward compatibility."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=[],
            )
            
            assert execution_id is not None
            assert isinstance(execution_id, int)
            
            execution = logger.get_execution(execution_id)
            assert execution is not None
            assert execution["goal"] == "Test goal"
            assert execution["status"] == "pending"


def test_execution_logger_with_new_fields():
    """Test that ExecutionLogger works with new progress fields."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test with progress",
                task_tree={"subtasks": []},
                results=[],
                phase_timestamps={
                    "plan": {"start": "2026-04-04T20:00:00", "end": "2026-04-04T20:00:10", "duration": 10.0}
                },
                progress_data={
                    "overall_progress": 50.0,
                    "current_phase": "generation",
                },
                speed_metrics={
                    "tasks_per_minute": 5.0,
                    "average_task_time": 12.0,
                },
            )
            
            execution = logger.get_execution(execution_id)
            
            assert execution["phase_timestamps"] is not None
            assert execution["progress_data"] is not None
            assert execution["speed_metrics"] is not None


def test_execution_logger_without_new_fields():
    """Test that ExecutionLogger works without new progress fields (backward compatibility)."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test without progress",
                task_tree={"subtasks": []},
                results=[],
            )
            
            execution = logger.get_execution(execution_id)
            
            assert execution["goal"] == "Test without progress"
            assert execution.get("phase_timestamps") is None or execution.get("phase_timestamps") == {}


def test_config_backward_compatibility():
    """Test that Config maintains backward compatibility."""
    config = Config()
    
    assert hasattr(config, 'project_root')
    assert hasattr(config, 'db_path')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config.project_root = Path(tmpdir)
        
        assert config.project_root == Path(tmpdir)


def test_executor_without_progress_tracking():
    """Test that executor works correctly when progress tracking is disabled."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config.project_root = Path(tmpdir)
        
        if hasattr(config, 'enable_progress_tracking'):
            config.enable_progress_tracking = False
        
        executor = AutonomousExecutor(config)
        
        assert executor.config == config


def test_database_schema_compatibility():
    """Test that database schema is backward compatible."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(executions)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            assert 'id' in columns
            assert 'goal' in columns
            assert 'task_tree' in columns
            assert 'results' in columns
            assert 'status' in columns
            assert 'timestamp' in columns
            
            conn.close()


def test_execution_list_functionality():
    """Test that execution listing still works correctly."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            for i in range(5):
                logger.log_execution(
                    goal=f"Test goal {i}",
                    task_tree={"subtasks": []},
                    results=[],
                )
            
            executions = logger.list_executions(limit=10)
            
            assert len(executions) == 5
            assert all("goal" in e for e in executions)


def test_execution_status_updates():
    """Test that execution status updates still work correctly."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=[],
            )
            
            logger.update_execution_status(execution_id, "success")
            
            execution = logger.get_execution(execution_id)
            assert execution["status"] == "success"


def test_file_creation_tracking():
    """Test that file creation tracking still works correctly."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=[],
                created_files=["file1.py", "file2.py"],
            )
            
            execution = logger.get_execution(execution_id)
            assert len(execution["created_files"]) == 2
            assert "file1.py" in execution["created_files"]


def test_task_tree_storage():
    """Test that task tree storage still works correctly."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            task_tree = {
                "id": 1,
                "description": "Root task",
                "subtasks": [
                    {"id": 2, "description": "Subtask 1"},
                    {"id": 3, "description": "Subtask 2"},
                ]
            }
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree=task_tree,
                results=[],
            )
            
            execution = logger.get_execution(execution_id)
            assert execution["task_tree"]["id"] == 1
            assert len(execution["task_tree"]["subtasks"]) == 2


def test_results_storage():
    """Test that results storage still works correctly."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            results = [
                {"task_id": 1, "status": "success", "output": "Output 1"},
                {"task_id": 2, "status": "success", "output": "Output 2"},
            ]
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=results,
            )
            
            execution = logger.get_execution(execution_id)
            assert len(execution["results"]) == 2


def test_progress_tracking_optional():
    """Test that progress tracking is optional and doesn't break existing code."""
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=[],
            )
            
            execution = logger.get_execution(execution_id)
            
            assert execution["goal"] == "Test goal"
            assert execution["status"] == "pending"
            
            assert execution.get("phase_timestamps") is None or execution.get("phase_timestamps") == {}
            assert execution.get("progress_data") is None or execution.get("progress_data") == {}
            assert execution.get("speed_metrics") is None or execution.get("speed_metrics") == {}


def test_web_api_backward_compatibility():
    """Test that Web API maintains backward compatibility."""
    from cinder_cli.web.api.executions import list_executions, get_execution
    
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree={"subtasks": []},
                results=[],
            )
            
            import asyncio
            
            async def test_api():
                result = await get_execution(execution_id)
                assert result["goal"] == "Test goal"
                
                list_result = await list_executions(limit=10)
                assert len(list_result["executions"]) == 1
            
            asyncio.run(test_api())


def test_cli_backward_compatibility():
    """Test that CLI commands maintain backward compatibility."""
    from click.testing import CliRunner
    from cinder_cli.cli import cli
    
    runner = CliRunner()
    
    result = runner.invoke(cli, ['--help'])
    
    assert result.exit_code == 0
    assert 'Usage:' in result.output or 'help' in result.output.lower()
