"""
Tests for ReflectionEngine.
"""

import pytest

from cinder_cli.config import Config
from cinder_cli.executor import ReflectionEngine


@pytest.fixture
def reflection_engine(tmp_path):
    """Create a reflection engine instance."""
    config = Config(tmp_path / ".cinder")
    return ReflectionEngine(config)


class TestReflectionEngine:
    """Test cases for ReflectionEngine."""

    def test_evaluate_execution_success(self, reflection_engine):
        """Test successful execution evaluation."""
        code = '''
def hello():
    """Say hello."""
    print("Hello, World!")
'''
        result = reflection_engine.evaluate_execution(
            code=code,
            task={"description": "创建问候函数"},
        )

        assert "approved" in result
        assert "quality_score" in result
        assert "suggestions" in result
        assert "risks" in result

    def test_check_risk_with_eval(self, reflection_engine):
        """Test risk check with eval pattern."""
        code = '''
def run_code(user_input):
    result = eval(user_input)
    return result
'''
        result = reflection_engine.evaluate_execution(
            code=code,
            task={"description": "执行用户代码"},
        )

        assert len(result["risks"]) > 0

    def test_check_style_without_docstring(self, reflection_engine):
        """Test style check without docstring."""
        code = '''
def calculate(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def subtract(a, b):
    return a - b
'''
        result = reflection_engine.evaluate_execution(
            code=code,
            task={"description": "数学运算"},
        )

        assert "suggestions" in result

    def test_check_code_quality_good(self, reflection_engine):
        """Test code quality check for good code."""
        good_code = '''
def calculate_sum(numbers: list[int]) -> int:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: A list of integers.

    Returns:
        The sum of all numbers.
    """
    total = 0
    for num in numbers:
        total += num
    return total
'''
        result = reflection_engine.evaluate_execution(
            code=good_code,
            task={"description": "求和函数"},
        )

        assert result["quality_score"] > 0.5

    def test_check_code_quality_poor(self, reflection_engine):
        """Test code quality check for poor code."""
        poor_code = "x=1+2"
        result = reflection_engine.evaluate_execution(
            code=poor_code,
            task={"description": "简单计算"},
        )

        assert result["quality_score"] < 0.9

    def test_evaluate_empty_code(self, reflection_engine):
        """Test evaluation with empty code."""
        result = reflection_engine.evaluate_execution(
            code="",
            task={"description": "空任务"},
        )

        assert "approved" in result
        assert result["quality_score"] < 0.8

    def test_evaluate_syntax_error(self, reflection_engine):
        """Test evaluation with syntax error."""
        bad_code = "def broken(\n"
        result = reflection_engine.evaluate_execution(
            code=bad_code,
            task={"description": "错误代码"},
        )

        assert result["quality_score"] < 0.6
