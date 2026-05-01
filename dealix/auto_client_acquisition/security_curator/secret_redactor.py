"""Secret Redactor — detect + redact secret-shaped strings before they leak."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Patterns are intentionally specific to avoid false positives.
# Each entry: (label, regex, redaction_template).
DEFAULT_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("github_pat", r"ghp_[A-Za-z0-9]{20,}", "ghp_***"),
    ("github_pat_legacy", r"github_pat_[A-Za-z0-9_]{20,}", "github_pat_***"),
    ("openai_key", r"sk-[A-Za-z0-9]{20,}", "sk-***"),
    ("anthropic_key", r"sk-ant-[A-Za-z0-9_\-]{20,}", "sk-ant-***"),
    ("supabase_service_role", r"eyJ[A-Za-z0-9_\-]{30,}\.[A-Za-z0-9_\-]{30,}\.[A-Za-z0-9_\-]{20,}", "eyJ.***.***"),
    ("whatsapp_token", r"EAA[A-Za-z0-9]{30,}", "EAA***"),
    ("moyasar_secret", r"sk_(?:test|live)_[A-Za-z0-9]{20,}", "sk_***_***"),
    ("langfuse_secret", r"lf_sk_[A-Za-z0-9]{20,}", "lf_sk_***"),
    ("sentry_dsn", r"https://[A-Za-z0-9]{20,}@[A-Za-z0-9.\-]+/\d+", "https://***@***/***"),
    ("aws_access_key", r"AKIA[A-Z0-9]{16}", "AKIA***"),
    ("google_api_key", r"AIza[A-Za-z0-9_\-]{30,}", "AIza***"),
    ("private_key_block", r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----", "-----BEGIN PRIVATE KEY *** REDACTED ***-----"),
)

# Sensitive keys for dict-shaped payloads (case-insensitive substring match).
SENSITIVE_PAYLOAD_KEYS: tuple[str, ...] = (
    "api_key", "apikey", "secret", "token", "password", "passwd",
    "authorization", "auth_token", "access_token", "refresh_token",
    "client_secret", "private_key", "ssn", "credit_card", "card_number",
    "cvv", "iban", "moyasar_secret",
)


@dataclass(frozen=True)
class SecretFinding:
    """A single secret detected in input."""
    label: str
    span: tuple[int, int]
    sample_redacted: str  # the *redacted* form, never the raw secret


def detect_secret_patterns(text: str) -> list[SecretFinding]:
    """Find secret-shaped substrings. Never returns the raw secret."""
    if not text:
        return []
    findings: list[SecretFinding] = []
    for label, pattern, redaction in DEFAULT_PATTERNS:
        for m in re.finditer(pattern, text):
            findings.append(SecretFinding(
                label=label,
                span=(m.start(), m.end()),
                sample_redacted=redaction,
            ))
    return findings


def redact_secrets(text: str) -> str:
    """Replace every detected secret with a label-typed redaction marker."""
    if not text:
        return text
    out = text
    for _label, pattern, redaction in DEFAULT_PATTERNS:
        out = re.sub(pattern, redaction, out)
    return out


def _is_sensitive_key(key: str) -> bool:
    k = key.lower()
    return any(s in k for s in SENSITIVE_PAYLOAD_KEYS)


def scan_payload(payload: Any) -> dict[str, Any]:
    """
    Scan a JSON-shaped payload for secret-typed keys + secret-shaped values.

    Returns:
        {
          "has_secrets": bool,
          "findings": [{"label", "path"}],
          "redacted": <same shape, but with values masked>,
        }
    """
    findings: list[dict[str, str]] = []

    def _walk(node: Any, path: str) -> Any:
        if isinstance(node, dict):
            out: dict[str, Any] = {}
            for k, v in node.items():
                p = f"{path}.{k}" if path else str(k)
                if _is_sensitive_key(str(k)):
                    findings.append({"label": "sensitive_key", "path": p})
                    out[k] = "***"
                else:
                    out[k] = _walk(v, p)
            return out
        if isinstance(node, list):
            return [_walk(item, f"{path}[{i}]") for i, item in enumerate(node)]
        if isinstance(node, str):
            secrets = detect_secret_patterns(node)
            if secrets:
                for s in secrets:
                    findings.append({"label": s.label, "path": path})
                return redact_secrets(node)
            return node
        return node

    redacted = _walk(payload, "")
    return {
        "has_secrets": bool(findings),
        "findings": findings,
        "redacted": redacted,
    }
