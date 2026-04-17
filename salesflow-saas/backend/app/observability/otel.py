"""OpenTelemetry integration — traces with correlation_id linkage.

Designed to work even if opentelemetry packages are not installed
(graceful degradation). Spans become no-ops when OTel is missing.

This is the bridge between business correlation_id (used by OpenClaw
gateway, golden_path, saudi_workflow) and OTel trace_id (used by
production debugging tools).
"""

from __future__ import annotations

import contextlib
import os
import uuid
from typing import Any, Dict, Optional


_OTEL_ENABLED = False
_TRACER = None


def init_otel(service_name: str = "dealix-backend") -> bool:
    """Initialize OpenTelemetry. Returns True if successful, False if unavailable.

    Auto-instruments FastAPI and SQLAlchemy if opentelemetry-instrumentation
    packages are installed. Falls back to no-op tracer if OTel not available.
    """
    global _OTEL_ENABLED, _TRACER

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        # Console exporter by default; OTLP if endpoint configured
        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter,
                )
                provider.add_span_processor(
                    BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
                )
            except ImportError:
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            # Disable console output by default to avoid noisy logs
            if os.environ.get("OTEL_CONSOLE", "").lower() == "true":
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        _TRACER = trace.get_tracer(service_name)
        _OTEL_ENABLED = True

        # Auto-instrument FastAPI if installed
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            # Will be applied to specific app instance via instrument_app()
        except ImportError:
            pass

        return True
    except ImportError:
        _OTEL_ENABLED = False
        _TRACER = None
        return False


def get_tracer():
    """Return the OTel tracer or a no-op stand-in."""
    return _TRACER


def instrument_fastapi(app) -> None:
    """Instrument a FastAPI app instance for automatic span creation."""
    if not _OTEL_ENABLED:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass


def instrument_sqlalchemy(engine) -> None:
    """Instrument a SQLAlchemy engine for automatic query span creation."""
    if not _OTEL_ENABLED:
        return
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument(engine=engine)
    except ImportError:
        pass


@contextlib.contextmanager
def span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Create a span. No-op if OTel not initialized.

    Usage:
        with span("golden_path.run", {"correlation_id": cid}):
            ...
    """
    if not _OTEL_ENABLED or _TRACER is None:
        yield None
        return

    with _TRACER.start_as_current_span(name) as s:
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    s.set_attribute(k, str(v))
        yield s


def inject_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Inject correlation_id into current span. Returns the correlation_id used."""
    cid = correlation_id or str(uuid.uuid4())
    if _OTEL_ENABLED and _TRACER is not None:
        try:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("correlation_id", cid)
        except Exception:
            pass
    return cid


def extract_trace_id() -> Optional[str]:
    """Get current trace_id from active span (None if no span active)."""
    if not _OTEL_ENABLED:
        return None
    try:
        from opentelemetry import trace
        current_span = trace.get_current_span()
        if current_span:
            ctx = current_span.get_span_context()
            if ctx and ctx.trace_id:
                return format(ctx.trace_id, "032x")
    except Exception:
        pass
    return None
