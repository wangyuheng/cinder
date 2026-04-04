"""
Tests for iterative code generation features.
"""

import pytest
from cinder_cli.config import Config
from cinder_cli.executor.code_generator import CodeGenerator


class TestIterativeCodeGeneration:
    """Test suite for iterative code generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.generator = CodeGenerator(self.config)

    def test_generate_with_iterations_basic(self):
        """Test basic iterative generation."""
        description = "创建一个简单的Python函数"
        result = self.generator.generate_with_iterations(
            description,
            language="python",
            max_iterations=2,
            quality_threshold=0.5
        )

        assert "code" in result
        assert "iterations" in result
        assert "final_score" in result
        assert result["iterations"] >= 1
        assert result["iterations"] <= 2

    def test_self_evaluate(self):
        """Test self-evaluation mechanism."""
        code = '''
def hello():
    """Say hello."""
    print("Hello")
'''
        description = "创建一个hello函数"
        evaluation = self.generator._self_evaluate(code, description, "python")

        assert "quality_score" in evaluation
        assert "scores" in evaluation
        assert "issues" in evaluation
        assert 0 <= evaluation["quality_score"] <= 1

    def test_evaluate_logic(self):
        """Test logic evaluation."""
        code = '''
def calculate_sum(a, b):
    return a + b
'''
        task = {"description": "创建一个加法函数"}
        score = self.generator._evaluate_logic(code, "创建一个加法函数", "python")

        assert 0 <= score <= 1
        assert score > 0.5

    def test_evaluate_style(self):
        """Test style evaluation."""
        good_code = '''
def well_formatted():
    """Well formatted function."""
    x = 1
    return x
'''
        score = self.generator._evaluate_style(good_code, "python")
        assert score > 0.5

    def test_evaluate_documentation(self):
        """Test documentation evaluation."""
        documented_code = '''
def documented_function():
    """This function has documentation."""
    pass
'''
        score = self.generator._evaluate_documentation(documented_code, "python")
        assert score > 0.3

    def test_best_version_tracking(self):
        """Test that best version is tracked."""
        result = self.generator.generate_with_iterations(
            "创建一个函数",
            language="python",
            max_iterations=3,
            quality_threshold=0.9
        )

        assert "code" in result
        assert "iteration_history" in result
        assert len(result["iteration_history"]) > 0

    def test_quality_threshold_enforcement(self):
        """Test quality threshold enforcement."""
        result = self.generator.generate_with_iterations(
            "创建一个函数",
            language="python",
            max_iterations=2,
            quality_threshold=0.7
        )

        assert "quality_threshold_met" in result
        if result["quality_threshold_met"]:
            assert result["final_score"] >= 0.7

    def test_regenerate_with_feedback(self):
        """Test feedback-driven regeneration."""
        previous_code = "def bad(): pass"
        evaluation = {
            "issues": ["No documentation"],
            "scores": {"documentation": 0.0}
        }

        new_code = self.generator._regenerate_with_feedback(
            "创建一个函数",
            "python",
            None,
            previous_code,
            evaluation
        )

        assert new_code is not None
        assert len(new_code) > 0
