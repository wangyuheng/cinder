"""
Tests for SoulRuleEngine.
"""

import pytest

from cinder_cli.proxy_decision import SoulRuleEngine, ConfidenceScorer, DecisionDetector


class TestSoulRuleEngine:
    """Test cases for SoulRuleEngine."""

    def test_conservative_risk_selection(self):
        """Test conservative risk selection."""
        soul_meta = {"traits": {"risk_tolerance": 30}}
        engine = SoulRuleEngine(soul_meta)

        options = [
            {"text": "Safe option", "risk": "low"},
            {"text": "Risky option", "risk": "high"},
        ]

        result = engine.apply_risk_rule(options)
        assert result == options[0]

    def test_aggressive_risk_selection(self):
        """Test aggressive risk selection."""
        soul_meta = {"traits": {"risk_tolerance": 70}}
        engine = SoulRuleEngine(soul_meta)

        options = [
            {"text": "Safe option", "risk": "low"},
            {"text": "Risky option", "risk": "high"},
        ]

        result = engine.apply_risk_rule(options)
        assert result == options[-1]

    def test_balanced_risk_selection(self):
        """Test balanced risk selection."""
        soul_meta = {"traits": {"risk_tolerance": 50}}
        engine = SoulRuleEngine(soul_meta)

        options = [
            {"text": "Safe option", "risk": "low"},
            {"text": "Medium option", "risk": "medium"},
            {"text": "Risky option", "risk": "high"},
        ]

        result = engine.apply_risk_rule(options)
        assert result == options[1]

    def test_should_escalate_high_stakes(self):
        """Test escalation for high-stakes decisions."""
        soul_meta = {"traits": {"risk_tolerance": 50}}
        engine = SoulRuleEngine(soul_meta)

        assert engine.should_escalate_to_human("涉及重大财务支出", 0.8) is True
        assert engine.should_escalate_to_human("日常决策", 0.8) is False

    def test_should_escalate_low_confidence(self):
        """Test escalation for low confidence."""
        soul_meta = {"traits": {"risk_tolerance": 50}}
        engine = SoulRuleEngine(soul_meta)

        assert engine.should_escalate_to_human("日常决策", 0.3) is True
        assert engine.should_escalate_to_human("日常决策", 0.7) is False


class TestConfidenceScorer:
    """Test cases for ConfidenceScorer."""

    def test_high_confidence(self):
        """Test high confidence calculation."""
        score = ConfidenceScorer.calculate(
            soul_rules_applied=["risk_tolerance", "communication"],
            option_match=0.9,
            context_clarity=0.9,
        )
        assert score >= 0.8

    def test_low_confidence(self):
        """Test low confidence calculation."""
        score = ConfidenceScorer.calculate(
            soul_rules_applied=[],
            option_match=0.3,
            context_clarity=0.3,
        )
        assert score < 0.7

    def test_confidence_bounds(self):
        """Test confidence score bounds."""
        score = ConfidenceScorer.calculate(
            soul_rules_applied=["rule1", "rule2", "rule3", "rule4", "rule5"],
            option_match=1.0,
            context_clarity=1.0,
        )
        assert 0.0 <= score <= 1.0


class TestDecisionDetector:
    """Test cases for DecisionDetector."""

    def test_is_decision_point(self):
        """Test decision point detection."""
        assert DecisionDetector.is_decision_point("应该选择哪个？", ["A", "B"]) is True
        assert DecisionDetector.is_decision_point("这是一个陈述", ["A"]) is False

    def test_is_high_stakes(self):
        """Test high-stakes detection."""
        assert DecisionDetector.is_high_stakes("这是关于职业的重大决定") is True
        assert DecisionDetector.is_high_stakes("今天吃什么") is False
