"""
Tests for Web API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from cinder_cli.config import Config
from cinder_cli.web.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    config = Config()
    app = create_app(config)
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns ok."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestExecutionsAPI:
    """Test executions API endpoints."""

    def test_list_executions(self, client):
        """Test listing executions."""
        response = client.get("/api/executions")
        assert response.status_code == 200
        data = response.json()
        assert "executions" in data
        assert "total" in data

    def test_list_executions_with_pagination(self, client):
        """Test listing executions with pagination."""
        response = client.get("/api/executions?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_get_execution_stats(self, client):
        """Test getting execution statistics."""
        response = client.get("/api/executions/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "success_count" in data
        assert "success_rate" in data

    def test_get_nonexistent_execution(self, client):
        """Test getting nonexistent execution."""
        response = client.get("/api/executions/99999")
        assert response.status_code == 404


class TestSoulAPI:
    """Test Soul configuration API endpoints."""

    def test_get_soul(self, client):
        """Test getting Soul configuration."""
        response = client.get("/api/soul")
        assert response.status_code == 200

    def test_init_soul(self, client):
        """Test initializing Soul configuration."""
        response = client.post("/api/soul/init")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "initialized"


class TestDecisionsAPI:
    """Test decisions API endpoints."""

    def test_list_decisions(self, client):
        """Test listing decisions."""
        response = client.get("/api/decisions")
        assert response.status_code == 200
        data = response.json()
        assert "decisions" in data
        assert "total" in data

    def test_get_decision_stats(self, client):
        """Test getting decision statistics."""
        response = client.get("/api/decisions/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data


class TestTasksAPI:
    """Test tasks API endpoints."""

    def test_get_available_modes(self, client):
        """Test getting available execution modes."""
        response = client.get("/api/tasks/modes")
        assert response.status_code == 200
        data = response.json()
        assert "modes" in data
        assert len(data["modes"]) == 3

    def test_trigger_dry_run_task(self, client):
        """Test triggering a dry-run task."""
        response = client.post(
            "/api/tasks",
            json={"goal": "测试目标", "mode": "dry-run"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_trigger_task_invalid_mode(self, client):
        """Test triggering task with invalid mode."""
        response = client.post(
            "/api/tasks",
            json={"goal": "测试目标", "mode": "invalid"},
        )
        assert response.status_code == 400
