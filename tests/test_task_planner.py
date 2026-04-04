"""
Tests for TaskPlanner.
"""

import pytest

from cinder_cli.config import Config
from cinder_cli.executor import TaskPlanner


@pytest.fixture
def planner():
    """Create a task planner instance."""
    config = Config()
    return TaskPlanner(config)


class TestTaskPlanner:
    """Test cases for TaskPlanner."""

    def test_decompose_web_project(self, planner):
        """Test web project decomposition."""
        result = planner.decompose_goal("做个记账web应用")

        assert result["goal"] == "做个记账web应用"
        assert len(result["subtasks"]) >= 3
        assert any(
            "项目" in task["description"] or "前端" in task["description"] or "后端" in task["description"]
            for task in result["subtasks"]
        )

    def test_decompose_api_project(self, planner):
        """Test API project decomposition."""
        result = planner.decompose_goal("创建REST API")

        assert result["goal"] == "创建REST API"
        assert len(result["subtasks"]) >= 2
        assert any("api" in task["description"].lower()
                   for task in result["subtasks"])

    def test_decompose_python_script(self, planner):
        """Test Python script decomposition."""
        result = planner.decompose_goal("创建Python脚本")

        assert result["goal"] == "创建Python脚本"
        assert len(result["subtasks"]) >= 1

    def test_decompose_with_constraints(self, planner):
        """Test decomposition with constraints."""
        result = planner.decompose_goal(
            goal="创建API",
            constraints={"framework": "fastapi"},
        )

        assert result["constraints"]["framework"] == "fastapi"
