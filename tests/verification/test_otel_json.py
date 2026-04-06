#!/usr/bin/env python3
"""Test OpenTelemetry exporter with JSON format."""

import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

print("="*60)
print("Testing OpenTelemetry Exporter with JSON format")
print("="*60)

PHOENIX_ENDPOINT = "http://localhost:6006"

print(f"\n1. Creating Resource with service.name='cinder-test'")
resource = Resource(attributes={
    SERVICE_NAME: "cinder-test",
    "service.version": "1.0.0",
})

print(f"\n2. Creating TracerProvider with resource")
provider = TracerProvider(resource=resource)

print(f"\n3. Trying different exporter configurations...")

# Try 1: OTLP HTTP with default (protobuf)
print(f"\n   [Try 1] OTLP HTTP Exporter (default protobuf)")
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    exporter = OTLPSpanExporter(endpoint=f"{PHOENIX_ENDPOINT}/v1/traces")
    print(f"   ✓ Created exporter")
    
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("cinder-test")
    
    with tracer.start_as_current_span(
        "test.span.protobuf",
        kind=trace.SpanKind.CLIENT,
        attributes={"test": "protobuf"}
    ) as span:
        pass
    
    provider.force_flush()
    print(f"   ✓ Exported with protobuf format")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Try 2: OTLP HTTP with JSON
print(f"\n   [Try 2] OTLP HTTP Exporter (JSON)")
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    import os
    os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = "Content-Type=application/json"
    
    provider2 = TracerProvider(resource=resource)
    exporter2 = OTLPSpanExporter(
        endpoint=f"{PHOENIX_ENDPOINT}/v1/traces",
        headers={"Content-Type": "application/json"}
    )
    processor2 = SimpleSpanProcessor(exporter2)
    provider2.add_span_processor(processor2)
    
    trace.set_tracer_provider(provider2)
    tracer2 = trace.get_tracer("cinder-test-json")
    
    with tracer2.start_as_current_span(
        "test.span.json",
        kind=trace.SpanKind.CLIENT,
        attributes={"test": "json"}
    ) as span:
        pass
    
    provider2.force_flush()
    print(f"   ✓ Exported with JSON format")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Try 3: Check Phoenix OTLP endpoint
print(f"\n   [Try 3] Check Phoenix OTLP endpoint")
import requests
try:
    response = requests.get(f"{PHOENIX_ENDPOINT}/v1/traces")
    print(f"   GET /v1/traces: {response.status_code}")
    print(f"   Content: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print(f"\n✓ Test completed!")
print(f"\n现在检查 Phoenix 数据库：")
print(f"  docker cp cinder-phoenix:/root/.phoenix/phoenix.db /tmp/phoenix.db")
print(f"  python check_phoenix_data.py")
