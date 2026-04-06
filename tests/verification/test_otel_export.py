#!/usr/bin/env python3
"""Test OpenTelemetry exporter to Phoenix."""

import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

print("="*60)
print("Testing OpenTelemetry Exporter to Phoenix")
print("="*60)

PHOENIX_ENDPOINT = "http://localhost:6006"

print(f"\n1. Creating Resource with service.name='cinder-test'")
resource = Resource(attributes={
    SERVICE_NAME: "cinder-test",
    "service.version": "1.0.0",
    "deployment.environment": "development",
})

print(f"\n2. Creating TracerProvider with resource")
provider = TracerProvider(resource=resource)

print(f"\n3. Creating OTLP HTTP Exporter")
print(f"   Endpoint: {PHOENIX_ENDPOINT}/v1/traces")
exporter = OTLPSpanExporter(endpoint=f"{PHOENIX_ENDPOINT}/v1/traces")

print(f"\n4. Adding SimpleSpanProcessor")
processor = SimpleSpanProcessor(exporter)
provider.add_span_processor(processor)

print(f"\n5. Setting global TracerProvider")
trace.set_tracer_provider(provider)

print(f"\n6. Getting tracer")
tracer = trace.get_tracer("cinder-test")

print(f"\n7. Creating test span with attributes")
with tracer.start_as_current_span(
    "llm.qwen3.5:0.8b.code_generation",
    kind=trace.SpanKind.CLIENT,
    attributes={
        "llm.system": "ollama",
        "llm.model": "qwen3.5:0.8b",
        "llm.request.type": "completion",
        "llm.prompt": "Write a Python function to calculate fibonacci",
        "llm.prompt.length": 50,
        "llm.response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        "llm.response.length": 100,
        "llm.usage.total_tokens": 150,
        "llm.usage.prompt_tokens": 50,
        "llm.usage.completion_tokens": 100,
        "cinder.phase": "code_generation",
    }
) as span:
    print(f"   Span ID: {span.context.span_id}")
    print(f"   Trace ID: {span.context.trace_id}")
    print(f"   Span Name: {span.name}")
    print(f"   Span Kind: {span.kind}")
    time.sleep(0.1)

print(f"\n8. Span ended, waiting for export...")
time.sleep(2)

print(f"\n9. Force flushing provider")
provider.force_flush()

print(f"\n10. Shutting down provider")
provider.shutdown()

print(f"\n✓ Test completed!")
print(f"\n现在检查 Phoenix 数据库是否有数据：")
print(f"  python check_phoenix_data.py")
