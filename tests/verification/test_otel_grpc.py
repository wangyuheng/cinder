#!/usr/bin/env python3
"""Test OpenTelemetry exporter with gRPC."""

import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

print("="*60)
print("Testing OpenTelemetry gRPC Exporter to Phoenix")
print("="*60)

PHOENIX_GRPC_ENDPOINT = "localhost:4317"

print(f"\n1. Creating Resource with service.name='cinder-test'")
resource = Resource(attributes={
    SERVICE_NAME: "cinder-test",
    "service.version": "1.0.0",
})

print(f"\n2. Creating TracerProvider with resource")
provider = TracerProvider(resource=resource)

print(f"\n3. Creating OTLP gRPC Exporter")
print(f"   Endpoint: {PHOENIX_GRPC_ENDPOINT}")
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    
    exporter = OTLPSpanExporter(
        endpoint=PHOENIX_GRPC_ENDPOINT,
        insecure=True
    )
    
    print(f"   ✓ Created gRPC exporter")
    
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("cinder-test")
    
    print(f"\n4. Creating test span with attributes")
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
        print(f"   Span ID: {span.context.span_id}")
        print(f"   Trace ID: {span.context.trace_id}")
        time.sleep(0.1)
    
    print(f"\n5. Span ended, waiting for export...")
    time.sleep(2)
    
    print(f"\n6. Force flushing provider")
    provider.force_flush()
    
    print(f"\n✓ Test completed successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python check_phoenix_data.py")
