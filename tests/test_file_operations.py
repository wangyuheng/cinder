"""
Tests for FileOperations.
"""

import pytest
from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.executor import FileOperations


@pytest.fixture
def file_ops(tmp_path):
    """Create a file operations instance with tmp_path as working directory."""
    config = Config(tmp_path / ".cinder")
    return FileOperations(config, working_dir=tmp_path)


class TestFileOperations:
    """Test cases for FileOperations."""

    def test_create_file(self, file_ops, tmp_path):
        """Test file creation."""
        file_path = tmp_path / "test.py"
        content = "# Test file\nprint('Hello')"

        result = file_ops.create_file(str(file_path), content)

        assert result["status"] == "success"
        assert file_path.exists()
        assert file_path.read_text() == content

    def test_create_directory(self, file_ops, tmp_path):
        """Test directory creation."""
        dir_path = tmp_path / "test_dir" / "nested"

        result = file_ops.create_directory(str(dir_path))

        assert result["status"] == "success"
        assert dir_path.exists()

    def test_modify_file(self, file_ops, tmp_path):
        """Test file modification."""
        file_path = tmp_path / "test.py"
        file_path.write_text("original content")

        new_content = "new content"
        result = file_ops.modify_file(str(file_path), new_content)

        assert result["status"] == "success"
        assert file_path.read_text() == new_content

    def test_delete_file(self, file_ops, tmp_path):
        """Test file deletion."""
        file_path = tmp_path / "test.py"
        file_path.write_text("content")

        result = file_ops.delete_file(str(file_path))

        assert result["status"] == "success"
        assert not file_path.exists()

    def test_validate_path_security(self, file_ops, tmp_path):
        """Test path validation security."""
        with pytest.raises(ValueError, match="不在工作目录内"):
            file_ops._validate_path("/etc/passwd")

    def test_validate_extension(self, file_ops, tmp_path):
        """Test file extension validation."""
        invalid_path = tmp_path / "test.exe"
        with pytest.raises(ValueError, match="不允许的文件类型"):
            file_ops._validate_path(str(invalid_path))

    def test_backup_creation(self, file_ops, tmp_path):
        """Test backup creation."""
        file_path = tmp_path / "test.py"
        file_path.write_text("original")

        backup_path = file_ops._create_backup(file_path)

        assert backup_path.exists()
        assert backup_path.read_text() == "original"
