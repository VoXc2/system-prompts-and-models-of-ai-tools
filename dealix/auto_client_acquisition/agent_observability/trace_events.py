"""Build sanitized trace events for Langfuse/Sentry."""

from __future__ import annotations

import hashlib
import time
from typing import Any

from auto_client_acquisition.security_curator import sanitize_trace_event


def _hash_id(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def build_trace_event(
    *,
    workflow_name: str,
    agent_name: str,
    status: str = "started",
    user_id: str | None = None,
    company_id: str | None = None,
    tool: str | None = None,
    policy_result: str | None = None,
    risk_level: str | None = None,
    approval_status: str | None = None,
    latency_ms: float = 0.0,
    cost_estimate: float = 0.0,
    payload: Any = None,
    output: Any = None,
) -> dict[str, Any]:
    """
    Build a sanitized trace event ready for Langfuse/Sentry.

    All payload/output fields go through the security_curator sanitizer.
    User/company IDs are hashed before logging.
    """
    raw = {
        "ts": time.time(),
        "workflow_name": workflow_name,
        "agent_name": agent_name,
        "status": status,
        "user_id_hash": _hash_id(user_id),
        "company_id_hash": _hash_id(company_id),
        "tool": tool,
        "policy_result": policy_result,
        "risk_level": risk_level,
        "approval_status": approval_status,
        "latency_ms": latency_ms,
        "cost_estimate": cost_estimate,
        "payload": payload,
        "output": output,
    }
    return sanitize_trace_event(raw)
