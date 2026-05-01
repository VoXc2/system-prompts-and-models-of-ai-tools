"""Structured trace event for dashboards (PII-redacted strings)."""

from __future__ import annotations

import time
import uuid
from typing import Any

from auto_client_acquisition.security_curator.trace_redactor import redact_trace_payload


def build_trace_event(
    *,
    workflow_name: str,
    agent_name: str,
    action_type: str,
    policy_result: str,
    tool_called: str | None = None,
    outcome: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    meta = metadata or {}
    safe_meta = redact_trace_payload(meta)
    return {
        "trace_id": str(uuid.uuid4()),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workflow_name": workflow_name,
        "agent_name": agent_name,
        "action_type": action_type,
        "policy_result": policy_result,
        "tool_called": tool_called,
        "outcome": outcome,
        "metadata": safe_meta,
        "demo": True,
    }
