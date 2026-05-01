"""Detect and redact common secret patterns from text and nested payloads."""

from __future__ import annotations

import copy
import json
import re
from typing import Any

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "ghp_<REDACTED>"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "github_pat_<REDACTED>"),
    (re.compile(r"sk_live_[A-Za-z0-9]{20,}"), "sk_live_<REDACTED>"),
    (
        re.compile(r"(?i)(OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY|GROQ_API_KEY)\s*[=:]\s*[\w\-]{8,}"),
        r"\1=<REDACTED>",
    ),
    (re.compile(r"(?i)SUPABASE_SERVICE_ROLE_KEY\s*[=:]\s*[\w\-.]{10,}"), "SUPABASE_SERVICE_ROLE_KEY=<REDACTED>"),
    (re.compile(r"(?i)WHATSAPP_ACCESS_TOKEN\s*[=:]\s*[\w\-.]{10,}"), "WHATSAPP_ACCESS_TOKEN=<REDACTED>"),
    (re.compile(r"(?i)MOYASAR_SECRET\s*[=:]\s*[\w\-.]{6,}"), "MOYASAR_SECRET=<REDACTED>"),
    (re.compile(r"(?i)LANGFUSE_SECRET_KEY\s*[=:]\s*[\w\-.]{6,}"), "LANGFUSE_SECRET_KEY=<REDACTED>"),
    (
        re.compile(r"https://[a-f0-9]+@[a-z0-9.-]+\.ingest\.[a-z0-9.-]+\.sentry\.io/\d+"),
        "https://<REDACTED>@sentry.io/<REDACTED>",
    ),
]


def redact_secrets(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, repl in _PATTERNS:
        out = pat.sub(repl, out)
    return out


def scan_payload(payload: Any) -> list[str]:
    """Return list of human-readable findings (empty if clean)."""
    findings: list[str] = []
    raw = json.dumps(payload, ensure_ascii=False, default=str) if not isinstance(payload, str) else payload
    if "ghp_" in raw or "github_pat_" in raw:
        findings.append("possible_github_token")
    if re.search(r"sk_live_", raw):
        findings.append("possible_stripe_live")
    if re.search(r"(?i)(OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*[=:]", raw):
        findings.append("possible_llm_key_assignment")
    if ".env" in raw and ("=" in raw or ":" in raw):
        findings.append("possible_env_dump")
    return findings


def sanitize_for_trace(payload: dict[str, Any]) -> dict[str, Any]:
    """Deep-copy and redact string leaves (MVP)."""
    data = copy.deepcopy(payload)

    def _walk(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _walk(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_walk(v) for v in obj]
        if isinstance(obj, str):
            return redact_secrets(obj)
        return obj

    return _walk(data)
