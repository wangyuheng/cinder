"""
Integration tests for the executor module.
"""

import pytest
from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.executor import (
    AutonomousExecutor,
    TaskPlanner,
    CodeGenerator,
    ReflectionEngine,
    FileOperations,
    ExecutionLogger,
)


@pytest.fixture
def setup_executor(tmp_path):
    """Set up executor components for testing."""
    config = Config(tmp_path / ".cinder")
    return {
        "config": config,
        "tmp_path": tmp_path,
    }


class TestExecutorIntegration:
    """Integration tests for executor workflow."""

    def test_task_planner_to_file_operations(self, setup_executor):
        """Test workflow from task planning to file creation."""
        config = setup_executor["config"]
        tmp_path = setup_executor["tmp_path"]

        planner = TaskPlanner(config)
        file_ops = FileOperations(config, working_dir=tmp_path)

        plan = planner.decompose_goal("创建Python脚本")
        assert len(plan["subtasks"]) >= 1

        task = plan["subtasks"][0]
        result = file_ops.create_file(
            str(tmp_path / task["file_path"]),
            "# Generated code\nprint('Hello')",
        )

        assert result["status"] == "success"
        assert (tmp_path / task["file_path"]).exists()

    def test_code_generator_to_reflection(self, setup_executor):
        """Test workflow from code generation to reflection."""
        config = setup_executor["config"]

        generator = CodeGenerator(config)
        reflection = ReflectionEngine(config)

        code = '''
def hello():
    """Say hello."""
    print("Hello, World!")
'''
        evaluation = reflection.evaluate_execution(
            code=code,
            task={"description": "创建问候函数"},
        )

        assert "quality_score" in evaluation
        assert evaluation["quality_score"] > 0.5

    def test_full_dry_run_workflow(self, setup_executor):
        """Test full dry-run execution workflow."""
        config = setup_executor["config"]

        executor = AutonomousExecutor(config)

        result = executor.execute(
            goal="创建简单的Python脚本",
            mode="dry-run",
        )

        assert result["status"] == "dry-run"
        assert "task_tree" in result
        assert len(result["task_tree"]["subtasks"]) >= 1

    def test_execution_logging_integration(self, setup_executor):
        """Test execution logging workflow."""
        config = setup_executor["config"]
        tmp_path = setup_executor["tmp_path"]

        logger = ExecutionLogger(config)
        file_ops = FileOperations(config, working_dir=tmp_path)

        file_ops.create_file(str(tmp_path / "test.py"), "# test")

        execution_id = logger.log_execution(
            goal="测试执行",
            task_tree={"subtasks": [{"id": "1", "description": "测试任务"}]},
            results=[{"file_result": {"file_path": str(tmp_path / "test.py")}}],
        )

        assert execution_id > 0

        report = logger.generate_report(execution_id)
        assert "测试执行" in report

    def test_task_complexity_and_preview(self, setup_executor):
        """Test task complexity estimation and preview."""
        config = setup_executor["config"]

        planner = TaskPlanner(config)

        preview = planner.preview_tasks("创建Web应用")

        assert "task_count" in preview
        assert "complexity" in preview
        assert preview["complexity"]["total"] > 0
        assert preview["complexity"]["estimated_time_minutes"] > 0

    def test_file_operations_with_backup(self, setup_executor):
        """Test file operations with backup system."""
        config = setup_executor["config"]
        tmp_path = setup_executor["tmp_path"]

        file_ops = FileOperations(config, working_dir=tmp_path)

        file_path = tmp_path / "test.py"
        file_ops.create_file(str(file_path), "original content")

        file_ops.modify_file(str(file_path), "new content")

        backups = file_ops.list_backups()
        assert len(backups) >= 1

        assert file_path.read_text() == "new content"

    def test_reflection_with_suggestions(self, setup_executor):
        """Test reflection engine suggestions."""
        config = setup_executor["config"]

        reflection = ReflectionEngine(config)

        poor_code = "x=1"
        evaluation = reflection.evaluate_execution(
            code=poor_code,
            task={"description": "简单代码"},
        )

        assert evaluation["quality_score"] < 0.9

    def test_report_generation_summary(self, setup_executor):
        """Test report generation for multiple executions."""
        config = setup_executor["config"]

        logger = ExecutionLogger(config)

        for i in range(3):
            logger.log_execution(
                goal=f"测试目标 {i}",
                task_tree={},
                results=[],
            )

        report = logger.generate_report(format="markdown")

        assert "执行统计报告" in report
        assert "总执行次数" in report

    def test_pattern_analysis(self, setup_executor):
        """Test execution pattern analysis."""
        config = setup_executor["config"]

        logger = ExecutionLogger(config)

        logger.log_execution(
            goal="创建Python项目",
            task_tree={},
            results=[{"file_result": {"file_path": "/tmp/test.py"}}],
        )
        logger.log_execution(
            goal="创建Web应用",
            task_tree={},
            results=[{"file_result": {"file_path": "/tmp/app.py"}}],
        )

        patterns = logger.analyze_patterns()

        assert "insights" in patterns
        assert len(patterns["insights"]) >= 0


class TestExecutorErrorHandling:
    """Test error handling in executor."""

    def test_invalid_file_path(self, setup_executor):
        """Test handling of invalid file paths."""
        config = setup_executor["config"]
        tmp_path = setup_executor["tmp_path"]

        file_ops = FileOperations(config, working_dir=tmp_path)

        with pytest.raises(ValueError, match="不在工作目录内"):
            file_ops._validate_path("/etc/passwd")

    def test_invalid_file_extension(self, setup_executor):
        """Test handling of invalid file extensions."""
        config = setup_executor["config"]
        tmp_path = setup_executor["tmp_path"]

        file_ops = FileOperations(config, working_dir=tmp_path)

        with pytest.raises(ValueError, match="不允许的文件类型"):
            file_ops._validate_path(str(tmp_path / "test.exe"))

    def test_nonexistent_execution_report(self, setup_executor):
        """Test report for nonexistent execution."""
        config = setup_executor["config"]

        logger = ExecutionLogger(config)

        report = logger.generate_report(execution_id=99999)

        assert "不存在" in report

    def test_replay_nonexistent_execution(self, setup_executor):
        """Test replay of nonexistent execution."""
        config = setup_executor["config"]

        logger = ExecutionLogger(config)

        replay = logger.replay_execution(99999)

        assert "error" in replay
