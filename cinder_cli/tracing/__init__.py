"""
Tracing Module - Unified tracing initialization and utilities.
"""

from __future__ import annotations

from typing import Optional

from .agent_tracer import AgentTracer
from .config import TracingConfig
from .llm_tracer import LLMTracer
from .phoenix_server import PhoenixServer
from .phoenix_tracer import PhoenixTracer


def init_tracing_from_config(config: dict) -> tuple[PhoenixTracer, LLMTracer, AgentTracer]:
    """
    Initialize tracing from configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (PhoenixTracer, LLMTracer, AgentTracer)
    """
    tracing_config = TracingConfig.from_dict(config)
    
    phoenix_tracer = PhoenixTracer.initialize(tracing_config)
    llm_tracer = LLMTracer(phoenix_tracer)
    agent_tracer = AgentTracer(phoenix_tracer)
    
    return phoenix_tracer, llm_tracer, agent_tracer


__all__ = [
    "TracingConfig",
    "PhoenixTracer",
    "PhoenixServer",
    "LLMTracer",
    "AgentTracer",
    "init_tracing_from_config",
]
