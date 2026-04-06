#!/usr/bin/env python3
"""Test updated LLMTracer with OpenInference attributes."""

import sys
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from cinder_cli.tracing.config import TracingConfig
from cinder_cli.tracing.phoenix_tracer import PhoenixTracer
from cinder_cli.tracing.llm_tracer import LLMTracer
import time

print("="*60)
print("Testing Updated LLMTracer with OpenInference Attributes")
print("="*60)

print(f"\n1. Creating TracingConfig...")
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

print(f"\n2. Initializing PhoenixTracer...")
phoenix_tracer = PhoenixTracer(config, service_name="cinder-test")

print(f"\n3. Creating LLMTracer...")
llm_tracer = LLMTracer(phoenix_tracer)

print(f"\n4. Creating test LLM call...")
with llm_tracer.trace_llm_call(
    model="qwen3.5:0.8b",
    prompt="Write a Python function to calculate fibonacci",
    system_prompt="You are a helpful coding assistant.",
    agent_id="test-agent",
    phase="code_generation",
    temperature=0.7,
) as record:
    print(f"   Span created")
    time.sleep(0.1)
    
    # Simulate LLM response
    llm_tracer.record_response(
        record,
        response="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        input_tokens=50,
        output_tokens=100,
    )

print(f"\n5. Force flushing...")
if phoenix_tracer.tracer_provider:
    phoenix_tracer.tracer_provider.force_flush()

print(f"\n✓ Test completed!")

print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python verify_openinference_attributes.py")
