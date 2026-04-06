#!/usr/bin/env python3
"""Complete verification and fix for Phoenix tracing."""

import sys
import time
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from cinder_cli.tracing.config import TracingConfig
from cinder_cli.tracing.phoenix_tracer import PhoenixTracer
from cinder_cli.tracing.llm_tracer import LLMTracer

print("="*60)
print("Complete Phoenix Tracing Verification")
print("="*60)

print(f"\n1. Creating TracingConfig...")
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

print(f"\n2. Initializing PhoenixTracer...")
phoenix_tracer = PhoenixTracer(config, service_name="cinder")

print(f"\n3. Creating LLMTracer...")
llm_tracer = LLMTracer(phoenix_tracer)

print(f"\n4. Creating test LLM call with complete attributes...")
with llm_tracer.trace_llm_call(
    model="qwen3.5:0.8b",
    prompt="Write a Python function to calculate fibonacci",
    system_prompt="You are a helpful coding assistant.",
    agent_id="test-agent",
    phase="code_generation",
    temperature=0.7,
) as record:
    print(f"   Span created, recording response...")
    time.sleep(0.2)
    
    llm_tracer.record_response(
        record,
        response="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        input_tokens=50,
        output_tokens=100,
    )

print(f"\n5. Waiting for data to be exported...")
time.sleep(3)

print(f"\n6. Force flushing...")
if phoenix_tracer.tracer_provider:
    phoenix_tracer.tracer_provider.force_flush()
    time.sleep(2)

print(f"\n✓ Test completed!")

print(f"\n现在请：")
print(f"1. 在浏览器中打开 http://localhost:6006")
print(f"2. 选择 'cinder' 项目")
print(f"3. 查看最新的 trace")
print(f"4. 检查 span 的属性是否包含：")
print(f"   - openinference.span.kind: LLM")
print(f"   - llm.input_messages")
print(f"   - llm.output_messages")
print(f"   - llm.token_count.*")
