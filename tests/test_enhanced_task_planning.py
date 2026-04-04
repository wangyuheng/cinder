"""
Tests for enhanced task planning features.
"""

import pytest
from cinder_cli.config import Config
from cinder_cli.executor.task_planner import TaskPlanner


class TestEnhancedTaskPlanning:
    """Test suite for enhanced task planning."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.planner = TaskPlanner(self.config)

    def test_understand_goal_with_llm(self):
        """Test LLM-based goal understanding."""
        goal = "创建一个Web应用"
        result = self.planner.understand_goal_with_llm(goal)

        assert "goal" in result
        assert "success" in result
        assert result["goal"] == goal

    def test_decompose_goal_with_llm(self):
        """Test plan generation with LLM understanding."""
        goal = "创建一个简单的Python脚本"
        result = self.planner.decompose_goal_with_llm(goal)

        assert "goal" in result
        assert "subtasks" in result
        assert len(result["subtasks"]) > 0
        assert "dependency_graph" in result
        assert "complexity" in result

    def test_validate_plan(self):
        """Test plan validation and quality scoring."""
        plan = {
            "goal": "Test goal",
            "subtasks": [
                {
                    "id": "1",
                    "description": "Task 1",
                    "type": "code",
                    "language": "python",
                    "file_path": "test.py",
                }
            ],
        }

        result = self.planner.validate_plan(plan)

        assert "valid" in result
        assert "quality_score" in result
        assert "completeness" in result
        assert "feasibility" in result
        assert "dependency_correctness" in result
        assert 0 <= result["quality_score"] <= 1

    def test_decompose_goal_with_validation(self):
        """Test plan generation with validation."""
        goal = "创建一个简单的API"
        result = self.planner.decompose_goal_with_validation(
            goal, max_retries=1, quality_threshold=0.5
        )

        assert "subtasks" in result
        assert "validation" in result
        assert "attempts" in result
        assert result["attempts"] >= 1

    def test_build_dependency_graph(self):
        """Test dependency graph building."""
        subtasks = [
            {"id": "1", "description": "Task 1", "type": "code"},
            {"id": "2", "description": "Task 2", "type": "code", "dependencies": ["1"]},
        ]

        graph = self.planner.build_dependency_graph(subtasks)

        assert "nodes" in graph
        assert "edges" in graph
        assert "execution_order" in graph
        assert len(graph["nodes"]) == 2

    def test_estimate_complexity(self):
        """Test complexity estimation."""
        subtasks = [
            {"id": "1", "description": "Task 1", "type": "code", "language": "python"},
            {"id": "2", "description": "Task 2", "type": "setup", "language": "python"},
        ]

        complexity = self.planner.estimate_complexity(subtasks)

        assert "total" in complexity
        assert "average" in complexity
        assert "task_count" in complexity
        assert complexity["task_count"] == 2

    def test_check_circular_dependencies(self):
        """Test circular dependency detection."""
        subtasks_no_cycle = [
            {"id": "1", "description": "Task 1", "dependencies": []},
            {"id": "2", "description": "Task 2", "dependencies": ["1"]},
        ]

        result = self.planner._check_dependency_correctness(subtasks_no_cycle)
        assert not result.get("has_circular_deps", False)

    def test_plan_regeneration_on_low_quality(self):
        """Test plan regeneration when quality is low."""
        goal = "测试低质量计划"
        result = self.planner.decompose_goal_with_validation(
            goal, max_retries=2, quality_threshold=0.9
        )

        assert "attempts" in result
        assert result["attempts"] <= 3
