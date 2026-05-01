"""Sanitize tool/agent outputs before they reach the user, ledger, or Proof Pack."""

from __future__ import annotations

from typing import Any

from .secret_redactor import scan_payload
from .trace_redactor import redact_trace


def sanitize_tool_output(output: Any, *, mask_pii: bool = True) -> dict[str, Any]:
    """
    Sanitize a tool's output before showing it to a human or persisting it.

    Returns:
        {
          "safe":     bool   (True iff no secrets and no payload PII at risk),
          "redacted": <same shape as input, masked>,
          "notes_ar": list[str] of human-readable notes,
        }
    """
    notes: list[str] = []
    secret_scan = scan_payload(output)
    redacted = secret_scan["redacted"]

    if secret_scan["has_secrets"]:
        labels = sorted({f["label"] for f in secret_scan["findings"]})
        notes.append(f"تمت إزالة قيم حساسة من المخرج: {', '.join(labels)}")

    if mask_pii:
        trace_scan = redact_trace(redacted, mask_pii=True)
        redacted = trace_scan["redacted"]
        if trace_scan["had_pii"]:
            notes.append("تم إخفاء أرقام/إيميلات في المخرج لأغراض الخصوصية.")

    safe = not secret_scan["has_secrets"]
    return {"safe": safe, "redacted": redacted, "notes_ar": notes}


def sanitize_trace_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize a single trace event for Langfuse/Sentry.

    Always preserves: event_type, agent_name, status, latency_ms, cost_estimate.
    Always masks:     payload, output, input.
    """
    safe_keys = {
        "event_type", "agent_name", "status", "latency_ms",
        "cost_estimate", "approval_status", "tool", "policy_result",
        "risk_level", "user_id_hash", "company_id_hash",
        "workflow_name", "trace_id", "span_id", "ts",
    }
    risky_keys = {"payload", "output", "input", "context", "raw"}

    out: dict[str, Any] = {}
    for k, v in event.items():
        if k in safe_keys:
            out[k] = v
        elif k in risky_keys:
            scan = redact_trace(v, mask_pii=True)
            out[k] = scan["redacted"]
            if scan["had_secrets"] or scan["had_pii"]:
                out.setdefault("_sanitized", []).append(k)
        else:
            # Unknown keys default to redaction, just in case.
            scan = redact_trace(v, mask_pii=True)
            out[k] = scan["redacted"]
    return out
