"""Observability: cost tracking, OpenTelemetry tracing, Sentry."""

from dealix.observability.cost_tracker import (
    MODEL_PRICES,
    CostEntry,
    CostTracker,
    estimate_cost_usd,
)
from dealix.observability.otel import (
    agent_span,
    instrument_fastapi,
    instrument_sqlalchemy,
    llm_span,
    setup_tracing,
    tool_span,
)
from dealix.observability.sentry import setup_sentry

__all__ = [
    "MODEL_PRICES",
    "CostEntry",
    "CostTracker",
    "agent_span",
    "estimate_cost_usd",
    "instrument_fastapi",
    "instrument_sqlalchemy",
    "llm_span",
    "setup_sentry",
    "setup_tracing",
    "tool_span",
]
