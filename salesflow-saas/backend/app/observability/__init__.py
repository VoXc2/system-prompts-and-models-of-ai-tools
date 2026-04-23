"""Observability layer — OpenTelemetry traces, metrics, and log correlation."""

from app.observability.otel import (
    init_otel,
    get_tracer,
    span,
    inject_correlation_id,
    extract_trace_id,
)

__all__ = [
    "init_otel",
    "get_tracer",
    "span",
    "inject_correlation_id",
    "extract_trace_id",
]
