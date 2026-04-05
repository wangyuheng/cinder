"""
Performance tests for progress tracking.
"""

from __future__ import annotations

import time
from unittest.mock import Mock

import pytest

from cinder_cli.executor.progress_tracker import ProgressTracker, ExecutionPhase
from cinder_cli.executor.progress_broadcaster import ProgressBroadcaster
from cinder_cli.executor.time_recorder import TimeRecorder
from cinder_cli.executor.speed_calculator import SpeedCalculator


def test_progress_tracker_performance():
    """Test progress tracker performance overhead."""
    tracker = ProgressTracker()
    
    start_time = time.time()
    
    for _ in range(1000):
        tracker.start_phase(ExecutionPhase.PLAN)
        tracker.update_phase_progress(50.0)
        tracker.get_progress()
        tracker.complete_phase(ExecutionPhase.PLAN)
    
    elapsed = time.time() - start_time
    
    assert elapsed < 1.0, f"Progress tracking took {elapsed:.2f}s for 1000 iterations"
    
    overhead_per_iteration = elapsed / 1000
    print(f"\nProgress tracking overhead: {overhead_per_iteration * 1000:.2f}ms per iteration")


def test_broadcaster_performance():
    """Test broadcaster performance with many listeners."""
    broadcaster = ProgressBroadcaster()
    
    listeners = [Mock() for _ in range(100)]
    for listener in listeners:
        broadcaster.add_listener(listener)
    
    start_time = time.time()
    
    for _ in range(100):
        broadcaster.broadcast({"progress": 50})
    
    elapsed = time.time() - start_time
    
    assert elapsed < 0.5, f"Broadcasting took {elapsed:.2f}s"
    
    for listener in listeners:
        assert listener.call_count == 100


def test_time_recorder_performance():
    """Test time recorder performance."""
    recorder = TimeRecorder()
    
    start_time = time.time()
    
    for i in range(100):
        recorder.start_phase(f"phase_{i}")
        recorder.end_phase(f"phase_{i}")
    
    elapsed = time.time() - start_time
    
    assert elapsed < 0.5, f"Time recording took {elapsed:.2f}s"


def test_speed_calculator_performance():
    """Test speed calculator performance."""
    calculator = SpeedCalculator()
    calculator.start()
    
    start_time = time.time()
    
    for _ in range(1000):
        calculator.record_task_completed(10.0)
        calculator.get_tasks_per_minute()
        calculator.get_average_task_time()
    
    elapsed = time.time() - start_time
    
    assert elapsed < 0.5, f"Speed calculation took {elapsed:.2f}s"


def test_memory_usage():
    """Test memory usage of progress tracking."""
    import sys
    
    tracker = ProgressTracker()
    broadcaster = ProgressBroadcaster()
    recorder = TimeRecorder()
    calculator = SpeedCalculator()
    
    initial_size = (
        sys.getsizeof(tracker) +
        sys.getsizeof(broadcaster) +
        sys.getsizeof(recorder) +
        sys.getsizeof(calculator)
    )
    
    for i in range(100):
        tracker.start_phase(ExecutionPhase.PLAN)
        recorder.start_phase(f"phase_{i}")
        calculator.record_task_completed(10.0)
        broadcaster.broadcast({"progress": i})
    
    final_size = (
        sys.getsizeof(tracker) +
        sys.getsizeof(broadcaster) +
        sys.getsizeof(recorder) +
        sys.getsizeof(calculator)
    )
    
    memory_increase = final_size - initial_size
    
    print(f"\nMemory usage:")
    print(f"  Initial: {initial_size} bytes")
    print(f"  Final: {final_size} bytes")
    print(f"  Increase: {memory_increase} bytes")
    
    assert memory_increase < 10000, f"Memory increased by {memory_increase} bytes"


def test_concurrent_updates():
    """Test concurrent progress updates."""
    import threading
    
    tracker = ProgressTracker()
    errors = []
    
    def update_concurrently():
        try:
            for _ in range(100):
                tracker.update_phase_progress(50.0)
                progress = tracker.get_progress()
                assert "overall_progress" in progress
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=update_concurrently) for _ in range(20)]
    
    start_time = time.time()
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start_time
    
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert elapsed < 2.0, f"Concurrent updates took {elapsed:.2f}s"
    
    print(f"\nConcurrent updates: 2000 operations in {elapsed:.2f}s")


def test_database_write_performance(tmp_path):
    """Test database write performance."""
    from cinder_cli.executor.execution_logger import ExecutionLogger
    from cinder_cli.config import Config
    
    db_path = tmp_path / "test.db"
    config = Config()
    
    import unittest.mock as mock
    with mock.patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
        logger = ExecutionLogger(config)
        
        start_time = time.time()
        
        for i in range(100):
            logger.log_execution(
                goal=f"Test goal {i}",
                task_tree={"subtasks": []},
                results=[],
                phase_timestamps={"plan": {"duration": 10.0}},
                progress_data={"overall_progress": 100.0},
                speed_metrics={"tasks_per_minute": 5.0},
            )
        
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"Database writes took {elapsed:.2f}s"
        
        print(f"\nDatabase writes: 100 executions in {elapsed:.2f}s")
        print(f"  Average: {elapsed / 100 * 1000:.2f}ms per write")


def test_overall_overhead():
    """Test overall progress tracking overhead."""
    tracker = ProgressTracker()
    recorder = TimeRecorder()
    calculator = SpeedCalculator()
    broadcaster = ProgressBroadcaster()
    
    listener = Mock()
    broadcaster.add_listener(listener)
    
    calculator.start()
    
    start_time = time.time()
    
    for i in range(100):
        tracker.start_phase(ExecutionPhase.PLAN)
        recorder.start_phase(f"phase_{i}")
        
        tracker.update_phase_progress(50.0)
        progress = tracker.get_progress()
        broadcaster.broadcast(progress)
        
        calculator.record_task_completed(10.0)
        speed = calculator.get_tasks_per_minute()
        
        recorder.end_phase(f"phase_{i}")
        tracker.complete_phase(ExecutionPhase.PLAN)
    
    elapsed = time.time() - start_time
    
    overhead_per_iteration = elapsed / 100
    
    print(f"\nOverall overhead:")
    print(f"  Total time: {elapsed:.2f}s for 100 iterations")
    print(f"  Per iteration: {overhead_per_iteration * 1000:.2f}ms")
    print(f"  Overhead percentage: {overhead_per_iteration * 100:.2f}%")
    
    assert overhead_per_iteration < 0.05, f"Overhead too high: {overhead_per_iteration * 1000:.2f}ms per iteration"
