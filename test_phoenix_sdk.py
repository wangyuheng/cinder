#!/usr/bin/env python3
"""Test Phoenix SDK directly."""

import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
import time

print("="*60)
print("Testing Phoenix SDK Direct Recording")
print("="*60)

print(f"\n1. Initializing Phoenix session...")
try:
    session = px.launch_app()
    print(f"   ✓ Phoenix session launched")
    print(f"   View at: {session.url}")
except Exception as e:
    print(f"   Note: {e}")
    print(f"   Continuing with existing Phoenix instance...")

print(f"\n2. Using Phoenix's OpenTelemetry tracer...")
try:
    from phoenix.trace.opentelemetry import TracerProvider as PhoenixTracerProvider
    
    resource = Resource.create({
        "service.name": "cinder-sdk-test",
        "service.version": "1.0.0",
    })
    
    provider = PhoenixTracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    
    tracer = trace.get_tracer(__name__)
    
    print(f"   ✓ Created Phoenix tracer")
    
    print(f"\n3. Creating test span...")
    with tracer.start_as_current_span(
        "llm.qwen3.5:0.8b.test",
        kind=trace.SpanKind.CLIENT,
        attributes={
            "llm.system": "ollama",
            "llm.model": "qwen3.5:0.8b",
            "llm.prompt": "test prompt",
            "llm.response": "test response",
        }
    ) as span:
        print(f"   Span created: {span.name}")
        time.sleep(0.1)
    
    print(f"\n4. Force flushing...")
    provider.force_flush()
    
    print(f"\n✓ Test completed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python check_phoenix_data.py")
