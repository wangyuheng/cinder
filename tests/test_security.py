"""
Security tests for the executor module.
"""

import pytest
from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.executor import FileOperations, ReflectionEngine


@pytest.fixture
def setup_security(tmp_path):
    """Set up security test environment."""
    config = Config(tmp_path / ".cinder")
    file_ops = FileOperations(config, working_dir=tmp_path)
    return {
        "config": config,
        "file_ops": file_ops,
        "tmp_path": tmp_path,
    }


class TestPathSecurity:
    """Test path security boundaries."""

    def test_reject_absolute_path_outside_workdir(self, setup_security):
        """Test rejection of absolute paths outside working directory."""
        file_ops = setup_security["file_ops"]

        with pytest.raises(ValueError, match="不在工作目录内"):
            file_ops._validate_path("/etc/passwd")

        with pytest.raises(ValueError, match="不在工作目录内"):
            file_ops._validate_path("/var/log/system.log")

    def test_reject_path_traversal_attack(self, setup_security):
        """Test rejection of path traversal attempts."""
        file_ops = setup_security["file_ops"]
        tmp_path = setup_security["tmp_path"]

        with pytest.raises(ValueError, match="不在工作目录内"):
            file_ops._validate_path(str(tmp_path / "../../../etc/passwd"))

    def test_reject_symlink_outside_workdir(self, setup_security):
        """Test rejection of symlinks pointing outside working directory."""
        file_ops = setup_security["file_ops"]
        tmp_path = setup_security["tmp_path"]

        symlink_path = tmp_path / "evil_link.py"
        try:
            symlink_path.symlink_to("/etc/passwd")

            with pytest.raises(ValueError, match="不在工作目录内"):
                file_ops._validate_path(str(symlink_path))
        finally:
            if symlink_path.exists():
                symlink_path.unlink()


class TestFileExtensionSecurity:
    """Test file extension security."""

    def test_reject_executable_extensions(self, setup_security):
        """Test rejection of executable file extensions."""
        file_ops = setup_security["file_ops"]
        tmp_path = setup_security["tmp_path"]

        dangerous_extensions = [".exe", ".bat", ".cmd", ".com", ".dll"]

        for ext in dangerous_extensions:
            with pytest.raises(ValueError, match="不允许的文件类型"):
                file_ops._validate_path(str(tmp_path / f"test{ext}"))

    def test_allow_safe_extensions(self, setup_security):
        """Test acceptance of safe file extensions."""
        file_ops = setup_security["file_ops"]
        tmp_path = setup_security["tmp_path"]

        safe_extensions = [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".md"]

        for ext in safe_extensions:
            result = file_ops._validate_path(str(tmp_path / f"test{ext}"))
            assert result.suffix == ext


class TestCodeSecurity:
    """Test code security analysis."""

    def test_detect_eval_usage(self, setup_security):
        """Test detection of eval() usage."""
        config = setup_security["config"]
        reflection = ReflectionEngine(config)

        dangerous_code = '''
def run_user_input(data):
    result = eval(data)
    return result
'''
        evaluation = reflection.evaluate_execution(
            code=dangerous_code,
            task={"description": "执行用户输入"},
        )

        assert len(evaluation["risks"]) > 0
        assert any("eval" in r.lower() for r in evaluation["risks"])

    def test_detect_exec_usage(self, setup_security):
        """Test detection of exec() usage."""
        config = setup_security["config"]
        reflection = ReflectionEngine(config)

        dangerous_code = '''
def run_code(code_str):
    exec(code_str)
'''
        evaluation = reflection.evaluate_execution(
            code=dangerous_code,
            task={"description": "执行代码"},
        )

        assert len(evaluation["risks"]) > 0
        assert any("exec" in r.lower() for r in evaluation["risks"])

    def test_detect_dynamic_import(self, setup_security):
        """Test detection of dynamic imports."""
        config = setup_security["config"]
        reflection = ReflectionEngine(config)

        dangerous_code = '''
def load_module(name):
    return __import__(name)
'''
        evaluation = reflection.evaluate_execution(
            code=dangerous_code,
            task={"description": "加载模块"},
        )

        assert len(evaluation["risks"]) > 0


class TestBackupSecurity:
    """Test backup and recovery security."""

    def test_backup_not_overwrite_system_files(self, setup_security):
        """Test that backup doesn't overwrite system files."""
        file_ops = setup_security["file_ops"]
        tmp_path = setup_security["tmp_path"]

        test_file = tmp_path / "test.py"
        test_file.write_text("original")

        backup_path = file_ops._create_backup(test_file)

        assert backup_path.parent == file_ops.backup_dir
        assert backup_path.suffix == ".bak"

    def test_backup_directory_isolation(self, setup_security):
        """Test that backup directory is isolated."""
        file_ops = setup_security["file_ops"]

        assert file_ops.backup_dir.name == ".cinder_backups"
        assert file_ops.backup_dir.parent == file_ops.working_dir


class TestInputValidation:
    """Test input validation."""

    def test_empty_code_handling(self, setup_security):
        """Test handling of empty code."""
        config = setup_security["config"]
        reflection = ReflectionEngine(config)

        evaluation = reflection.evaluate_execution(
            code="",
            task={"description": "空代码"},
        )

        assert evaluation["quality_score"] < 0.8

    def test_malformed_code_handling(self, setup_security):
        """Test handling of malformed code."""
        config = setup_security["config"]
        reflection = ReflectionEngine(config)

        malformed_code = "def broken(:\n    pass"

        evaluation = reflection.evaluate_execution(
            code=malformed_code,
            task={"description": "错误代码"},
        )

        assert evaluation["quality_score"] < 0.7
