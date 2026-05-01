"""Sanitize agent/tool outputs before logging or returning to clients."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.security_curator.secret_redactor import redact_secrets, sanitize_for_trace


def sanitize_tool_output(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_secrets(obj)
    if isinstance(obj, dict):
        return sanitize_for_trace(obj)
    return obj
