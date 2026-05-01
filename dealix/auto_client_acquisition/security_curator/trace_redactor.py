"""Trace Redactor — strip secrets/PII from traces before sending to Langfuse/Sentry."""

from __future__ import annotations

import re
from typing import Any

from .secret_redactor import scan_payload

# Phone-number-ish patterns we'll mask. Saudi: +966 5xxxxxxxx; international.
_PHONE_RE = re.compile(r"\+?\d[\d\s\-]{7,}\d")
# Generic email.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def _mask_phone(s: str) -> str:
    def _mask(m: re.Match[str]) -> str:
        raw = m.group(0)
        digits_only = re.sub(r"\D", "", raw)
        if len(digits_only) < 7:
            return raw
        return digits_only[:3] + "*" * (len(digits_only) - 6) + digits_only[-3:]
    return _PHONE_RE.sub(_mask, s)


def _mask_email(s: str) -> str:
    def _mask(m: re.Match[str]) -> str:
        local, _, domain = m.group(0).partition("@")
        if not local or not domain:
            return m.group(0)
        keep = local[0] if local else ""
        return f"{keep}***@{domain}"
    return _EMAIL_RE.sub(_mask, s)


def redact_trace(payload: Any, *, mask_pii: bool = True) -> dict[str, Any]:
    """
    Redact a trace payload for safe storage in observability tools.

    - Always strips secret patterns + sensitive keys (api_key/token/etc.).
    - When mask_pii=True (default), also masks phone numbers and emails inside
      string values.

    Returns:
        {
          "had_secrets": bool,
          "had_pii":     bool,
          "redacted":    <same shape, masked>,
        }
    """
    secret_scan = scan_payload(payload)
    redacted = secret_scan["redacted"]
    had_pii = False

    if mask_pii:
        had_pii_box: list[bool] = [False]

        def _walk(node: Any) -> Any:
            if isinstance(node, dict):
                return {k: _walk(v) for k, v in node.items()}
            if isinstance(node, list):
                return [_walk(item) for item in node]
            if isinstance(node, str):
                if _PHONE_RE.search(node) or _EMAIL_RE.search(node):
                    had_pii_box[0] = True
                return _mask_email(_mask_phone(node))
            return node

        redacted = _walk(redacted)
        had_pii = had_pii_box[0]

    return {
        "had_secrets": secret_scan["has_secrets"],
        "had_pii": had_pii,
        "redacted": redacted,
    }
