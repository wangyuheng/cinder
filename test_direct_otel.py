#!/usr/bin/env python3
"""Direct OpenTelemetry test to Phoenix."""

import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

print("Testing direct OpenTelemetry to Phoenix...")
print("="*60)

# Create resource
resource = Resource.create({
    "service.name": "test-direct",
    "service.version": "1.0.0",
})

# Create provider
provider = TracerProvider(resource=resource)

# Create HTTP exporter
exporter = OTLPSpanExporter(
    endpoint="http://localhost:6006/v1/traces",
)

# Use SimpleSpanProcessor for immediate export
processor = SimpleSpanProcessor(exporter)
provider.add_span_processor(processor)

# Set global provider
trace.set_tracer_provider(provider)

# Get tracer
tracer = trace.get_tracer(__name__)

# Create span
print("\nCreating span...")
with tracer.start_as_current_span("test-direct-span") as span:
    span.set_attribute("test.key", "test-value")
    span.set_attribute("test.number", 42)
    print("✓ Span created")

# Force flush
print("\nForce flushing...")
provider.force_flush()
print("✓ Flush complete")

# Wait
print("\nWaiting 2 seconds...")
time.sleep(2)
print("✓ Done")

print("\n" + "="*60)
print("Check Phoenix UI: http://localhost:6006")
print("Look for 'test-direct' service")
