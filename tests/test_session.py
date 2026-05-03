"""
Tests for session management.
"""

import pytest

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database
from cinder_cli.database.user_dao import UserDAO
from cinder_cli.web.session import SessionManager


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(DatabaseConnection, "_db_path", db_path)
    DatabaseConnection._instance = None
    init_database()
    yield
    DatabaseConnection._instance = None
    DatabaseConnection._db_path = None


class TestSessionManager:
    def test_create_session(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        manager = SessionManager()
        session_id = manager.create_session(user.id)
        
        assert session_id is not None
        assert len(session_id) == 36

    def test_validate_session(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        manager = SessionManager()
        session_id = manager.create_session(user.id)
        
        assert manager.validate_session(session_id) is True

    def test_validate_invalid_session(self):
        manager = SessionManager()
        assert manager.validate_session("nonexistent") is False

    def test_get_user_id(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        manager = SessionManager()
        session_id = manager.create_session(user.id)
        
        found_user_id = manager.get_user_id(session_id)
        assert found_user_id == user.id

    def test_delete_session(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        manager = SessionManager()
        session_id = manager.create_session(user.id)
        
        manager.delete_session(session_id)
        assert manager.validate_session(session_id) is False

    def test_cleanup_expired(self):
        user_dao = UserDAO()
        user = user_dao.create("测试用户")
        
        manager = SessionManager()
        manager.create_session(user.id, expires_in_days=-1)
        valid_session = manager.create_session(user.id, expires_in_days=7)
        
        cleaned = manager.cleanup_expired()
        assert cleaned >= 1
        assert manager.validate_session(valid_session) is True
