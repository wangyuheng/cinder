#!/usr/bin/env python3
"""Test updated PhoenixTracer."""

import sys
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from cinder_cli.tracing.config import TracingConfig
from cinder_cli.tracing.phoenix_tracer import PhoenixTracer
import time

print("="*60)
print("Testing Updated PhoenixTracer")
print("="*60)

print(f"\n1. Creating TracingConfig...")
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

print(f"\n2. Initializing PhoenixTracer...")
tracer = PhoenixTracer(config, service_name="cinder-test")

print(f"\n3. Checking if tracer is enabled: {tracer.is_enabled()}")

if tracer.tracer:
    print(f"\n4. Creating test span...")
    
    from opentelemetry import trace as trace_api
    
    with tracer.tracer.start_as_current_span(
        "llm.qwen3.5:0.8b.test_with_arize",
        kind=trace_api.SpanKind.CLIENT,
        attributes={
            "llm.system": "ollama",
            "llm.model": "qwen3.5:0.8b",
            "llm.prompt": "Test prompt with arize-phoenix-otel",
            "llm.response": "Test response with arize-phoenix-otel",
            "llm.usage.total_tokens": 100,
            "cinder.phase": "test",
        }
    ) as span:
        print(f"   Span created: {span.name}")
        print(f"   Span ID: {span.context.span_id}")
        print(f"   Trace ID: {span.context.trace_id}")
        time.sleep(0.1)
    
    print(f"\n5. Force flushing...")
    if tracer.tracer_provider:
        tracer.tracer_provider.force_flush()
    
    print(f"\n✓ Test completed!")
else:
    print(f"\n✗ Tracer not initialized")

print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python check_latest_spans.py")
