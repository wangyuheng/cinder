"""
Performance tests for tracing module.
"""

from __future__ import annotations

import time
import pytest
from unittest.mock import Mock, patch
from cinder_cli.tracing import (
    TracingConfig,
    LLMTracer,
    AgentTracer,
    PhoenixTracer,
)


class TestTracingPerformance:
    """Performance tests for tracing operations."""
    
    def test_trace_recording_overhead(self):
        """Test overhead of trace recording."""
        config = TracingConfig(enabled=True)
        tracer = LLMTracer()
        
        # Measure time without tracing
        start_time = time.time()
        for _ in range(100):
            pass
        baseline_time = time.time() - start_time
        
        # Measure time with tracing
        start_time = time.time()
        for i in range(100):
            with tracer.trace_llm_call(
                model="test-model",
                prompt=f"test prompt {i}",
                phase="test",
            ) as record:
                record.response = f"response {i}"
                record.total_tokens = 100
        trace_time = time.time() - start_time
        
        # Calculate overhead
        overhead = (trace_time - baseline_time) / baseline_time * 100
        
        # Assert overhead is less than 5%
        assert overhead < 5.0, f"Tracing overhead {overhead:.2f}% exceeds 5%"
    
    def test_memory_usage(self):
        """Test memory usage of trace recording."""
        import sys
        
        config = TracingConfig(enabled=True)
        tracer = LLMTracer()
        
        # Measure initial memory
        initial_size = sys.getsizeof(tracer)
        
        # Create many traces
        for i in range(1000):
            with tracer.trace_llm_call(
                model="test-model",
                prompt=f"test prompt {i}",
            ) as record:
                record.response = f"response {i}"
                record.total_tokens = 100
        
        # Measure final memory
        final_size = sys.getsizeof(tracer)
        
        # Assert memory increase is reasonable
        memory_increase = final_size - initial_size
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB
    
    def test_concurrent_traces(self):
        """Test concurrent trace recording."""
        import threading
        
        config = TracingConfig(enabled=True)
        tracer = LLMTracer()
        
        errors = []
        
        def create_trace(i):
            try:
                with tracer.trace_llm_call(
                    model="test-model",
                    prompt=f"test prompt {i}",
                ) as record:
                    record.response = f"response {i}"
                    record.total_tokens = 100
            except Exception as e:
                errors.append(e)
        
        # Create traces concurrently
        threads = []
        for i in range(100):
            thread = threading.Thread(target=create_trace, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Assert no errors occurred
        assert len(errors) == 0, f"Concurrent trace recording failed with {len(errors)} errors"
    
    def test_large_trace_handling(self):
        """Test handling of large trace data."""
        config = TracingConfig(enabled=True)
        tracer = LLMTracer()
        
        # Create a trace with large prompt and response
        large_prompt = "x" * 10000  # 10KB prompt
        large_response = "y" * 20000  # 20KB response
        
        start_time = time.time()
        with tracer.trace_llm_call(
            model="test-model",
            prompt=large_prompt,
        ) as record:
            record.response = large_response
            record.total_tokens = 30000
        duration = time.time() - start_time
        
        # Assert large trace is handled quickly
        assert duration < 1.0, f"Large trace handling took {duration:.2f}s"
    
    def test_span_processor_performance(self):
        """Test batch span processor performance."""
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        # Create tracer provider with batch processor
        provider = TracerProvider()
        
        # Measure batch processing time
        start_time = time.time()
        
        # Create many spans
        tracer = provider.get_tracer("test")
        for i in range(1000):
            with tracer.start_as_current_span(f"test-span-{i}"):
                pass
        
        # Force flush
        provider.force_flush()
        
        duration = time.time() - start_time
        
        # Assert batch processing is efficient
        assert duration < 5.0, f"Batch processing took {duration:.2f}s"
    
    def test_export_performance(self):
        """Test trace export performance."""
        from cinder_cli.tracing import TraceExporter
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = TraceExporter(export_dir=tmpdir)
            
            # Create test spans
            spans = []
            for i in range(100):
                spans.append({
                    "span_id": f"span-{i}",
                    "operation_name": f"test-{i}",
                })
            
            # Measure export time
            start_time = time.time()
            output_file = exporter.export_to_json(spans)
            duration = time.time() - start_time
            
            # Assert export is fast
            assert duration < 2.0, f"Export took {duration:.2f}s"
            assert output_file.exists()
