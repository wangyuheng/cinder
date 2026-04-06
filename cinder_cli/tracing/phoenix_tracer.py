"""
Phoenix Tracer - OpenTelemetry tracer integration with Phoenix.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from opentelemetry import trace

from .config import TracingConfig


logger = logging.getLogger(__name__)


class PhoenixTracer:
    """
    Phoenix Tracer - Manages OpenTelemetry tracing with Phoenix backend.
    
    This class provides a unified interface for tracing LLM calls and Agent behavior
    using OpenTelemetry standard and Phoenix as the visualization backend.
    """
    
    _instance: Optional[PhoenixTracer] = None
    
    def __init__(self, config: TracingConfig, service_name: str = "cinder-cli"):
        """
        Initialize Phoenix Tracer.
        
        Args:
            config: Tracing configuration
            service_name: Service name for OpenTelemetry resource
        """
        self.config = config
        self.service_name = service_name
        self.tracer: Optional[trace.Tracer] = None
        self.tracer_provider = None
        
        if config.enabled:
            self.tracer = self._init_tracer()
    
    def _init_tracer(self) -> trace.Tracer:
        """
        Initialize OpenTelemetry tracer with Phoenix backend using arize-phoenix-otel.
        
        Returns:
            OpenTelemetry Tracer instance
        """
        try:
            # Set environment variables for Phoenix
            endpoint = self.config.get_phoenix_endpoint()
            os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = endpoint
            os.environ["PHOENIX_PROJECT_NAME"] = "cinder"
            
            # Use arize-phoenix-otel for proper Phoenix integration
            from phoenix.otel import register
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            
            self.tracer_provider = register(
                project_name="cinder",
                endpoint=f"{endpoint}/v1/traces",
                set_global_tracer_provider=True,
                batch=True,  # Use BatchSpanProcessor for production
                verbose=False,  # Disable verbose logging
            )
            
            tracer = trace.get_tracer("cinder")
            
            logger.info(f"OpenTelemetry tracer initialized with Phoenix endpoint: {endpoint} (using BatchSpanProcessor)")
            
            return tracer
            
        except ImportError:
            logger.warning("arize-phoenix-otel not installed, falling back to standard OTLP")
            return self._init_tracer_fallback()
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry tracer: {e}")
            return None
    
    def _init_tracer_fallback(self) -> trace.Tracer:
        """
        Fallback initialization using standard OTLP exporter.
        
        Returns:
            OpenTelemetry Tracer instance
        """
        try:
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import Resource, SERVICE_NAME
            
            resource = Resource(attributes={
                SERVICE_NAME: "cinder",
                "service.version": "3.0.0",
                "deployment.environment": "development",
                "service.namespace": "cinder-cli",
            })
            
            provider = TracerProvider(resource=resource)
            
            endpoint = self.config.get_phoenix_endpoint()
            otlp_endpoint = f"{endpoint}/v1/traces"
            
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
            
            trace.set_tracer_provider(provider)
            self.tracer_provider = provider
            
            tracer = trace.get_tracer("cinder")
            
            logger.info(f"OpenTelemetry tracer initialized with OTLP HTTP endpoint: {otlp_endpoint}")
            
            return tracer
            
        except Exception as e:
            logger.error(f"Failed to initialize fallback tracer: {e}")
            return None
    
    @classmethod
    def get_instance(cls) -> Optional[PhoenixTracer]:
        """
        Get global PhoenixTracer instance.
        
        Returns:
            PhoenixTracer instance or None
        """
        return cls._instance
    
    @classmethod
    def initialize(cls, config: TracingConfig, service_name: str = "cinder-cli") -> PhoenixTracer:
        """
        Initialize global PhoenixTracer instance.
        
        Args:
            config: Tracing configuration
            service_name: Service name for OpenTelemetry resource
            
        Returns:
            PhoenixTracer instance
        """
        if cls._instance is None:
            cls._instance = cls(config, service_name)
        
        return cls._instance
    
    def is_enabled(self) -> bool:
        """
        Check if tracing is enabled.
        
        Returns:
            True if tracing is enabled
        """
        return self.config.enabled and self.tracer is not None
    
    def should_sample(self) -> bool:
        """
        Determine if this trace should be sampled based on sample rate.
        
        Returns:
            True if this trace should be sampled
        """
        if not self.is_enabled():
            return False
        
        import random
        return random.random() < self.config.sample_rate


def get_tracer() -> Optional[PhoenixTracer]:
    """
    Get global PhoenixTracer instance.
    
    Returns:
        PhoenixTracer instance or None
    """
    return PhoenixTracer.get_instance()


def init_tracing(config: TracingConfig, service_name: str = "cinder-cli") -> PhoenixTracer:
    """
    Initialize global tracing.
    
    Args:
        config: Tracing configuration
        service_name: Service name for OpenTelemetry resource
        
    Returns:
        PhoenixTracer instance
    """
    return PhoenixTracer.initialize(config, service_name)
