"""
Example: Technology Choice Decision

This example demonstrates how the Decision Agent makes technology choices
based on Soul profile.
"""

from cinder_cli.config import Config
from cinder_cli.extended_proxy_decision import ExtendedProxyDecisionMaker, DecisionType


def example_conservative_tech_choice():
    """Example: Conservative user choosing database."""
    
    # Conservative user profile (low risk tolerance)
    soul_meta = {
        "traits": {
            "risk_tolerance": 25,  # Very conservative
            "structure": 50,
            "detail_orientation": 50,
        }
    }
    
    decision_maker = ExtendedProxyDecisionMaker(soul_meta)
    
    # Technology options
    options = [
        {
            "text": "PostgreSQL",
            "risk": "low",
            "performance": "high",
            "pros": ["ACID", "Mature", "Stable"],
            "cons": ["Resource intensive"],
        },
        {
            "text": "MongoDB",
            "risk": "medium",
            "performance": "high",
            "pros": ["Flexible schema", "Fast writes"],
            "cons": ["No ACID guarantees"],
        },
        {
            "text": "Redis",
            "risk": "high",
            "performance": "very_high",
            "pros": ["Extremely fast", "In-memory"],
            "cons": ["Data persistence concerns"],
        },
    ]
    
    # Make decision
    result = decision_maker.make_decision(
        context="Choose database for production financial application",
        options=options,
        decision_type=DecisionType.TECH_CHOICE,
    )
    
    print("Conservative User Decision:")
    print(f"  Selected: {result['decision']['text']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Reasoning: {result['reasoning']}")
    print(f"  Soul Rules Applied: {result['soul_rules_applied']}")
    
    # Expected: PostgreSQL (low risk)
    assert result['decision']['text'] == "PostgreSQL"
    
    return result


def example_aggressive_tech_choice():
    """Example: Aggressive user choosing database."""
    
    # Aggressive user profile (high risk tolerance)
    soul_meta = {
        "traits": {
            "risk_tolerance": 85,  # Very aggressive
            "structure": 50,
            "detail_orientation": 50,
        }
    }
    
    decision_maker = ExtendedProxyDecisionMaker(soul_meta)
    
    # Same technology options
    options = [
        {
            "text": "PostgreSQL",
            "risk": "low",
            "performance": "high",
        },
        {
            "text": "MongoDB",
            "risk": "medium",
            "performance": "high",
        },
        {
            "text": "Redis",
            "risk": "high",
            "performance": "very_high",
        },
    ]
    
    # Make decision
    result = decision_maker.make_decision(
        context="Choose database for high-performance caching layer",
        options=options,
        decision_type=DecisionType.TECH_CHOICE,
    )
    
    print("\nAggressive User Decision:")
    print(f"  Selected: {result['decision']['text']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Reasoning: {result['reasoning']}")
    
    # Expected: Redis (high performance, acceptable risk for aggressive user)
    assert result['decision']['text'] == "Redis"
    
    return result


def example_balanced_tech_choice():
    """Example: Balanced user choosing database."""
    
    # Balanced user profile
    soul_meta = {
        "traits": {
            "risk_tolerance": 50,  # Balanced
            "structure": 50,
            "detail_orientation": 50,
        }
    }
    
    decision_maker = ExtendedProxyDecisionMaker(soul_meta)
    
    options = [
        {"text": "PostgreSQL", "risk": "low"},
        {"text": "MongoDB", "risk": "medium"},
        {"text": "Redis", "risk": "high"},
    ]
    
    result = decision_maker.make_decision(
        context="Choose database for general web application",
        options=options,
        decision_type=DecisionType.TECH_CHOICE,
    )
    
    print("\nBalanced User Decision:")
    print(f"  Selected: {result['decision']['text']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Reasoning: {result['reasoning']}")
    
    # Expected: MongoDB (medium risk, balanced choice)
    assert result['decision']['text'] == "MongoDB"
    
    return result


def example_with_high_stakes():
    """Example: High-stakes decision requires human confirmation."""
    
    soul_meta = {
        "traits": {
            "risk_tolerance": 50,
        }
    }
    
    decision_maker = ExtendedProxyDecisionMaker(soul_meta)
    
    options = [
        {"text": "Option A", "risk": "low"},
        {"text": "Option B", "risk": "medium"},
    ]
    
    # High-stakes context (financial decision)
    result = decision_maker.make_decision(
        context="Choose payment processing system for financial application",
        options=options,
        decision_type=DecisionType.TECH_CHOICE,
    )
    
    print("\nHigh-Stakes Decision:")
    print(f"  Selected: {result['decision']['text']}")
    print(f"  Requires Human: {result['requires_human']}")
    print(f"  Reasoning: {result['reasoning']}")
    
    # High-stakes decisions should require human confirmation
    assert result['requires_human'] == True
    
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Technology Choice Examples")
    print("=" * 60)
    
    example_conservative_tech_choice()
    example_aggressive_tech_choice()
    example_balanced_tech_choice()
    example_with_high_stakes()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
