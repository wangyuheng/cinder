#!/usr/bin/env python3
"""Test trace data export to Phoenix."""

from cinder_cli.tracing import LLMTracer, TracingConfig

# Initialize tracer
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

tracer = LLMTracer()

# Create a test trace
with tracer.trace_llm_call(
    model="test-model",
    prompt="Hello, this is a test",
    system_prompt="You are a test assistant",
    model_params={"temperature": 0.7},
) as record:
    record.response = "This is a test response"
    record.input_tokens = 10
    record.output_tokens = 20
    record.total_tokens = 30

print("✓ Test trace created successfully!")
print(f"  Call ID: {record.call_id}")
print(f"  Model: {record.model}")
print(f"  Tokens: {record.total_tokens}")

# Check Phoenix
print("\nCheck Phoenix UI: http://localhost:6006")
print("Look for the trace in the 'traces' section")
