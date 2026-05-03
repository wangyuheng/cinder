"""
Tests for onboarding database operations.
"""

import tempfile
from pathlib import Path

import pytest

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database
from cinder_cli.database.user_dao import UserDAO
from cinder_cli.database.session_dao import SessionDAO
from cinder_cli.database.questionnaire_dao import QuestionnaireDAO
from cinder_cli.database.models import User, InvitationCode, UserSession, QuestionnaireAnswer


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(DatabaseConnection, "_db_path", db_path)
    DatabaseConnection._instance = None
    init_database()
    yield
    DatabaseConnection._instance = None
    DatabaseConnection._db_path = None


class TestUserDAO:
    def test_create_user(self):
        dao = UserDAO()
        user = dao.create("测试用户")
        
        assert user is not None
        assert user.id is not None
        assert user.name == "测试用户"
        assert user.onboarding_completed is False

    def test_get_by_id(self):
        dao = UserDAO()
        created = dao.create("测试用户")
        found = dao.get_by_id(created.id)
        
        assert found is not None
        assert found.name == "测试用户"

    def test_get_by_id_not_found(self):
        dao = UserDAO()
        found = dao.get_by_id(999)
        assert found is None

    def test_update_onboarding_status(self):
        dao = UserDAO()
        user = dao.create("测试用户")
        
        dao.update_onboarding_status(user.id, True)
        updated = dao.get_by_id(user.id)
        
        assert updated.onboarding_completed is True

    def test_update_soul_path(self):
        dao = UserDAO()
        user = dao.create("测试用户")
        
        dao.update_soul_path(user.id, "/path/to/soul.meta.yaml")
        updated = dao.get_by_id(user.id)
        
        assert updated.soul_path == "/path/to/soul.meta.yaml"

    def test_get_all(self):
        dao = UserDAO()
        dao.create("用户1")
        dao.create("用户2")
        
        users = dao.get_all()
        assert len(users) == 2


class TestSessionDAO:
    def test_create_session(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        session_dao = SessionDAO()
        session = session_dao.create("test-session-id", user.id)
        
        assert session is not None
        assert session.session_id == "test-session-id"
        assert session.user_id == user.id

    def test_get_by_session_id(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        session_dao = SessionDAO()
        session_dao.create("test-session-id", user.id)
        
        found = session_dao.get_by_session_id("test-session-id")
        assert found is not None
        assert found.user_id == user.id

    def test_get_not_found(self):
        session_dao = SessionDAO()
        found = session_dao.get_by_session_id("nonexistent")
        assert found is None

    def test_delete_session(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        session_dao = SessionDAO()
        session_dao.create("test-session-id", user.id)
        
        session_dao.delete("test-session-id")
        found = session_dao.get_by_session_id("test-session-id")
        assert found is None

    def test_delete_expired(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        session_dao = SessionDAO()
        session_dao.create("expired-session", user.id, expires_in_days=-1)
        session_dao.create("valid-session", user.id, expires_in_days=7)
        
        deleted = session_dao.delete_expired()
        assert deleted >= 1
        
        assert session_dao.get_by_session_id("expired-session") is None
        assert session_dao.get_by_session_id("valid-session") is not None


class TestQuestionnaireDAO:
    def test_save_answer(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        dao = QuestionnaireDAO()
        answer = dao.save_answer(user.id, "q1", "A", "测试原因")
        
        assert answer is not None
        assert answer.question_key == "q1"
        assert answer.choice == "A"
        assert answer.reason == "测试原因"

    def test_update_answer(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        dao = QuestionnaireDAO()
        dao.save_answer(user.id, "q1", "A")
        updated = dao.save_answer(user.id, "q1", "B", "改主意了")
        
        assert updated.choice == "B"
        assert updated.reason == "改主意了"

    def test_get_progress(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        dao = QuestionnaireDAO()
        dao.save_answer(user.id, "q1", "A")
        dao.save_answer(user.id, "q2", "C")
        
        progress = dao.get_progress(user.id)
        assert progress["completed"] == 2
        assert progress["total"] == 6
        assert "q1" in progress["answers"]

    def test_clear_progress(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        dao = QuestionnaireDAO()
        dao.save_answer(user.id, "q1", "A")
        dao.clear_progress(user.id)
        
        progress = dao.get_progress(user.id)
        assert progress["completed"] == 0

    def test_get_all_answers(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        dao = QuestionnaireDAO()
        dao.save_answer(user.id, "q1", "A")
        dao.save_answer(user.id, "q2", "B")
        dao.save_answer(user.id, "q3", "C")
        
        answers = dao.get_all_answers(user.id)
        assert len(answers) == 3


class TestModels:
    def test_user_defaults(self):
        user = User(name="测试")
        assert user.id is None
        assert user.onboarding_completed is False
        assert user.created_at != ""

    def test_invitation_code_can_use(self):
        code = InvitationCode(code="TEST", is_single_use=False, max_uses=10, used_count=5)
        assert code.can_use() is True

    def test_invitation_code_cannot_use_single(self):
        code = InvitationCode(code="TEST", is_single_use=True, used_count=1)
        assert code.can_use() is False

    def test_invitation_code_cannot_use_max(self):
        code = InvitationCode(code="TEST", is_single_use=False, max_uses=10, used_count=10)
        assert code.can_use() is False

    def test_invitation_code_cannot_use_inactive(self):
        code = InvitationCode(code="TEST", is_single_use=False, is_active=False)
        assert code.can_use() is False

    def test_session_is_expired(self):
        session = UserSession(session_id="test", user_id=1, expires_at="2020-01-01T00:00:00")
        assert session.is_expired() is True

    def test_session_not_expired(self):
        session = UserSession(session_id="test", user_id=1, expires_at="2099-01-01T00:00:00")
        assert session.is_expired() is False
