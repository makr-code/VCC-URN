# VCC-URN OpenTelemetry Integration
# ===================================
# Distributed tracing for the federal URN resolver infrastructure
# On-premise compatible with Jaeger as the default backend

"""
OpenTelemetry Module for VCC-URN

Provides distributed tracing capabilities:
- Request tracing across federation peers
- Performance monitoring
- Error tracking

Backends supported (all on-premise, Open-Source):
- Jaeger (recommended)
- Zipkin
- OTLP-compatible collectors

This is an optional module - if OpenTelemetry is not installed,
the application continues to work without tracing.
"""

import os
from typing import Optional, Dict, Any
from functools import wraps

from vcc_urn.core.logging import logger

# Try to import OpenTelemetry - it's optional
OTEL_AVAILABLE = False
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
    logger.info("OpenTelemetry tracing available")
except ImportError:
    logger.info("OpenTelemetry not installed - tracing disabled (optional)")


class TracingManager:
    """
    Manages OpenTelemetry tracing for VCC-URN.
    
    Features:
    - Automatic request tracing
    - Federation call tracing
    - Custom span creation
    - Context propagation
    
    Configuration via environment variables:
    - URN_TRACING_ENABLED: Enable/disable tracing (default: false)
    - URN_TRACING_ENDPOINT: OTLP collector endpoint (default: http://localhost:4317)
    - URN_TRACING_SERVICE_NAME: Service name for traces (default: vcc-urn)
    """
    
    def __init__(self):
        self.enabled = os.getenv("URN_TRACING_ENABLED", "false").lower() == "true"
        self.endpoint = os.getenv("URN_TRACING_ENDPOINT", "http://localhost:4317")
        self.service_name = os.getenv("URN_TRACING_SERVICE_NAME", "vcc-urn")
        self.tracer: Optional[Any] = None
        self.propagator: Optional[Any] = None
        
        if self.enabled and OTEL_AVAILABLE:
            self._initialize()
    
    def _initialize(self) -> None:
        """Initialize OpenTelemetry tracing."""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.namespace": "vcc",
                "deployment.environment": os.getenv("URN_ENVIRONMENT", "development"),
            })
            
            # Set up trace provider
            provider = TracerProvider(resource=resource)
            
            # Configure exporter (OTLP to Jaeger or compatible collector)
            exporter = OTLPSpanExporter(endpoint=self.endpoint, insecure=True)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
            
            # Set global trace provider
            trace.set_tracer_provider(provider)
            
            # Get tracer instance
            self.tracer = trace.get_tracer(__name__, "1.0.0")
            self.propagator = TraceContextTextMapPropagator()
            
            logger.info(
                "OpenTelemetry tracing initialized",
                endpoint=self.endpoint,
                service_name=self.service_name
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
            self.enabled = False
    
    def create_span(self, name: str, kind: str = "internal", attributes: Optional[Dict] = None):
        """
        Create a new tracing span.
        
        Args:
            name: Name of the span
            kind: Span kind (internal, server, client, producer, consumer)
            attributes: Optional attributes to add to the span
        """
        if not self.enabled or not self.tracer:
            return NoOpSpan()
        
        span_kind_map = {
            "internal": SpanKind.INTERNAL,
            "server": SpanKind.SERVER,
            "client": SpanKind.CLIENT,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
        }
        
        return self.tracer.start_as_current_span(
            name,
            kind=span_kind_map.get(kind, SpanKind.INTERNAL),
            attributes=attributes or {}
        )
    
    def trace_federation_call(self, peer_url: str, urn: str):
        """Create a span for federation calls."""
        return self.create_span(
            "federation.resolve",
            kind="client",
            attributes={
                "peer.url": peer_url,
                "urn.value": urn,
                "http.method": "GET",
            }
        )
    
    def trace_urn_operation(self, operation: str, urn: Optional[str] = None):
        """Create a span for URN operations."""
        attributes = {"urn.operation": operation}
        if urn:
            attributes["urn.value"] = urn
        
        return self.create_span(f"urn.{operation}", kind="internal", attributes=attributes)
    
    def inject_context(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into HTTP headers for propagation."""
        if not self.enabled or not self.propagator:
            return headers
        
        self.propagator.inject(headers)
        return headers
    
    def extract_context(self, headers: Dict[str, str]):
        """Extract trace context from incoming HTTP headers."""
        if not self.enabled or not self.propagator:
            return None
        
        return self.propagator.extract(headers)
    
    def get_status(self) -> Dict[str, Any]:
        """Get tracing status for monitoring."""
        return {
            "enabled": self.enabled,
            "available": OTEL_AVAILABLE,
            "endpoint": self.endpoint if self.enabled else None,
            "service_name": self.service_name,
        }


class NoOpSpan:
    """No-operation span for when tracing is disabled."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def set_attribute(self, key: str, value: Any):
        pass
    
    def set_status(self, status):
        pass
    
    def record_exception(self, exception):
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict] = None):
        pass


def traced(name: Optional[str] = None, kind: str = "internal"):
    """
    Decorator to automatically trace function calls.
    
    Usage:
        @traced("my_operation")
        def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracing_manager.create_span(span_name, kind):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracing_manager.create_span(span_name, kind):
                return await func(*args, **kwargs)
        
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator


def asyncio_iscoroutinefunction(func):
    """Check if a function is a coroutine function."""
    import asyncio
    return asyncio.iscoroutinefunction(func)


# Global tracing manager instance
tracing_manager = TracingManager()
