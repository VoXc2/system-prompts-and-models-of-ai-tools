"""Redact nested structures before sending traces to external observability."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.security_curator.secret_redactor import sanitize_for_trace


def redact_trace_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Deep-redact string leaves; safe for Langfuse/OpenAI-style span metadata."""
    return sanitize_for_trace(payload)


def redact_span_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Alias for observability adapters."""
    return redact_trace_payload(metadata or {})
