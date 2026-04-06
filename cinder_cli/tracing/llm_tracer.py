"""
LLM Tracer - Traces LLM calls with detailed information.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .phoenix_tracer import PhoenixTracer


@dataclass
class LLMCallRecord:
    """Record of a single LLM call."""
    
    call_id: str
    model: str
    prompt: str
    response: str = ""
    system_prompt: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    duration_ms: float = 0.0
    model_params: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    estimated_cost: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMTracer:
    """Tracer for LLM calls with OpenTelemetry integration."""
    
    def __init__(self, phoenix_tracer: Optional[PhoenixTracer] = None):
        """
        Initialize LLM Tracer.
        
        Args:
            phoenix_tracer: PhoenixTracer instance for OpenTelemetry integration
        """
        self.phoenix_tracer = phoenix_tracer
        self._call_records: list[LLMCallRecord] = []
    
    @contextmanager
    def trace_llm_call(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_params: Optional[dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        phase: str = "unknown",
        **metadata: Any,
    ) -> Iterator[LLMCallRecord]:
        """
        Trace an LLM call with OpenTelemetry.
        
        Args:
            model: Model name (e.g., "gpt-4", "qwen3.5:0.8b")
            prompt: User prompt content
            system_prompt: System prompt content (optional)
            model_params: Model parameters (optional)
            agent_id: Agent ID making the call (optional)
            phase: Execution phase (e.g., code_generation, goal_understanding)
            **metadata: Additional metadata
            
        Yields:
            LLMCallRecord instance
        """
        call_id = f"call_{int(time.time() * 1000)}"
        start_time = time.time()
        
        record = LLMCallRecord(
            call_id=call_id,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            model_params=model_params or {},
            metadata={"agent_id": agent_id, "phase": phase, **metadata},
        )
        
        if self.phoenix_tracer and self.phoenix_tracer.is_enabled():
            span_name = f"llm.{model}.{phase}"
            
            attributes = {
                "openinference.span.kind": "LLM",
                "llm.system": "ollama",
                "llm.model_name": model,
                "cinder.phase": phase,
                "agent.id": agent_id or "unknown",
            }
            
            # Build input messages with flattened attributes
            message_index = 0
            if system_prompt:
                attributes[f"llm.input_messages.{message_index}.message.role"] = "system"
                attributes[f"llm.input_messages.{message_index}.message.content"] = system_prompt
                message_index += 1
            
            if prompt:
                attributes[f"llm.input_messages.{message_index}.message.role"] = "user"
                attributes[f"llm.input_messages.{message_index}.message.content"] = prompt
            
            if model_params:
                for key, value in model_params.items():
                    attributes[f"llm.{key}"] = value
            
            for key, value in metadata.items():
                if value is not None:
                    attributes[f"cinder.{key}"] = value
            
            with self.phoenix_tracer.tracer.start_as_current_span(
                span_name,
                kind=trace.SpanKind.CLIENT,
                attributes=attributes,
            ) as span:
                try:
                    yield record
                    record.duration_ms = (time.time() - start_time) * 1000
                    
                    if record.response:
                        span.set_attribute("llm.output_messages.0.message.role", "assistant")
                        span.set_attribute("llm.output_messages.0.message.content", record.response)
                        span.set_attribute("output.value", record.response)
                    
                    if record.input_tokens > 0:
                        span.set_attribute("llm.token_count.prompt", record.input_tokens)
                    if record.output_tokens > 0:
                        span.set_attribute("llm.token_count.completion", record.output_tokens)
                    if record.total_tokens > 0:
                        span.set_attribute("llm.token_count.total", record.total_tokens)
                    
                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    record.error = str(e)
                    raise
        else:
            yield record
            record.duration_ms = (time.time() - start_time) * 1000
        
        self._call_records.append(record)
    
    def record_response(
        self,
        record: LLMCallRecord,
        response: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        Record LLM response details.
        
        Args:
            record: LLMCallRecord instance
            response: Response content
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        record.response = response
        record.input_tokens = input_tokens
        record.output_tokens = output_tokens
        record.total_tokens = input_tokens + output_tokens
    
    def get_call_records(self) -> list[LLMCallRecord]:
        """
        Get all LLM call records.
        
        Returns:
            List of LLMCallRecord instances
        """
        return self._call_records.copy()
    
    def clear_records(self) -> None:
        """Clear all LLM call records."""
        self._call_records.clear()
