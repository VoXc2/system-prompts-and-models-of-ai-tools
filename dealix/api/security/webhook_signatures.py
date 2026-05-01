"""
Webhook signature verification for HubSpot, Calendly, and n8n.
التحقق من توقيع webhook.

Each function returns True/False; the caller should 401 on False.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from collections.abc import Mapping


def _get_secret(env_var: str, override: str | None = None) -> str | None:
    return override or os.getenv(env_var)


# ── HubSpot v3 signatures ──────────────────────────────────────────
# https://developers.hubspot.com/docs/api/webhooks/validating-requests
def verify_hubspot_signature(
    *,
    method: str,
    url: str,
    body: bytes,
    timestamp: str | None,
    signature: str | None,
    secret: str | None = None,
) -> bool:
    s = _get_secret("HUBSPOT_APP_SECRET", secret)
    if not s or not signature or not timestamp:
        return False
    source = f"{method.upper()}{url}{body.decode('utf-8', 'replace')}{timestamp}"
    digest = hmac.new(s.encode(), source.encode(), hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


# ── Calendly signatures ────────────────────────────────────────────
# https://developer.calendly.com/api-docs/ZG9jOjE2OTM0NjE4-webhook-signatures
def verify_calendly_signature(
    *,
    body: bytes,
    header: str | None,
    secret: str | None = None,
) -> bool:
    s = _get_secret("CALENDLY_WEBHOOK_SECRET", secret)
    if not s or not header:
        return False
    # header format: "t=<timestamp>,v1=<signature>"
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts = parts.get("t")
    sig = parts.get("v1")
    if not ts or not sig:
        return False
    signed = f"{ts}.{body.decode('utf-8', 'replace')}"
    expected = hmac.new(s.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


# ── n8n (generic HMAC-SHA256 hex) ──────────────────────────────────
def verify_n8n_signature(
    *,
    body: bytes,
    signature: str | None,
    secret: str | None = None,
) -> bool:
    s = _get_secret("N8N_WEBHOOK_SECRET", secret)
    if not s or not signature:
        return False
    expected = hmac.new(s.encode(), body, hashlib.sha256).hexdigest()
    provided = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


# ── Generic helper for FastAPI request objects ────────────────────
async def require_signed(
    request_body: bytes,
    headers: Mapping[str, str],
    *,
    provider: str,
    method: str = "POST",
    url: str = "",
) -> bool:
    if provider == "hubspot":
        return verify_hubspot_signature(
            method=method,
            url=url,
            body=request_body,
            timestamp=headers.get("X-HubSpot-Request-Timestamp"),
            signature=headers.get("X-HubSpot-Signature-v3"),
        )
    if provider == "calendly":
        return verify_calendly_signature(
            body=request_body,
            header=headers.get("Calendly-Webhook-Signature"),
        )
    if provider == "n8n":
        return verify_n8n_signature(
            body=request_body,
            signature=headers.get("X-N8N-Signature"),
        )
    return False
