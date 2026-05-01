"""Incoming webhooks — WhatsApp, HubSpot, Calendly."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request

from api.dependencies import get_acquisition_pipeline
from auto_client_acquisition.agents.intake import LeadSource
from core.config.settings import get_settings
from core.logging import get_logger
from integrations.whatsapp import WhatsAppClient

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


# ── WhatsApp ───────────────────────────────────────────────────
@router.get("/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
) -> Any:
    """Meta WhatsApp webhook verification."""
    client = WhatsAppClient()
    challenge = client.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge is None:
        raise HTTPException(status_code=403, detail="Invalid verification token")
    return int(challenge)


@router.post("/whatsapp")
async def whatsapp_incoming(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
) -> dict[str, Any]:
    """Handle incoming WhatsApp messages — route them as leads."""
    body = await request.body()
    client = WhatsAppClient()
    settings = get_settings()
    has_secret = bool(client.settings.whatsapp_app_secret)

    # Staging/production with app secret: require valid Meta signature always.
    if has_secret and settings.app_env in ("staging", "production"):
        if not x_hub_signature_256 or not client.verify_signature(body, x_hub_signature_256):
            logger.warning("whatsapp_missing_or_invalid_signature_strict_env")
            raise HTTPException(status_code=403, detail="missing_or_invalid_signature")
    elif x_hub_signature_256 and has_secret and not client.verify_signature(body, x_hub_signature_256):
        logger.warning("whatsapp_invalid_signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}") from e

    messages = client.parse_incoming(payload)
    pipeline = get_acquisition_pipeline()
    processed = []

    for msg in messages:
        if msg["type"] != "text" or not msg.get("text"):
            continue
        lead_payload = {
            "name": msg.get("contact_name") or "",
            "phone": f"+{msg['from']}",
            "message": msg["text"],
            "company": "",
        }
        result = await pipeline.run(payload=lead_payload, source=LeadSource.WHATSAPP)
        processed.append(result.lead.id)
    logger.info("whatsapp_webhook_processed", count=len(processed))
    return {"processed": processed, "count": len(processed)}


# ── Calendly ───────────────────────────────────────────────────
@router.post("/calendly")
async def calendly_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    """Receive Calendly event lifecycle notifications."""
    event = payload.get("event") or payload.get("type") or "unknown"
    logger.info("calendly_webhook_received", event=event)
    return {"ok": True, "event": event}


# ── HubSpot ────────────────────────────────────────────────────
@router.post("/hubspot")
async def hubspot_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    """Receive HubSpot subscription events."""
    logger.info(
        "hubspot_webhook_received", n_events=len(payload) if isinstance(payload, list) else 1
    )
    return {"ok": True}
