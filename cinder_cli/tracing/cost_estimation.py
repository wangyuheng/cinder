"""
Cost Estimation - Estimates LLM API costs.
"""

from __future__ import annotations

from typing import Optional


MODEL_PRICING = {
    "gpt-4": {
        "input": 0.03 / 1000,
        "output": 0.06 / 1000,
    },
    "gpt-4-turbo": {
        "input": 0.01 / 1000,
        "output": 0.03 / 1000,
    },
    "gpt-3.5-turbo": {
        "input": 0.0015 / 1000,
        "output": 0.002 / 1000,
    },
    "claude-3-opus": {
        "input": 0.015 / 1000,
        "output": 0.075 / 1000,
    },
    "claude-3-sonnet": {
        "input": 0.003 / 1000,
        "output": 0.015 / 1000,
    },
    "claude-3-haiku": {
        "input": 0.00025 / 1000,
        "output": 0.00125 / 1000,
    },
    "qwen3.5:0.8b": {
        "input": 0.0,
        "output": 0.0,
    },
    "qwen3.5:1.8b": {
        "input": 0.0,
        "output": 0.0,
    },
    "qwen3.5:7b": {
        "input": 0.0,
        "output": 0.0,
    },
}


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> Optional[float]:
    """
    Estimate the cost of an LLM API call.
    
    Args:
        model: Model name (e.g., "gpt-4", "qwen3.5:0.8b")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Estimated cost in USD, or None if model not found
    """
    model_lower = model.lower()
    
    for model_key, pricing in MODEL_PRICING.items():
        if model_key.lower() in model_lower or model_lower in model_key.lower():
            input_cost = input_tokens * pricing["input"]
            output_cost = output_tokens * pricing["output"]
            return input_cost + output_cost
    
    return None


def format_cost(cost: Optional[float]) -> str:
    """
    Format cost for display.
    
    Args:
        cost: Cost in USD
        
    Returns:
        Formatted cost string
    """
    if cost is None:
        return "Unknown"
    
    if cost < 0.01:
        return f"${cost:.6f}"
    elif cost < 1.0:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"
