"""
End-to-end tests for progress tracking.
"""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest

from cinder_cli.config import Config
from cinder_cli.executor import AutonomousExecutor
from cinder_cli.executor.progress_tracker import ExecutionPhase


@pytest.fixture
def config():
    """Create test configuration."""
    config = Config()
    config.set("progress_tracking", True)
    return config


def test_cli_execution_with_progress(config, tmp_path):
    """Test CLI execution with progress tracking."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor') as MockExecutor:
        executor = MockExecutor.return_value
        
        executor.progress_tracker.start_phase(ExecutionPhase.PLAN)
        executor.progress_tracker.update_phase_progress(50.0)
        
        progress = executor.progress_tracker.get_progress()
        assert progress["current_phase"] == "plan"
        assert progress["phase_progress"]["plan"] == 50.0
        
        executor.progress_tracker.complete_phase(ExecutionPhase.PLAN)
        progress = executor.progress_tracker.get_progress()
        assert progress["phase_progress"]["plan"] == 100.0


def test_progress_broadcasting(config):
    """Test progress broadcasting to listeners."""
    from cinder_cli.executor.progress_broadcaster import ProgressBroadcaster
    
    broadcaster = ProgressBroadcaster()
    listener = Mock()
    
    broadcaster.add_listener(listener)
    broadcaster.broadcast({"progress": 50})
    
    listener.assert_called_once_with({"progress": 50})


def test_time_recording(config):
    """Test time recording for phases and tasks."""
    from cinder_cli.executor.time_recorder import TimeRecorder
    
    recorder = TimeRecorder()
    
    recorder.start_phase("plan")
    time.sleep(0.1)
    recorder.end_phase("plan")
    
    timestamps = recorder.get_phase_timestamps()
    assert "plan" in timestamps
    assert "duration" in timestamps["plan"]
    assert timestamps["plan"]["duration"] >= 0.1


def test_speed_calculation(config):
    """Test speed calculation."""
    from cinder_cli.executor.speed_calculator import SpeedCalculator
    
    calculator = SpeedCalculator()
    
    calculator.start()
    calculator.record_task_completed(10.0)
    calculator.record_task_completed(20.0)
    
    time.sleep(0.1)
    
    speed = calculator.get_tasks_per_minute()
    assert speed > 0
    
    avg_time = calculator.get_average_task_time()
    assert avg_time == 15.0


def test_estimation_engine(config):
    """Test estimation engine."""
    from cinder_cli.executor.estimation_engine import EstimationEngine
    
    engine = EstimationEngine()
    
    estimate, confidence = engine.estimate_initial(tasks_count=5)
    assert estimate > 0
    assert 0 < confidence <= 1
    
    remaining, new_confidence = engine.estimate_remaining(
        elapsed=60.0,
        progress=25.0,
        tasks_completed=1,
        tasks_total=4,
    )
    assert remaining > 0
    assert new_confidence > confidence


def test_database_persistence(config, tmp_path):
    """Test progress data persistence in database."""
    from cinder_cli.executor.execution_logger import ExecutionLogger
    import sqlite3
    
    db_path = tmp_path / "test.db"
    
    with patch('cinder_cli.executor.execution_logger.ExecutionLogger._get_db_path', return_value=db_path):
        logger = ExecutionLogger(config)
        
        execution_id = logger.log_execution(
            goal="Test goal",
            task_tree={"subtasks": []},
            results=[],
            phase_timestamps={"plan": {"duration": 10.0}},
            progress_data={"overall_progress": 100.0},
            speed_metrics={"tasks_per_minute": 5.0},
        )
        
        assert execution_id > 0
        
        execution = logger.get_execution(execution_id)
        assert execution is not None
        assert execution["goal"] == "Test goal"
        assert execution["phase_timestamps"]["plan"]["duration"] == 10.0
        assert execution["progress_data"]["overall_progress"] == 100.0


def test_sse_streaming(config):
    """Test SSE streaming endpoint."""
    from cinder_cli.web.api.progress import stream_execution_progress
    import asyncio
    
    async def test_stream():
        with patch('cinder_cli.web.api.progress.get_logger') as mock_logger:
            mock_execution = {
                "id": 1,
                "status": "success",
                "progress_data": {"overall_progress": 100.0},
                "speed_metrics": {"tasks_per_minute": 5.0},
            }
            
            mock_logger.return_value.get_execution.return_value = mock_execution
            
            response = await stream_execution_progress(1)
            assert response.media_type == "text/event-stream"
    
    asyncio.run(test_stream())


def test_progress_snapshot(config):
    """Test progress snapshot creation."""
    from cinder_cli.executor.progress_snapshot import ProgressSnapshot
    
    snapshot = ProgressSnapshot(
        current_phase="generation",
        overall_progress=50.0,
        elapsed_time=60.0,
        tasks_completed=2,
        tasks_total=4,
        current_task="Task 3",
    )
    
    data = snapshot.to_dict()
    assert data["current_phase"] == "generation"
    assert data["overall_progress"] == 50.0
    
    restored = ProgressSnapshot.from_dict(data)
    assert restored.current_phase == "generation"
    assert restored.overall_progress == 50.0


def test_thread_safety(config):
    """Test thread safety of progress tracking."""
    from cinder_cli.executor.progress_tracker import ProgressTracker
    import threading
    
    tracker = ProgressTracker()
    errors = []
    
    def update_progress():
        try:
            for _ in range(100):
                tracker.update_phase_progress(50.0)
                tracker.get_progress()
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=update_progress) for _ in range(10)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    assert len(errors) == 0


def test_configuration_options(config):
    """Test progress tracking configuration."""
    from cinder_cli.executor.progress_config import ProgressConfig
    
    progress_config = ProgressConfig()
    
    assert progress_config.is_progress_enabled() is True
    assert progress_config.is_estimation_enabled() is True
    assert progress_config.get_update_interval() == 1
    assert progress_config.get_max_sse_connections() == 10
    
    progress_config.set("progress_tracking.enabled", False)
    assert progress_config.is_progress_enabled() is False
