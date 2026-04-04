"""
Proxy decision module for making decisions based on soul rules.
"""

from __future__ import annotations

from typing import Any


class DecisionDetector:
    """Detects when a decision point is reached."""

    @staticmethod
    def is_decision_point(context: str, options: list[str]) -> bool:
        """Check if current context requires a decision."""
        if len(options) <= 1:
            return False

        decision_keywords = ["选择", "决定", "应该", "还是", "或者"]
        if any(keyword in context for keyword in decision_keywords):
            return True

        return False

    @staticmethod
    def is_high_stakes(context: str) -> bool:
        """Check if decision is high-stakes."""
        high_stakes_keywords = ["财务", "人生", "职业", "关系", "重大", "重要"]
        return any(keyword in context for keyword in high_stakes_keywords)


class SoulRuleEngine:
    """Applies soul rules to decision-making."""

    def __init__(self, soul_meta: dict[str, Any]):
        self.soul_meta = soul_meta
        self.traits = soul_meta.get("traits", {})

    def apply_risk_rule(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply risk tolerance rule to select option."""
        risk_tolerance = self.traits.get("risk_tolerance", 50)

        if risk_tolerance <= 38:
            return self._select_conservative(options)
        elif risk_tolerance >= 66:
            return self._select_aggressive(options)
        else:
            return self._select_balanced(options)

    def apply_communication_rule(self, response: str) -> str:
        """Apply communication preference rule to format response."""
        structure = self.traits.get("structure", 50)

        if structure >= 65:
            return self._format_structured(response)
        else:
            return self._format_conversational(response)

    def should_escalate_to_human(self, context: str, confidence: float) -> bool:
        """Check if decision should be escalated to human."""
        if DecisionDetector.is_high_stakes(context):
            return True

        if confidence < 0.5:
            return True

        return False

    def _select_conservative(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select most conservative option."""
        return options[0] if options else {}

    def _select_aggressive(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select most aggressive option."""
        return options[-1] if options else {}

    def _select_balanced(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select balanced option."""
        if not options:
            return {}
        mid_index = len(options) // 2
        return options[mid_index]

    def _format_structured(self, response: str) -> str:
        """Format response in structured way."""
        return f"结论：\n{response}\n\n建议：\n- 建议一\n- 建议二"

    def _format_conversational(self, response: str) -> str:
        """Format response in conversational way."""
        return response


class ConfidenceScorer:
    """Calculates confidence score for decisions."""

    @staticmethod
    def calculate(
        soul_rules_applied: list[str],
        option_match: float,
        context_clarity: float,
    ) -> float:
        """Calculate confidence score."""
        base_score = 0.5

        rules_bonus = len(soul_rules_applied) * 0.1

        match_bonus = option_match * 0.2

        clarity_bonus = context_clarity * 0.2

        total = base_score + rules_bonus + match_bonus + clarity_bonus

        return min(1.0, max(0.0, total))


class ProxyDecisionMaker:
    """Main class for making proxy decisions."""

    def __init__(self, soul_meta: dict[str, Any]):
        self.rule_engine = SoulRuleEngine(soul_meta)
        self.confidence_scorer = ConfidenceScorer()

    def make_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make a proxy decision based on soul rules."""
        if not DecisionDetector.is_decision_point(context, [opt.get("text", "") for opt in options]):
            return {
                "decision": None,
                "confidence": 0.0,
                "requires_human": False,
                "reasoning": "Not a decision point",
            }

        selected = self.rule_engine.apply_risk_rule(options)

        confidence = self.confidence_scorer.calculate(
            soul_rules_applied=["risk_tolerance"],
            option_match=0.8,
            context_clarity=0.7,
        )

        requires_human = self.rule_engine.should_escalate_to_human(context, confidence)

        return {
            "decision": selected,
            "confidence": confidence,
            "requires_human": requires_human,
            "reasoning": f"Applied risk tolerance rule (score: {self.rule_engine.traits.get('risk_tolerance', 50)})",
            "soul_rules_applied": ["risk_tolerance"],
        }
