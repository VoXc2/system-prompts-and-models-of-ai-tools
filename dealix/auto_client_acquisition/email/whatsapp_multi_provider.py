"""
Multi-provider WhatsApp send adapter — Green API → Ultramsg → Fonnte → Meta Cloud.

Smart fallback: tries each configured provider in priority order; if the call
fails (5xx, timeout, instance disconnected), falls through to the next.

CRITICAL — All non-Meta options use WhatsApp Web (not the official Business API).
DO NOT bind your primary phone — use a secondary SIM. WhatsApp may rate-limit
or block numbers that send too aggressively.

Recommended stack for Saudi B2B:
1. Green API   — free dev tier, ~5 min setup. PRIMARY.
2. Ultramsg    — $13/mo paid; lives in repo as legacy. SECONDARY.
3. Fonnte      — $2-5/mo, Asian market. TERTIARY.
4. Meta Cloud  — official, requires Business verification + approved templates. FALLBACK.

Env vars:
    GREEN_API_INSTANCE_ID, GREEN_API_TOKEN
    ULTRAMSG_INSTANCE_ID,  ULTRAMSG_TOKEN
    FONNTE_TOKEN
    META_WHATSAPP_PHONE_NUMBER_ID, META_WHATSAPP_ACCESS_TOKEN

Set WHATSAPP_MOCK_MODE=true to short-circuit all providers (CI / dev).

Live sends require WHATSAPP_ALLOW_LIVE_SEND=true (see `Settings.whatsapp_allow_live_send`);
otherwise `send_whatsapp_smart` returns status ``blocked`` after phone validation.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

import httpx

log = logging.getLogger(__name__)

_NON_DIGIT = re.compile(r"\D+")


@dataclass
class WhatsAppSendResult:
    status: str  # ok | no_keys | http_error | timeout | mock | blocked | all_providers_failed
    provider: str | None = None
    message_id: str | None = None
    error: str | None = None
    fallback_chain_tried: list[str] = None  # type: ignore[assignment]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["fallback_chain_tried"] = self.fallback_chain_tried or []
        return d


def _normalize_phone(phone: str) -> str:
    """Strip non-digits. Saudi numbers expected to start with 966 or 05."""
    digits = _NON_DIGIT.sub("", phone or "")
    if digits.startswith("00966"):
        digits = digits[2:]
    elif digits.startswith("05") and len(digits) == 10:
        digits = "966" + digits[1:]
    elif digits.startswith("5") and len(digits) == 9:
        digits = "966" + digits
    elif digits.startswith("0") and len(digits) == 10:
        digits = "966" + digits[1:]
    return digits


# ── Provider implementations ──────────────────────────────────────
async def _send_via_green_api(
    client: httpx.AsyncClient, phone: str, message: str
) -> WhatsAppSendResult | None:
    instance = os.getenv("GREEN_API_INSTANCE_ID", "").strip()
    token = os.getenv("GREEN_API_TOKEN", "").strip()
    if not (instance and token):
        return None
    url = f"https://api.green-api.com/waInstance{instance}/sendMessage/{token}"
    try:
        r = await client.post(
            url, json={"chatId": f"{phone}@c.us", "message": message}, timeout=15.0
        )
    except Exception as exc:  # noqa: BLE001
        return WhatsAppSendResult(status="http_error", provider="green_api", error=str(exc))
    if r.status_code == 200:
        body = r.json() or {}
        return WhatsAppSendResult(
            status="ok", provider="green_api",
            message_id=body.get("idMessage"),
        )
    return WhatsAppSendResult(
        status="http_error", provider="green_api",
        error=f"HTTP {r.status_code}: {r.text[:200]}",
    )


async def _send_via_ultramsg(
    client: httpx.AsyncClient, phone: str, message: str
) -> WhatsAppSendResult | None:
    instance = os.getenv("ULTRAMSG_INSTANCE_ID", "").strip()
    token = os.getenv("ULTRAMSG_TOKEN", "").strip()
    if not (instance and token):
        return None
    url = f"https://api.ultramsg.com/{instance}/messages/chat"
    try:
        r = await client.post(
            url, data={"token": token, "to": phone, "body": message}, timeout=15.0
        )
    except Exception as exc:  # noqa: BLE001
        return WhatsAppSendResult(status="http_error", provider="ultramsg", error=str(exc))
    if r.status_code in (200, 201):
        body = r.json() or {}
        if body.get("sent") in (True, "true", "True"):
            return WhatsAppSendResult(
                status="ok", provider="ultramsg",
                message_id=str(body.get("id") or ""),
            )
    return WhatsAppSendResult(
        status="http_error", provider="ultramsg",
        error=f"HTTP {r.status_code}: {r.text[:200]}",
    )


async def _send_via_fonnte(
    client: httpx.AsyncClient, phone: str, message: str
) -> WhatsAppSendResult | None:
    token = os.getenv("FONNTE_TOKEN", "").strip()
    if not token:
        return None
    try:
        r = await client.post(
            "https://api.fonnte.com/send",
            headers={"Authorization": token},
            data={"target": phone, "message": message},
            timeout=15.0,
        )
    except Exception as exc:  # noqa: BLE001
        return WhatsAppSendResult(status="http_error", provider="fonnte", error=str(exc))
    if r.status_code == 200:
        body = r.json() or {}
        if body.get("status") in (True, "true"):
            return WhatsAppSendResult(
                status="ok", provider="fonnte",
                message_id=str(body.get("id") or ""),
            )
    return WhatsAppSendResult(
        status="http_error", provider="fonnte",
        error=f"HTTP {r.status_code}: {r.text[:200]}",
    )


async def _send_via_meta_cloud(
    client: httpx.AsyncClient, phone: str, message: str
) -> WhatsAppSendResult | None:
    pid = os.getenv("META_WHATSAPP_PHONE_NUMBER_ID", "").strip()
    tok = os.getenv("META_WHATSAPP_ACCESS_TOKEN", "").strip()
    if not (pid and tok):
        return None
    url = f"https://graph.facebook.com/v18.0/{pid}/messages"
    try:
        r = await client.post(
            url,
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp", "to": phone, "type": "text",
                "text": {"body": message},
            },
            timeout=15.0,
        )
    except Exception as exc:  # noqa: BLE001
        return WhatsAppSendResult(status="http_error", provider="meta_cloud", error=str(exc))
    if r.status_code == 200:
        body = r.json() or {}
        msgs = body.get("messages") or []
        return WhatsAppSendResult(
            status="ok", provider="meta_cloud",
            message_id=msgs[0].get("id") if msgs else None,
        )
    return WhatsAppSendResult(
        status="http_error", provider="meta_cloud",
        error=f"HTTP {r.status_code}: {r.text[:200]}",
    )


# ── Public API ────────────────────────────────────────────────────
PROVIDER_CHAIN = [
    ("green_api", _send_via_green_api),
    ("ultramsg", _send_via_ultramsg),
    ("fonnte", _send_via_fonnte),
    ("meta_cloud", _send_via_meta_cloud),
]


def configured_providers() -> list[str]:
    """Which providers have credentials in env. Useful for /os/test-send."""
    out: list[str] = []
    if os.getenv("GREEN_API_INSTANCE_ID") and os.getenv("GREEN_API_TOKEN"):
        out.append("green_api")
    if os.getenv("ULTRAMSG_INSTANCE_ID") and os.getenv("ULTRAMSG_TOKEN"):
        out.append("ultramsg")
    if os.getenv("FONNTE_TOKEN"):
        out.append("fonnte")
    if os.getenv("META_WHATSAPP_PHONE_NUMBER_ID") and os.getenv("META_WHATSAPP_ACCESS_TOKEN"):
        out.append("meta_cloud")
    return out


async def send_whatsapp_smart(phone: str, message: str) -> WhatsAppSendResult:
    """Send via the first available WhatsApp provider in priority order."""
    if os.getenv("WHATSAPP_MOCK_MODE", "").lower() in {"true", "1", "yes"}:
        log.info("whatsapp_mock_mode phone=%s msg_len=%d", phone, len(message))
        return WhatsAppSendResult(status="mock", provider="mock")

    normalized = _normalize_phone(phone)
    if not normalized:
        return WhatsAppSendResult(status="http_error", error="invalid_phone")

    from core.config.settings import get_settings

    if not get_settings().whatsapp_allow_live_send:
        log.info("whatsapp_send_blocked_by_policy phone_prefix=%s", normalized[:5])
        return WhatsAppSendResult(
            status="blocked",
            provider="policy",
            error="whatsapp_allow_live_send_false",
            fallback_chain_tried=[],
        )

    tried: list[str] = []
    last: WhatsAppSendResult | None = None
    async with httpx.AsyncClient() as client:
        for name, fn in PROVIDER_CHAIN:
            result = await fn(client, normalized, message)
            if result is None:
                continue  # not configured
            tried.append(name)
            if result.status == "ok":
                result.fallback_chain_tried = tried
                return result
            last = result
            log.info("whatsapp_fallback_from=%s status=%s", name, result.status)

    if not tried:
        return WhatsAppSendResult(
            status="no_keys",
            error="no_whatsapp_provider_configured",
            fallback_chain_tried=[],
        )
    if last:
        last.fallback_chain_tried = tried
        return last
    return WhatsAppSendResult(
        status="all_providers_failed",
        fallback_chain_tried=tried,
    )
