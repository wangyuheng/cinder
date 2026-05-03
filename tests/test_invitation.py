"""
Tests for invitation code management.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database
from cinder_cli.invitation.loader import InvitationLoader
from cinder_cli.invitation.validator import InvitationValidator


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
def config_file(tmp_path):
    config_data = {
        "codes": [
            {"code": "VALID-CODE", "is_single_use": False, "max_uses": 100, "description": "通用邀请码"},
            {"code": "SINGLE-USE", "is_single_use": True, "description": "单次邀请码"},
            {"code": "LIMITED-5", "is_single_use": False, "max_uses": 5, "description": "5次邀请码"},
            {"code": "DISABLED", "is_single_use": False, "is_active": False, "description": "已禁用邀请码"},
        ]
    }
    
    config_path = tmp_path / "invitations.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, allow_unicode=True)
    
    return config_path


class TestInvitationLoader:
    def test_load_codes(self, config_file):
        loader = InvitationLoader(config_file)
        codes = loader.load_codes()
        
        assert len(codes) == 4
        assert codes[0].code == "VALID-CODE"
        assert codes[1].is_single_use is True

    def test_load_codes_no_file(self, tmp_path):
        loader = InvitationLoader(tmp_path / "nonexistent.yaml")
        codes = loader.load_codes()
        assert codes == []

    def test_get_code_by_value(self, config_file):
        loader = InvitationLoader(config_file)
        code = loader.get_code_by_value("VALID-CODE")
        
        assert code is not None
        assert code.code == "VALID-CODE"

    def test_get_code_not_found(self, config_file):
        loader = InvitationLoader(config_file)
        code = loader.get_code_by_value("NONEXISTENT")
        assert code is None


class TestInvitationValidator:
    def test_validate_valid_code(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        is_valid, message = validator.validate("VALID-CODE")
        
        assert is_valid is True
        assert message == "邀请码有效"

    def test_validate_invalid_code(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        is_valid, message = validator.validate("INVALID")
        
        assert is_valid is False
        assert message == "邀请码无效"

    def test_validate_disabled_code(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        is_valid, message = validator.validate("DISABLED")
        
        assert is_valid is False
        assert message == "邀请码已被禁用"

    def test_validate_single_use_code(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        
        is_valid, _ = validator.validate("SINGLE-USE")
        assert is_valid is True
        
        validator.record_usage("SINGLE-USE")
        
        is_valid, message = validator.validate("SINGLE-USE")
        assert is_valid is False
        assert message == "邀请码已被使用"

    def test_validate_limited_code(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        
        for i in range(5):
            is_valid, _ = validator.validate("LIMITED-5")
            assert is_valid is True
            validator.record_usage("LIMITED-5")
        
        is_valid, message = validator.validate("LIMITED-5")
        assert is_valid is False
        assert message == "邀请码已达到使用上限"

    def test_record_usage(self, config_file):
        validator = InvitationValidator(InvitationLoader(config_file))
        
        validator.record_usage("VALID-CODE")
        
        db_code = validator._get_db_code("VALID-CODE")
        assert db_code is not None
        assert db_code["used_count"] == 1
