"""Multi-Provider WhatsApp Send — tries multiple providers with automatic fallback.

Supported providers (in priority order):
1. Green API   — free dev tier, simple REST, green-api.com
2. Ultramsg    — simple REST, ultramsg.com
3. WhatsApp Cloud API (official Meta) — needs Business verification
4. Fonnte      — ultra-cheap, fonnte.com

The system tries each provider in order until one succeeds.
All providers normalize Saudi phone numbers to 966XXXXXXXXX.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("dealix.whatsapp_multi")


def _format_saudi_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")
    if phone.startswith("05"):
        phone = "966" + phone[1:]
    elif phone.startswith("00966"):
        phone = phone[2:]
    elif phone.startswith("966"):
        pass
    elif phone.startswith("5") and len(phone) == 9:
        phone = "966" + phone
    return phone


async def send_via_greenapi(phone: str, message: str) -> Dict[str, Any]:
    """Green API — free dev tier, green-api.com.

    Env vars: GREEN_API_INSTANCE_ID, GREEN_API_TOKEN
    """
    instance = os.getenv("GREEN_API_INSTANCE_ID", "")
    token = os.getenv("GREEN_API_TOKEN", "")
    if not instance or not token:
        return {"provider": "greenapi", "status": "not_configured"}

    formatted = _format_saudi_phone(phone)
    url = f"https://api.green-api.com/waInstance{instance}/sendMessage/{token}"
    payload = {
        "chatId": f"{formatted}@c.us",
        "message": message,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            if resp.status_code == 200 and data.get("idMessage"):
                logger.info("GreenAPI sent to %s: %s", formatted, data.get("idMessage"))
                return {"provider": "greenapi", "status": "sent", "message_id": data.get("idMessage")}
            return {"provider": "greenapi", "status": "failed", "detail": data}
    except Exception as exc:
        return {"provider": "greenapi", "status": "error", "detail": str(exc)[:200]}


async def send_via_ultramsg(phone: str, message: str) -> Dict[str, Any]:
    """Ultramsg — simple REST API, ultramsg.com.

    Env vars: ULTRAMSG_INSTANCE_ID, ULTRAMSG_TOKEN
    """
    instance = os.getenv("ULTRAMSG_INSTANCE_ID", "")
    token = os.getenv("ULTRAMSG_TOKEN", "")
    if not instance or not token:
        return {"provider": "ultramsg", "status": "not_configured"}

    formatted = _format_saudi_phone(phone)
    url = f"https://api.ultramsg.com/{instance}/messages/chat"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, data={
                "token": token,
                "to": formatted,
                "body": message,
            })
            data = resp.json()
            if "error" not in str(data).lower() or data.get("sent") == "true":
                logger.info("Ultramsg sent to %s", formatted)
                return {"provider": "ultramsg", "status": "sent", "result": data}
            return {"provider": "ultramsg", "status": "failed", "detail": data}
    except Exception as exc:
        return {"provider": "ultramsg", "status": "error", "detail": str(exc)[:200]}


async def send_via_fonnte(phone: str, message: str) -> Dict[str, Any]:
    """Fonnte — ultra-cheap, fonnte.com.

    Env vars: FONNTE_TOKEN
    """
    token = os.getenv("FONNTE_TOKEN", "")
    if not token:
        return {"provider": "fonnte", "status": "not_configured"}

    formatted = _format_saudi_phone(phone)
    url = "https://api.fonnte.com/send"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers={"Authorization": token}, json={
                "target": formatted,
                "message": message,
            })
            data = resp.json()
            if data.get("status"):
                logger.info("Fonnte sent to %s", formatted)
                return {"provider": "fonnte", "status": "sent", "result": data}
            return {"provider": "fonnte", "status": "failed", "detail": data}
    except Exception as exc:
        return {"provider": "fonnte", "status": "error", "detail": str(exc)[:200]}


async def send_via_meta_cloud(phone: str, message: str) -> Dict[str, Any]:
    """Official WhatsApp Cloud API (Meta).

    Env vars: WHATSAPP_API_TOKEN, WHATSAPP_PHONE_NUMBER_ID
    """
    token = os.getenv("WHATSAPP_API_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    if not token or not phone_id:
        return {"provider": "meta_cloud", "status": "not_configured"}

    formatted = _format_saudi_phone(phone)
    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }, json={
                "messaging_product": "whatsapp",
                "to": formatted,
                "type": "text",
                "text": {"body": message},
            })
            data = resp.json()
            if resp.status_code == 200 and data.get("messages"):
                msg_id = data["messages"][0].get("id", "")
                logger.info("MetaCloud sent to %s: %s", formatted, msg_id)
                return {"provider": "meta_cloud", "status": "sent", "message_id": msg_id}
            return {"provider": "meta_cloud", "status": "failed", "detail": data}
    except Exception as exc:
        return {"provider": "meta_cloud", "status": "error", "detail": str(exc)[:200]}


PROVIDER_CHAIN = [
    ("greenapi", send_via_greenapi),
    ("ultramsg", send_via_ultramsg),
    ("fonnte", send_via_fonnte),
    ("meta_cloud", send_via_meta_cloud),
]


async def send_whatsapp_smart(phone: str, message: str) -> Dict[str, Any]:
    """Try all configured providers in order until one succeeds."""
    attempts = []
    for name, send_fn in PROVIDER_CHAIN:
        result = await send_fn(phone, message)
        attempts.append(result)
        if result.get("status") == "sent":
            return {
                "sent": True,
                "provider_used": name,
                "result": result,
                "attempts": len(attempts),
            }

    return {
        "sent": False,
        "provider_used": None,
        "error": "all_providers_failed_or_not_configured",
        "attempts": attempts,
    }


async def check_providers() -> Dict[str, Any]:
    """Check which providers are configured (without sending)."""
    status = {}
    for name, _ in PROVIDER_CHAIN:
        if name == "greenapi":
            configured = bool(os.getenv("GREEN_API_INSTANCE_ID") and os.getenv("GREEN_API_TOKEN"))
        elif name == "ultramsg":
            configured = bool(os.getenv("ULTRAMSG_INSTANCE_ID") and os.getenv("ULTRAMSG_TOKEN"))
        elif name == "fonnte":
            configured = bool(os.getenv("FONNTE_TOKEN"))
        elif name == "meta_cloud":
            configured = bool(os.getenv("WHATSAPP_API_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
        else:
            configured = False
        status[name] = configured
    return {
        "providers": status,
        "any_configured": any(status.values()),
        "recommended": "greenapi" if not any(status.values()) else next((k for k, v in status.items() if v), None),
    }
