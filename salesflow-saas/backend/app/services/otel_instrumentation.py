"""
OpenTelemetry Instrumentation — Dealix Sovereign OS

Provides vendor-neutral traces, metrics, and logs with correlation IDs
across all 5 planes: Decision, Execution, Trust, Data, Operating.

Design:
  - Falls back gracefully if opentelemetry is not installed
  - Always attaches correlation_id + tenant_id to every span/metric
  - Structured log events follow CloudEvents convention
"""
from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

logger = logging.getLogger("dealix.otel")

try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import Status, StatusCode
    _OTEL_AVAILABLE = True
    tracer = trace.get_tracer("dealix.sovereign")
    meter = metrics.get_meter("dealix.sovereign")
    # Metrics
    _decision_counter = meter.create_counter(
        "dealix_decisions_total",
        description="Total structured AI decisions made",
    )
    _contradiction_counter = meter.create_counter(
        "dealix_contradictions_total",
        description="Total contradiction records detected",
    )
    _hitl_counter = meter.create_counter(
        "dealix_hitl_requests_total",
        description="Total HITL (Human-in-the-Loop) approval requests",
    )
    _connector_call_histogram = meter.create_histogram(
        "dealix_connector_latency_ms",
        description="Connector call latency in milliseconds",
        unit="ms",
    )
except ImportError:
    _OTEL_AVAILABLE = False
    tracer = None
    meter = None


def new_correlation_id() -> str:
    return str(uuid.uuid4()).replace("-", "")[:16]


@contextmanager
def sovereign_span(
    name: str,
    tenant_id: str = "",
    correlation_id: str = "",
    **attributes: Any,
) -> Generator:
    """Context manager for a Sovereign OS trace span."""
    if not _OTEL_AVAILABLE or tracer is None:
        yield None
        return

    with tracer.start_as_current_span(name) as span:
        span.set_attribute("dealix.tenant_id", tenant_id)
        span.set_attribute("dealix.correlation_id", correlation_id or new_correlation_id())
        span.set_attribute("dealix.environment", "sovereign")
        for k, v in attributes.items():
            span.set_attribute(f"dealix.{k}", str(v))
        try:
            yield span
        except Exception as exc:
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


async def record_decision_span(
    decision_type: str,
    lane: str,
    latency_ms: int,
    hitl_required: bool,
    tenant_id: str = "",
) -> None:
    """Record a decision telemetry event."""
    if _OTEL_AVAILABLE and _decision_counter is not None:
        _decision_counter.add(1, {
            "decision_type": decision_type,
            "lane": lane,
            "hitl_required": str(hitl_required),
            "tenant_id": tenant_id,
        })
        if hitl_required and _hitl_counter is not None:
            _hitl_counter.add(1, {"decision_type": decision_type, "tenant_id": tenant_id})

    logger.info(
        "sovereign_decision",
        extra={
            "decision_type": decision_type,
            "lane": lane,
            "latency_ms": latency_ms,
            "hitl_required": hitl_required,
            "tenant_id": tenant_id,
        },
    )


async def record_contradiction(
    agent_role: str,
    contradiction_type: str,
    severity: str,
    tenant_id: str = "",
) -> None:
    if _OTEL_AVAILABLE and _contradiction_counter is not None:
        _contradiction_counter.add(1, {
            "agent_role": agent_role,
            "contradiction_type": contradiction_type,
            "severity": severity,
            "tenant_id": tenant_id,
        })

    logger.warning(
        "contradiction_detected",
        extra={
            "agent_role": agent_role,
            "contradiction_type": contradiction_type,
            "severity": severity,
            "tenant_id": tenant_id,
        },
    )


async def record_connector_call(
    connector_key: str,
    latency_ms: float,
    success: bool,
    tenant_id: str = "",
) -> None:
    if _OTEL_AVAILABLE and _connector_call_histogram is not None:
        _connector_call_histogram.record(latency_ms, {
            "connector_key": connector_key,
            "success": str(success),
            "tenant_id": tenant_id,
        })

    logger.info(
        "connector_call",
        extra={
            "connector_key": connector_key,
            "latency_ms": latency_ms,
            "success": success,
            "tenant_id": tenant_id,
        },
    )


def cloud_event(
    event_type: str,
    source: str,
    data: dict[str, Any],
    tenant_id: str = "",
    correlation_id: str = "",
) -> dict[str, Any]:
    """
    Build a CloudEvents-compliant event envelope.
    Reference: https://cloudevents.io/
    """
    return {
        "specversion": "1.0",
        "type": f"dealix.{event_type}",
        "source": f"/dealix/{source}",
        "id": str(uuid.uuid4()),
        "time": datetime.now(timezone.utc).isoformat(),
        "datacontenttype": "application/json",
        "extensions": {
            "tenantid": tenant_id,
            "correlationid": correlation_id or new_correlation_id(),
        },
        "data": data,
    }
