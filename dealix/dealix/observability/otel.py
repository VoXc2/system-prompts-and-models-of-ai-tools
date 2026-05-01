"""
OpenTelemetry setup — traces for FastAPI, SQLAlchemy, HTTPX + custom LLM spans.
إعداد OpenTelemetry — تتبع FastAPI و SQLAlchemy و HTTPX مع spans مخصصة للـ LLM.

Default exporter = OTLP/HTTP → Langfuse (via OTEL_EXPORTER_OTLP_ENDPOINT).
Falls back to no-op exporter when OTel libs aren't installed.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

log = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    _HAS_OTEL = True
except ImportError:  # pragma: no cover
    _HAS_OTEL = False


_tracer: Any = None


def setup_tracing(service_name: str = "dealix-api", version: str = "3.0.0") -> None:
    """Initialize OTel tracer + instrument libraries. Safe if OTel is absent."""
    global _tracer
    if not _HAS_OTEL:
        log.info("otel_unavailable — tracing disabled")
        return

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        log.info("otel_not_configured — set OTEL_EXPORTER_OTLP_ENDPOINT to enable")
        return

    headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": version,
            "deployment.environment": os.getenv("APP_ENV", "production"),
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=dict(p.split("=", 1) for p in headers.split(",") if "=" in p),
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name, version)
    log.info("otel_enabled", extra={"endpoint": endpoint})


def instrument_fastapi(app: Any) -> None:
    if _HAS_OTEL and _tracer is not None:
        FastAPIInstrumentor.instrument_app(app)
        HTTPXClientInstrumentor().instrument()


def instrument_sqlalchemy(engine: Any) -> None:
    if _HAS_OTEL and _tracer is not None and engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine)


@contextmanager
def llm_span(model: str, task: str, **attrs: Any) -> Iterator[Any]:
    """Context manager for a custom LLM span."""
    if not _HAS_OTEL or _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(
        f"llm.call:{model}",
        attributes={
            "llm.model": model,
            "llm.task": task,
            **{f"llm.{k}": v for k, v in attrs.items()},
        },
    ) as span:
        yield span


@contextmanager
def agent_span(agent_name: str, **attrs: Any) -> Iterator[Any]:
    if not _HAS_OTEL or _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(
        f"agent:{agent_name}",
        attributes={"agent.name": agent_name, **attrs},
    ) as span:
        yield span


@contextmanager
def tool_span(tool_name: str, **attrs: Any) -> Iterator[Any]:
    if not _HAS_OTEL or _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(
        f"tool:{tool_name}",
        attributes={"tool.name": tool_name, **attrs},
    ) as span:
        yield span
