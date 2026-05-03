"""
Integration tests for the onboarding flow.
"""

import pytest
from fastapi.testclient import TestClient

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database
from cinder_cli.database.user_dao import UserDAO
from cinder_cli.web.server import create_app


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(DatabaseConnection, "_db_path", db_path)
    DatabaseConnection._instance = None
    init_database()
    yield
    DatabaseConnection._instance = None
    DatabaseConnection._db_path = None


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app, raise_server_exceptions=False)


class TestInvitationAPI:
    def test_validate_valid_code(self, client, tmp_path):
        import yaml
        config_data = {
            "codes": [
                {"code": "TEST-CODE", "is_single_use": False, "max_uses": 100, "description": "测试邀请码"},
            ]
        }
        config_path = tmp_path / "invitations.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        from cinder_cli.invitation.validator import InvitationValidator
        from cinder_cli.invitation.loader import InvitationLoader
        
        loader = InvitationLoader(config_path)
        validator = InvitationValidator(loader)
        is_valid, message = validator.validate("TEST-CODE")
        
        assert is_valid is True

    def test_validate_invalid_code(self, client):
        response = client.post("/api/invitations/validate", json={"code": "INVALID"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["message"] == "邀请码无效"


class TestUserAPI:
    def test_create_user(self, client):
        response = client.post("/api/users", json={"name": "测试用户"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试用户"
        assert data["id"] is not None
        assert data["onboarding_completed"] is False

    def test_create_user_empty_name(self, client):
        response = client.post("/api/users", json={"name": ""})
        assert response.status_code == 422

    def test_create_user_long_name(self, client):
        response = client.post("/api/users", json={"name": "x" * 51})
        assert response.status_code == 422

    def test_get_current_user(self, client):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        response = client.get(f"/api/users/me?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试用户"


class TestQuestionnaireAPI:
    def test_get_questionnaire(self, client):
        response = client.get("/api/soul/questionnaire")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 6
        assert data[0]["key"] == "q1"
        assert len(data[0]["options"]) == 4

    def test_submit_answer(self, client):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        response = client.post("/api/soul/questionnaire", json={
            "user_id": user_id,
            "question_key": "q1",
            "choice": "A",
            "reason": "测试原因",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["question_key"] == "q1"
        assert data["choice"] == "A"

    def test_get_progress(self, client):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        client.post("/api/soul/questionnaire", json={
            "user_id": user_id,
            "question_key": "q1",
            "choice": "A",
        })
        
        response = client.get(f"/api/soul/questionnaire/progress?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == 1
        assert data["total"] == 6

    def test_clear_progress(self, client):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        client.post("/api/soul/questionnaire", json={
            "user_id": user_id,
            "question_key": "q1",
            "choice": "A",
        })
        
        response = client.delete(f"/api/soul/questionnaire/progress?user_id={user_id}")
        assert response.status_code == 200

    def test_complete_questionnaire(self, client, tmp_path):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        answers = [
            ("q1", "A"), ("q2", "B"), ("q3", "C"),
            ("q4", "D"), ("q5", "A"), ("q6", "B"),
        ]
        
        for key, choice in answers:
            client.post("/api/soul/questionnaire", json={
                "user_id": user_id,
                "question_key": key,
                "choice": choice,
            })
        
        response = client.post(f"/api/soul/questionnaire/complete?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "traits" in data

    def test_complete_questionnaire_incomplete(self, client):
        create_resp = client.post("/api/users", json={"name": "测试用户"})
        user_id = create_resp.json()["id"]
        
        client.post("/api/soul/questionnaire", json={
            "user_id": user_id,
            "question_key": "q1",
            "choice": "A",
        })
        
        response = client.post(f"/api/soul/questionnaire/complete?user_id={user_id}")
        assert response.status_code == 400


class TestOnboardingFlow:
    def test_full_onboarding_flow(self, client, tmp_path):
        import yaml
        config_data = {
            "codes": [
                {"code": "ONBOARD-TEST", "is_single_use": False, "max_uses": 100, "description": "测试邀请码"},
            ]
        }
        config_path = tmp_path / "invitations.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        from cinder_cli.invitation.validator import InvitationValidator
        from cinder_cli.invitation.loader import InvitationLoader
        loader = InvitationLoader(config_path)
        validator = InvitationValidator(loader)
        
        is_valid, _ = validator.validate("ONBOARD-TEST")
        assert is_valid is True
        
        create_resp = client.post("/api/users", json={"name": "完整流程用户"})
        user_id = create_resp.json()["id"]
        
        answers = [
            ("q1", "B"), ("q2", "C"), ("q3", "A"),
            ("q4", "D"), ("q5", "C"), ("q6", "A"),
        ]
        
        for key, choice in answers:
            resp = client.post("/api/soul/questionnaire", json={
                "user_id": user_id,
                "question_key": key,
                "choice": choice,
            })
            assert resp.status_code == 200
        
        complete_resp = client.post(f"/api/soul/questionnaire/complete?user_id={user_id}")
        assert complete_resp.status_code == 200
        data = complete_resp.json()
        assert data["status"] == "completed"
        assert "traits" in data
        
        user_dao = UserDAO()
        user = user_dao.get_by_id(user_id)
        assert user.onboarding_completed is True
