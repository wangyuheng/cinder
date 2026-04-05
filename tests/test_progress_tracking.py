"""
Unit tests for progress tracking system.
"""

from __future__ import annotations

import time
from unittest.mock import Mock

import pytest

from cinder_cli.executor.progress_tracker import ProgressTracker, ExecutionPhase
from cinder_cli.executor.progress_broadcaster import ProgressBroadcaster
from cinder_cli.executor.time_recorder import TimeRecorder
from cinder_cli.executor.speed_calculator import SpeedCalculator
from cinder_cli.executor.progress_snapshot import ProgressSnapshot
from cinder_cli.executor.estimation_engine import EstimationEngine


def test_progress_tracker_initial_state():
    """Test ProgressTracker initial state."""
    tracker = ProgressTracker()
    progress = tracker.get_progress()
    
    assert progress["current_phase"] == "plan"
    assert progress["overall_progress"] == 0.0
    assert progress["tasks_total"] == 0
    assert progress["tasks_completed"] == 0


def test_progress_tracker_phase_progression():
    """Test ProgressTracker phase progression."""
    tracker = ProgressTracker()
    
    tracker.start_phase(ExecutionPhase.PLAN)
    tracker.update_phase_progress(50.0)
    progress = tracker.get_progress()
    assert progress["phase_progress"]["plan"] == 50.0
    
    tracker.complete_phase(ExecutionPhase.PLAN)
    progress = tracker.get_progress()
    assert progress["phase_progress"]["plan"] == 100.0


def test_progress_tracker_overall_progress():
    """Test overall progress calculation."""
    tracker = ProgressTracker()
    
    tracker.start_phase(ExecutionPhase.PLAN)
    tracker.complete_phase(ExecutionPhase.PLAN)
    
    tracker.start_phase(ExecutionPhase.GENERATION)
    tracker.update_phase_progress(50.0)
    
    progress = tracker.get_progress()
    assert progress["overall_progress"] > 0
    assert progress["overall_progress"] < 100


def test_progress_broadcaster_registration():
    """Test ProgressBroadcaster listener registration."""
    broadcaster = ProgressBroadcaster()
    
    listener1 = Mock()
    listener2 = Mock()
    
    broadcaster.add_listener(listener1)
    broadcaster.add_listener(listener2)
    
    assert broadcaster.listener_count() == 2


def test_progress_broadcaster_broadcast():
    """Test ProgressBroadcaster broadcast functionality."""
    broadcaster = ProgressBroadcaster()
    
    listener1 = Mock()
    listener2 = Mock()
    
    broadcaster.add_listener(listener1)
    broadcaster.add_listener(listener2)
    
    data = {"progress": 50.0}
    broadcaster.broadcast(data)
    
    listener1.assert_called_once_with(data)
    listener2.assert_called_once_with(data)


def test_time_recorder_phases():
    """Test TimeRecorder phase tracking."""
    recorder = TimeRecorder()
    
    recorder.start_phase("plan")
    time.sleep(0.1)
    recorder.end_phase("plan")
    
    timestamps = recorder.get_phase_timestamps()
    assert "plan" in timestamps
    assert "start" in timestamps["plan"]
    assert "end" in timestamps["plan"]
    assert "duration" in timestamps["plan"]
    assert timestamps["plan"]["duration"] >= 0.1


def test_time_recorder_tasks():
    """Test TimeRecorder task tracking."""
    recorder = TimeRecorder()
    
    recorder.start_task("task1", "First task")
    time.sleep(0.1)
    recorder.end_task("task1")
    
    timestamps = recorder.get_task_timestamps()
    assert "task1" in timestamps
    assert timestamps["task1"]["description"] == "First task"
    assert timestamps["task1"]["duration"] >= 0.1


def test_speed_calculator_tasks_per_minute():
    """Test SpeedCalculator tasks per minute."""
    calculator = SpeedCalculator()
    
    calculator.start()
    calculator.record_task_completed(5.0)
    calculator.record_task_completed(10.0)
    
    time.sleep(0.1)
    
    speed = calculator.get_tasks_per_minute()
    assert speed > 0


def test_speed_calculator_average_task_time():
    """Test SpeedCalculator average task time."""
    calculator = SpeedCalculator()
    
    calculator.record_task_completed(5.0)
    calculator.record_task_completed(15.0)
    
    avg_time = calculator.get_average_task_time()
    assert avg_time == 10.0


def test_progress_snapshot():
    """Test ProgressSnapshot creation and serialization."""
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


def test_estimation_engine_initial_estimate():
    """Test EstimationEngine initial estimation."""
    engine = EstimationEngine()
    
    estimate, confidence = engine.estimate_initial(tasks_count=5)
    
    assert estimate > 0
    assert 0 < confidence <= 1


def test_estimation_engine_dynamic_estimate():
    """Test EstimationEngine dynamic estimation."""
    engine = EstimationEngine()
    
    engine.estimate_initial(tasks_count=10)
    
    remaining, confidence = engine.estimate_remaining(
        elapsed=60.0,
        progress=25.0,
        tasks_completed=2,
        tasks_total=8,
    )
    
    assert remaining > 0
    assert confidence > 0.3


def test_estimation_engine_confidence_interval():
    """Test EstimationEngine confidence interval."""
    engine = EstimationEngine()
    
    lower, upper = engine.get_confidence_interval(estimate=100.0, confidence=0.5)
    
    assert lower < 100.0
    assert upper > 100.0
    assert lower >= 0
