"""
Tests for comprehensive evaluation features.
"""

import pytest
from cinder_cli.config import Config
from cinder_cli.executor.reflection_engine import ReflectionEngine


class TestComprehensiveEvaluation:
    """Test suite for comprehensive evaluation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.engine = ReflectionEngine(self.config)

    def test_evaluate_comprehensive_basic(self):
        """Test basic comprehensive evaluation."""
        code = '''
def hello():
    """Say hello."""
    print("Hello")
'''
        task = {
            "id": "1",
            "description": "创建一个hello函数",
            "language": "python"
        }

        result = self.engine.evaluate_comprehensive(code, task)

        assert "quality_score" in result
        assert "approved" in result
        assert "code_quality" in result
        assert "soul_alignment" in result
        assert "risk_assessment" in result

    def test_evaluate_code_quality_detailed(self):
        """Test detailed code quality evaluation."""
        good_code = '''
def well_written():
    """Well written function."""
    x = 1
    return x + 1
'''
        task = {"description": "创建一个函数"}
        result = self.engine._evaluate_code_quality_detailed(good_code, task)

        assert "overall_score" in result
        assert "scores" in result
        assert "syntax" in result["scores"]
        assert "logic" in result["scores"]
        assert "style" in result["scores"]
        assert "documentation" in result["scores"]

    def test_check_syntax_quality(self):
        """Test syntax quality checking."""
        valid_code = "x = 1"
        invalid_code = "def bad("

        valid_score = self.engine._check_syntax_quality(valid_code)
        invalid_score = self.engine._check_syntax_quality(invalid_code)

        assert valid_score == 1.0
        assert invalid_score < 1.0

    def test_check_logic_quality(self):
        """Test logic quality checking."""
        code = '''
def calculate(a, b):
    return a + b
'''
        task = {"description": "创建一个计算函数"}
        score = self.engine._check_logic_quality(code, task)

        assert 0 <= score <= 1
        assert score > 0.5

    def test_evaluate_soul_alignment(self):
        """Test Soul alignment evaluation."""
        code = '''
def conservative():
    """Safe function."""
    return 1 + 1
'''
        task = {"description": "创建一个函数"}
        soul_meta = {
            "traits": {
                "risk_tolerance": 30,
                "structure": 70,
                "detail_orientation": 60
            }
        }

        result = self.engine._evaluate_soul_alignment(code, task, soul_meta)

        assert "alignment_score" in result
        assert "trait_scores" in result
        assert 0 <= result["alignment_score"] <= 1

    def test_check_risk_tolerance_alignment(self):
        """Test risk tolerance alignment."""
        safe_code = "x = 1"
        risky_code = "eval('dangerous')"

        conservative_score = self.engine._check_risk_tolerance_alignment(safe_code, 30)
        risky_score = self.engine._check_risk_tolerance_alignment(risky_code, 30)

        assert conservative_score > risky_score

    def test_assess_risks(self):
        """Test risk assessment."""
        safe_code = "x = 1"
        risky_code = '''
import os
os.system("dangerous")
eval("risky")
'''

        task = {"description": "创建一个函数"}

        safe_result = self.engine._assess_risks(safe_code, task, None)
        risky_result = self.engine._assess_risks(risky_code, task, None)

        assert "risk_score" in safe_result
        assert "risk_score" in risky_result
        assert safe_result["risk_score"] > risky_result["risk_score"]

    def test_check_security_risks(self):
        """Test security risk detection."""
        dangerous_code = '''
import os
os.system("rm -rf /")
eval(user_input)
'''
        risks = self.engine._check_security_risks(dangerous_code)

        assert len(risks) > 0
        assert any("eval" in risk.lower() for risk in risks)

    def test_check_performance_risks(self):
        """Test performance risk detection."""
        nested_loops = '''
for i in range(10):
    for j in range(10):
        for k in range(10):
            for l in range(10):
                pass
'''
        risks = self.engine._check_performance_risks(nested_loops)

        assert len(risks) > 0

    def test_check_maintainability_risks(self):
        """Test maintainability risk detection."""
        long_code = "\n".join([f"# Line {i}" for i in range(150)])
        risks = self.engine._check_maintainability_risks(long_code)

        assert len(risks) > 0

    def test_generate_suggestions(self):
        """Test suggestion generation."""
        code_quality = {
            "issues": ["Syntax errors detected"]
        }
        soul_alignment = {
            "suggestions": ["Add more documentation"]
        }
        risk_assessment = {
            "risk_count": 2
        }

        suggestions = self.engine._generate_suggestions(
            code_quality,
            soul_alignment,
            risk_assessment
        )

        assert len(suggestions) > 0
        assert "Syntax errors detected" in suggestions
