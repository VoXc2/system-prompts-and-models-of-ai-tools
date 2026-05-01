"""Security Curator — secret redaction + patch firewall + trace sanitization.

Inspired by Hermes Agent's Curator pattern, but specialized for Dealix's
external-action surface (WhatsApp, Gmail, Calendar, Moyasar, Social).

Goals:
- Never let an API key, token, or PAT escape into a log/trace/embedding/patch.
- Block any diff that adds .env files or secret-shaped strings.
- Sanitize tool outputs before they go into the Action Ledger or Proof Pack.
"""

from __future__ import annotations

from .patch_firewall import (
    PatchFirewallResult,
    inspect_diff,
    is_safe_diff,
)
from .secret_redactor import (
    DEFAULT_PATTERNS,
    SecretFinding,
    detect_secret_patterns,
    redact_secrets,
    scan_payload,
)
from .tool_output_sanitizer import (
    sanitize_tool_output,
    sanitize_trace_event,
)
from .trace_redactor import (
    redact_trace,
)

__all__ = [
    "DEFAULT_PATTERNS",
    "PatchFirewallResult",
    "SecretFinding",
    "detect_secret_patterns",
    "inspect_diff",
    "is_safe_diff",
    "redact_secrets",
    "redact_trace",
    "sanitize_tool_output",
    "sanitize_trace_event",
    "scan_payload",
]
