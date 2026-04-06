#!/usr/bin/env python3
"""Test OpenTelemetry connection to Phoenix."""

import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

print("Testing OpenTelemetry connection to Phoenix...")
print("="*60)

# 1. Create resource
print("\n1. Creating OpenTelemetry resource...")
resource = Resource(attributes={
    SERVICE_NAME: "test-service",
    "service.version": "1.0.0",
})
print(f"✓ Resource created: {resource.attributes}")

# 2. Create tracer provider
print("\n2. Creating tracer provider...")
provider = TracerProvider(resource=resource)
print("✓ Tracer provider created")

# 3. Create OTLP exporter
print("\n3. Creating OTLP gRPC exporter...")
otlp_endpoint = "localhost:4317"
print(f"   Endpoint: {otlp_endpoint}")

try:
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    print("✓ OTLP exporter created")
except Exception as e:
    print(f"✗ Failed to create exporter: {e}")
    exit(1)

# 4. Add span processor
print("\n4. Adding span processor...")
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
print("✓ Span processor added")

# 5. Set tracer provider
print("\n5. Setting tracer provider...")
trace.set_tracer_provider(provider)
print("✓ Tracer provider set")

# 6. Get tracer
print("\n6. Getting tracer...")
tracer = trace.get_tracer(__name__)
print("✓ Tracer obtained")

# 7. Create a test span
print("\n7. Creating test span...")
with tracer.start_as_current_span("test-span") as span:
    span.set_attribute("test.attribute", "test-value")
    span.set_attribute("test.number", 42)
    print("✓ Test span created and attributes set")

# 8. Force flush
print("\n8. Force flushing spans...")
provider.force_flush()
print("✓ Spans flushed")

# 9. Wait for export
print("\n9. Waiting for export...")
time.sleep(2)
print("✓ Wait complete")

print("\n" + "="*60)
print("✓ Test complete!")
print("\nCheck Phoenix UI: http://localhost:6006")
print("Look for spans in the 'Tracing' section")
