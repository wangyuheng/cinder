"""
Stress tests for long-running executions.
"""

from __future__ import annotations

import time
import threading
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from cinder_cli.executor.progress_tracker import ProgressTracker, ExecutionPhase
from cinder_cli.executor.progress_broadcaster import ProgressBroadcaster
from cinder_cli.executor.time_recorder import TimeRecorder
from cinder_cli.executor.speed_calculator import SpeedCalculator
from cinder_cli.executor.execution_logger import ExecutionLogger
from cinder_cli.config import Config


def test_long_running_execution_simulation():
    """Test progress tracking during a simulated long-running execution."""
    tracker = ProgressTracker()
    recorder = TimeRecorder()
    calculator = SpeedCalculator()
    broadcaster = ProgressBroadcaster()
    
    calculator.start()
    
    listener = Mock()
    broadcaster.add_listener(listener)
    
    start_time = time.time()
    
    phases = [
        ExecutionPhase.PLAN,
        ExecutionPhase.GENERATION,
        ExecutionPhase.EVALUATION,
        ExecutionPhase.DECISION,
    ]
    
    for iteration in range(50):
        for phase in phases:
            tracker.start_phase(phase)
            recorder.start_phase(f"{phase.value}_{iteration}")
            
            for task_num in range(10):
                tracker.update_phase_progress(task_num * 10)
                calculator.record_task_completed(time.time())
                progress = tracker.get_progress()
                broadcaster.broadcast(progress)
                
                time.sleep(0.001)
            
            recorder.end_phase(f"{phase.value}_{iteration}")
            tracker.complete_phase(phase)
    
    elapsed = time.time() - start_time
    
    assert elapsed < 30.0, f"Long-running execution took too long: {elapsed:.2f}s"
    assert listener.call_count > 0, "No progress updates were broadcast"
    
    print(f"\nLong-running execution simulation:")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"  Iterations: 50")
    print(f"  Tasks per iteration: 10")
    print(f"  Total tasks: 500")
    print(f"  Broadcasts: {listener.call_count}")


def test_memory_stability_long_running():
    """Test memory stability during long-running execution."""
    import gc
    import sys
    
    tracker = ProgressTracker()
    recorder = TimeRecorder()
    calculator = SpeedCalculator()
    broadcaster = ProgressBroadcaster()
    
    calculator.start()
    
    initial_objects = len(gc.get_objects())
    
    for iteration in range(100):
        tracker.start_phase(ExecutionPhase.GENERATION)
        recorder.start_phase(f"phase_{iteration}")
        
        for _ in range(10):
            tracker.update_phase_progress(50.0)
            calculator.record_task_completed(time.time())
            broadcaster.broadcast(tracker.get_progress())
        
        recorder.end_phase(f"phase_{iteration}")
        tracker.complete_phase(ExecutionPhase.GENERATION)
        
        if iteration % 20 == 0:
            gc.collect()
    
    final_objects = len(gc.get_objects())
    object_increase = final_objects - initial_objects
    
    print(f"\nMemory stability test:")
    print(f"  Initial objects: {initial_objects}")
    print(f"  Final objects: {final_objects}")
    print(f"  Object increase: {object_increase}")
    
    assert object_increase < 1000, f"Memory leak detected: {object_increase} objects created"


def test_database_stress_long_running(tmp_path):
    """Test database performance under long-running stress."""
    db_path = tmp_path / "stress_test.db"
    config = Config()
    
    with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
        logger = ExecutionLogger(config)
        
        start_time = time.time()
        
        for i in range(500):
            logger.log_execution(
                goal=f"Stress test goal {i}",
                task_tree={"subtasks": []},
                results=[],
                phase_timestamps={
                    "plan": {"duration": 10.0},
                    "generation": {"duration": 100.0},
                    "evaluation": {"duration": 50.0},
                },
                progress_data={
                    "overall_progress": 100.0,
                    "current_phase": "decision",
                    "elapsed_time": 160.0,
                },
                speed_metrics={
                    "tasks_per_minute": 5.0,
                    "average_task_time": 12.0,
                },
            )
        
        elapsed = time.time() - start_time
        
        assert elapsed < 30.0, f"Database stress test took too long: {elapsed:.2f}s"
        
        print(f"\nDatabase stress test:")
        print(f"  Executions logged: 500")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Average per execution: {elapsed / 500 * 1000:.2f}ms")


def test_concurrent_long_running_executions():
    """Test multiple concurrent long-running executions."""
    num_executions = 10
    tasks_per_execution = 50
    
    def simulate_execution(execution_id):
        tracker = ProgressTracker()
        calculator = SpeedCalculator()
        calculator.start()
        
        for task_num in range(tasks_per_execution):
            tracker.start_phase(ExecutionPhase.GENERATION)
            tracker.update_phase_progress(task_num * 2)
            calculator.record_task_completed(time.time())
            tracker.complete_phase(ExecutionPhase.GENERATION)
            time.sleep(0.001)
        
        return execution_id
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_executions) as executor:
        futures = [executor.submit(simulate_execution, i) for i in range(num_executions)]
        results = [future.result() for future in as_completed(futures)]
    
    elapsed = time.time() - start_time
    
    assert len(results) == num_executions, "Not all executions completed"
    assert elapsed < 20.0, f"Concurrent executions took too long: {elapsed:.2f}s"
    
    print(f"\nConcurrent long-running executions:")
    print(f"  Concurrent executions: {num_executions}")
    print(f"  Tasks per execution: {tasks_per_execution}")
    print(f"  Total tasks: {num_executions * tasks_per_execution}")
    print(f"  Total time: {elapsed:.2f}s")


def test_broadcaster_stress_many_listeners():
    """Test broadcaster with many listeners over long period."""
    broadcaster = ProgressBroadcaster()
    
    num_listeners = 200
    listeners = [Mock() for _ in range(num_listeners)]
    
    for listener in listeners:
        broadcaster.add_listener(listener)
    
    start_time = time.time()
    
    for i in range(1000):
        broadcaster.broadcast({
            "progress": i / 10,
            "phase": "generation",
            "timestamp": time.time(),
        })
    
    elapsed = time.time() - start_time
    
    for listener in listeners:
        assert listener.call_count == 1000, "Not all broadcasts received"
    
    print(f"\nBroadcaster stress test:")
    print(f"  Listeners: {num_listeners}")
    print(f"  Broadcasts: 1000")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Broadcasts per second: {1000 / elapsed:.2f}")


def test_speed_calculator_long_running():
    """Test speed calculator over extended period."""
    calculator = SpeedCalculator()
    calculator.start()
    
    start_time = time.time()
    
    for i in range(1000):
        calculator.record_task_completed(time.time())
        
        if i % 100 == 0:
            speed = calculator.get_tasks_per_minute()
            avg_time = calculator.get_average_task_time()
            assert speed > 0, "Speed should be positive"
            assert avg_time > 0, "Average time should be positive"
    
    elapsed = time.time() - start_time
    
    final_speed = calculator.get_tasks_per_minute()
    final_avg_time = calculator.get_average_task_time()
    
    assert final_speed > 0, "Final speed should be positive"
    assert final_avg_time > 0, "Final average time should be positive"
    
    print(f"\nSpeed calculator long-running test:")
    print(f"  Tasks recorded: 1000")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Final speed: {final_speed:.2f} tasks/min")
    print(f"  Final avg time: {final_avg_time:.2f}s")


def test_time_recorder_extended_usage():
    """Test time recorder with extended usage."""
    recorder = TimeRecorder()
    
    start_time = time.time()
    
    for i in range(200):
        phase_name = f"phase_{i % 10}"
        recorder.start_phase(phase_name)
        time.sleep(0.001)
        recorder.end_phase(phase_name)
    
    elapsed = time.time() - start_time
    
    phase_durations = recorder.get_all_phase_durations()
    
    assert len(phase_durations) > 0, "No phase durations recorded"
    
    for phase_name, durations in phase_durations.items():
        assert len(durations) > 0, f"No durations for phase {phase_name}"
        assert all(d > 0 for d in durations), f"Invalid durations for phase {phase_name}"
    
    print(f"\nTime recorder extended usage:")
    print(f"  Phases recorded: 200")
    print(f"  Unique phases: {len(phase_durations)}")
    print(f"  Total time: {elapsed:.2f}s")


def test_progress_tracker_state_persistence():
    """Test progress tracker state over extended operations."""
    tracker = ProgressTracker()
    
    for iteration in range(100):
        tracker.start_phase(ExecutionPhase.PLAN)
        tracker.update_phase_progress(50.0)
        tracker.complete_phase(ExecutionPhase.PLAN)
        
        tracker.start_phase(ExecutionPhase.GENERATION)
        for task in range(20):
            tracker.update_phase_progress(task * 5)
        tracker.complete_phase(ExecutionPhase.GENERATION)
        
        progress = tracker.get_progress()
        assert "overall_progress" in progress, "Progress data missing"
        assert progress["overall_progress"] >= 0, "Invalid progress value"
    
    final_progress = tracker.get_progress()
    
    print(f"\nProgress tracker state persistence:")
    print(f"  Iterations: 100")
    print(f"  Final progress: {final_progress.get('overall_progress', 0):.2f}%")


def test_endurance_test():
    """Endurance test running for extended period."""
    tracker = ProgressTracker()
    recorder = TimeRecorder()
    calculator = SpeedCalculator()
    broadcaster = ProgressBroadcaster()
    
    calculator.start()
    
    listener = Mock()
    broadcaster.add_listener(listener)
    
    start_time = time.time()
    iteration = 0
    max_duration = 10
    
    while time.time() - start_time < max_duration:
        tracker.start_phase(ExecutionPhase.GENERATION)
        recorder.start_phase(f"phase_{iteration}")
        
        tracker.update_phase_progress(50.0)
        calculator.record_task_completed(time.time())
        broadcaster.broadcast(tracker.get_progress())
        
        recorder.end_phase(f"phase_{iteration}")
        tracker.complete_phase(ExecutionPhase.GENERATION)
        
        iteration += 1
        time.sleep(0.01)
    
    elapsed = time.time() - start_time
    
    print(f"\nEndurance test:")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"  Iterations: {iteration}")
    print(f"  Iterations per second: {iteration / elapsed:.2f}")
    print(f"  Total broadcasts: {listener.call_count}")
    
    assert iteration > 100, f"Too few iterations in {max_duration}s: {iteration}"
    assert listener.call_count > 0, "No broadcasts occurred"
