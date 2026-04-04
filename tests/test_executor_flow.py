"""
Tests for executor flow refactoring.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from cinder_cli.config import Config
from cinder_cli.executor.autonomous_executor import AutonomousExecutor


class TestExecutorFlow:
    """Test suite for executor flow refactoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_execute_plan_phase(self, mock_init):
        """Test Plan phase execution."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.task_planner = Mock()
        executor.task_planner.decompose_goal_with_validation = Mock(return_value={
            "subtasks": [{"id": "1", "description": "Task 1"}],
            "validation": {"quality_score": 0.85},
            "attempts": 1
        })

        progress = Mock()
        task = Mock()

        result = executor._execute_plan_phase("Test goal", None, progress, task)

        assert result["phase"] == "plan"
        assert result["success"] is True
        assert "plan" in result
        assert result["quality_score"] == 0.85

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_execute_generation_phase(self, mock_init):
        """Test Generation phase execution."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.code_generator = Mock()
        executor.code_generator.generate_with_iterations = Mock(return_value={
            "code": "print('hello')",
            "iterations": 2,
            "final_score": 0.82,
            "quality_threshold_met": True
        })

        plan = {
            "subtasks": [
                {"id": "1", "description": "Task 1", "language": "python"}
            ]
        }

        progress = Mock()
        task = Mock()

        results = executor._execute_generation_phase(plan, progress, task)

        assert len(results) == 1
        assert results[0]["phase"] == "generation"
        assert results[0]["iterations"] == 2
        assert results[0]["quality_threshold_met"] is True

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_execute_evaluation_phase(self, mock_init):
        """Test Evaluation phase execution."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.reflection_engine = Mock()
        executor.reflection_engine.evaluate_comprehensive = Mock(return_value={
            "quality_score": 0.82,
            "approved": True
        })
        executor.soul_meta = {}

        generation_results = [
            {
                "subtask_id": "1",
                "code": "print('hello')",
                "subtask": {"description": "Task 1"}
            }
        ]

        progress = Mock()
        task = Mock()

        result = executor._execute_evaluation_phase(generation_results, progress, task)

        assert result["phase"] == "evaluation"
        assert result["all_approved"] is True
        assert len(result["evaluations"]) == 1

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_execute_decision_phase(self, mock_init):
        """Test Decision phase execution."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.soul_meta = {}
        executor._make_proxy_decision = Mock(return_value={"text": "接受代码"})

        evaluation_result = {
            "evaluations": [
                {
                    "subtask_id": "1",
                    "evaluation": {"quality_score": 0.82, "approved": True}
                }
            ]
        }

        progress = Mock()
        task = Mock()

        result = executor._execute_decision_phase(evaluation_result, progress, task)

        assert result["phase"] == "decision"
        assert result["accepted_count"] >= 0
        assert len(result["decisions"]) == 1

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_create_failure_result(self, mock_init):
        """Test failure result creation."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)

        result = executor._create_failure_result(
            "Test goal",
            "Plan failed",
            {"phases": []}
        )

        assert result["status"] == "failed"
        assert result["goal"] == "Test goal"
        assert result["reason"] == "Plan failed"

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_phase_completion_verification(self, mock_init):
        """Test phase completion verification."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.task_planner = Mock()
        executor.task_planner.decompose_goal_with_validation = Mock(return_value={
            "subtasks": [],
            "validation": {"quality_score": 0.5},
            "attempts": 2
        })

        progress = Mock()
        task = Mock()

        result = executor._execute_plan_phase("Test goal", None, progress, task)

        assert result["success"] is False
        assert result["quality_score"] < 0.7

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_quality_threshold_enforcement(self, mock_init):
        """Test quality threshold enforcement."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.code_generator = Mock()
        executor.code_generator.generate_with_iterations = Mock(return_value={
            "code": "bad code",
            "iterations": 3,
            "final_score": 0.5,
            "quality_threshold_met": False
        })

        plan = {
            "subtasks": [
                {"id": "1", "description": "Task 1", "language": "python"}
            ]
        }

        progress = Mock()
        task = Mock()

        results = executor._execute_generation_phase(plan, progress, task)

        assert results[0]["quality_threshold_met"] is False
        assert results[0]["final_score"] < 0.8

    @patch('cinder_cli.executor.autonomous_executor.AutonomousExecutor.__init__')
    def test_execution_flow_tracking(self, mock_init):
        """Test execution flow tracking."""
        mock_init.return_value = None
        
        executor = AutonomousExecutor(self.config)
        executor.task_planner = Mock()
        executor.task_planner.decompose_goal_with_validation = Mock(return_value={
            "subtasks": [],
            "validation": {"quality_score": 0.5},
            "attempts": 1
        })

        progress = Mock()
        task = Mock()

        result = executor._execute_plan_phase("Test goal", None, progress, task)

        assert "phase" in result
        assert "success" in result
        assert "quality_score" in result
