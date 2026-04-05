"""
Extended proxy decision module with support for multiple decision types.
"""

from __future__ import annotations

from typing import Any
from enum import Enum

from cinder_cli.proxy_decision import (
    ConfidenceScorer,
    DecisionDetector,
    ProxyDecisionMaker,
    SoulRuleEngine,
)


class DecisionType(Enum):
    """Types of decisions."""
    
    CODE_ACCEPT = "code_accept"
    TECH_CHOICE = "tech_choice"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    GENERAL = "general"


class ExtendedSoulRuleEngine(SoulRuleEngine):
    """Extended soul rule engine with additional rules."""
    
    def apply_structure_rule(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply structure preference rule for architecture decisions."""
        structure = self.traits.get("structure", 50)
        
        if structure >= 65:
            return self._select_high_structure(options)
        elif structure <= 35:
            return self._select_low_structure(options)
        else:
            return self._select_balanced(options)
    
    def apply_detail_rule(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply detail orientation rule for implementation decisions."""
        detail_orientation = self.traits.get("detail_orientation", 50)
        
        if detail_orientation >= 65:
            return self._select_detailed(options)
        elif detail_orientation <= 35:
            return self._select_simple(options)
        else:
            return self._select_balanced(options)
    
    def _select_high_structure(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select option with highest structure/complexity."""
        if not options:
            return {}
        
        scored_options = []
        for option in options:
            complexity = option.get("complexity", "medium")
            score = {"low": 1, "medium": 2, "high": 3}.get(complexity, 2)
            scored_options.append((option, score))
        
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0]
    
    def _select_low_structure(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select option with lowest structure/complexity."""
        if not options:
            return {}
        
        scored_options = []
        for option in options:
            complexity = option.get("complexity", "medium")
            score = {"low": 3, "medium": 2, "high": 1}.get(complexity, 2)
            scored_options.append((option, score))
        
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0]
    
    def _select_detailed(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select option with most detail."""
        if not options:
            return {}
        
        scored_options = []
        for option in options:
            detail_level = option.get("detail_level", "medium")
            score = {"low": 1, "medium": 2, "high": 3}.get(detail_level, 2)
            scored_options.append((option, score))
        
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0]
    
    def _select_simple(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Select option with least detail."""
        if not options:
            return {}
        
        scored_options = []
        for option in options:
            detail_level = option.get("detail_level", "medium")
            score = {"low": 3, "medium": 2, "high": 1}.get(detail_level, 2)
            scored_options.append((option, score))
        
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0]


class ExtendedProxyDecisionMaker(ProxyDecisionMaker):
    """Extended proxy decision maker with support for multiple decision types."""
    
    def __init__(self, soul_meta: dict[str, Any]):
        self.rule_engine = ExtendedSoulRuleEngine(soul_meta)
        self.confidence_scorer = ConfidenceScorer()
        self.soul_meta = soul_meta
    
    def make_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
        decision_type: DecisionType = DecisionType.GENERAL,
    ) -> dict[str, Any]:
        """Make a proxy decision based on decision type and soul rules."""
        
        if not DecisionDetector.is_decision_point(context, [opt.get("text", "") for opt in options]):
            return {
                "decision": None,
                "confidence": 0.0,
                "requires_human": False,
                "reasoning": "Not a decision point",
                "decision_type": decision_type.value,
            }
        
        if decision_type == DecisionType.CODE_ACCEPT:
            return self._make_code_accept_decision(context, options)
        elif decision_type == DecisionType.TECH_CHOICE:
            return self._make_tech_choice_decision(context, options)
        elif decision_type == DecisionType.ARCHITECTURE:
            return self._make_architecture_decision(context, options)
        elif decision_type == DecisionType.IMPLEMENTATION:
            return self._make_implementation_decision(context, options)
        else:
            return self._make_general_decision(context, options)
    
    def _make_code_accept_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make code acceptance decision."""
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
            "decision_type": DecisionType.CODE_ACCEPT.value,
        }
    
    def _make_tech_choice_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make technology choice decision."""
        selected = self.rule_engine.apply_risk_rule(options)
        
        confidence = self.confidence_scorer.calculate(
            soul_rules_applied=["risk_tolerance"],
            option_match=0.7,
            context_clarity=0.6,
        )
        
        requires_human = self.rule_engine.should_escalate_to_human(context, confidence)
        
        return {
            "decision": selected,
            "confidence": confidence,
            "requires_human": requires_human,
            "reasoning": f"Applied risk tolerance for tech choice (score: {self.rule_engine.traits.get('risk_tolerance', 50)})",
            "soul_rules_applied": ["risk_tolerance"],
            "decision_type": DecisionType.TECH_CHOICE.value,
        }
    
    def _make_architecture_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make architecture decision."""
        selected = self.rule_engine.apply_structure_rule(options)
        
        confidence = self.confidence_scorer.calculate(
            soul_rules_applied=["structure"],
            option_match=0.7,
            context_clarity=0.6,
        )
        
        requires_human = self.rule_engine.should_escalate_to_human(context, confidence)
        
        return {
            "decision": selected,
            "confidence": confidence,
            "requires_human": requires_human,
            "reasoning": f"Applied structure preference rule (score: {self.rule_engine.traits.get('structure', 50)})",
            "soul_rules_applied": ["structure"],
            "decision_type": DecisionType.ARCHITECTURE.value,
        }
    
    def _make_implementation_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make implementation decision."""
        selected = self.rule_engine.apply_detail_rule(options)
        
        confidence = self.confidence_scorer.calculate(
            soul_rules_applied=["detail_orientation"],
            option_match=0.7,
            context_clarity=0.6,
        )
        
        requires_human = self.rule_engine.should_escalate_to_human(context, confidence)
        
        return {
            "decision": selected,
            "confidence": confidence,
            "requires_human": requires_human,
            "reasoning": f"Applied detail orientation rule (score: {self.rule_engine.traits.get('detail_orientation', 50)})",
            "soul_rules_applied": ["detail_orientation"],
            "decision_type": DecisionType.IMPLEMENTATION.value,
        }
    
    def _make_general_decision(
        self,
        context: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make general decision."""
        selected = self.rule_engine.apply_risk_rule(options)
        
        confidence = self.confidence_scorer.calculate(
            soul_rules_applied=["risk_tolerance"],
            option_match=0.6,
            context_clarity=0.5,
        )
        
        requires_human = self.rule_engine.should_escalate_to_human(context, confidence)
        
        return {
            "decision": selected,
            "confidence": confidence,
            "requires_human": requires_human,
            "reasoning": "Applied general decision rules",
            "soul_rules_applied": ["risk_tolerance"],
            "decision_type": DecisionType.GENERAL.value,
        }
