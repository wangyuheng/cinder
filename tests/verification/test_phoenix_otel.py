#!/usr/bin/env python3
"""Test Phoenix OTel package."""

import os
import time

print("="*60)
print("Testing arize-phoenix-otel Package")
print("="*60)

os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"
os.environ["PHOENIX_PROJECT_NAME"] = "cinder"

print(f"\n1. Setting environment variables:")
print(f"   PHOENIX_COLLECTOR_ENDPOINT: {os.environ['PHOENIX_COLLECTOR_ENDPOINT']}")
print(f"   PHOENIX_PROJECT_NAME: {os.environ['PHOENIX_PROJECT_NAME']}")

print(f"\n2. Importing arize-phoenix-otel...")
try:
    from phoenix.otel import register
    
    print(f"   ✓ Imported successfully")
    
    print(f"\n3. Registering tracer provider...")
    tracer_provider = register(
        project_name="cinder",
        endpoint="http://localhost:6006/v1/traces",
    )
    
    print(f"   ✓ Registered successfully")
    
    print(f"\n4. Getting tracer...")
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    
    print(f"   ✓ Got tracer")
    
    print(f"\n5. Creating test span...")
    with tracer.start_as_current_span(
        "llm.qwen3.5:0.8b.code_generation",
        kind=trace.SpanKind.CLIENT,
        attributes={
            "llm.system": "ollama",
            "llm.model": "qwen3.5:0.8b",
            "llm.request.type": "completion",
            "llm.prompt": "Write a Python function to calculate fibonacci",
            "llm.response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "llm.usage.total_tokens": 150,
            "cinder.phase": "code_generation",
        }
    ) as span:
        print(f"   Span created: {span.name}")
        print(f"   Span ID: {span.context.span_id}")
        print(f"   Trace ID: {span.context.trace_id}")
        time.sleep(0.1)
    
    print(f"\n6. Force flushing...")
    tracer_provider.force_flush()
    
    print(f"\n✓ Test completed successfully!")
    
except ImportError as e:
    print(f"\n✗ arize-phoenix-otel not installed")
    print(f"   Install with: pip install arize-phoenix-otel")
    print(f"   Error: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python check_phoenix_data.py")
