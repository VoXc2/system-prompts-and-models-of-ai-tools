"""Lead form webhook MVP — trusted simulation only, no signature crypto yet."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.platform_services.event_bus import EventType, validate_event
from auto_client_acquisition.platform_services.unified_inbox import event_to_inbox_card

_ALLOWED_SOURCES = frozenset({"trusted_simulation"})


def ingest_lead_form(body: dict[str, Any]) -> dict[str, Any]:
    """
    Accepts ``source``, ``channel_id`` (linkedin_lead_form | website_form), and lead fields.
    Documented contract for later HMAC verification.
    """
    source = str(body.get("source") or "")
    if source not in _ALLOWED_SOURCES:
        return {
            "ok": False,
            "error": "invalid_source",
            "detail_ar": "المصدر غير مسموح في MVP — استخدم trusted_simulation حتى تفعيل التوقيع.",
        }

    channel_id = str(body.get("channel_id") or "website_form")
    if channel_id not in ("linkedin_lead_form", "website_form"):
        return {"ok": False, "error": "invalid_channel", "detail_ar": "القناة غير مدعومة في مسار الـ ingest هذا."}

    event = {
        "event_type": EventType.LEAD_RECEIVED.value,
        "source": source,
        "channel_id": channel_id,
        "lead_name": body.get("lead_name") or body.get("name") or "",
        "lead_email": body.get("lead_email") or body.get("email"),
        "meta": body.get("meta") if isinstance(body.get("meta"), dict) else {},
    }
    v = validate_event(event)
    if not v["valid"]:
        return {"ok": False, "error": "validation_failed", "errors": v["errors"]}

    card = event_to_inbox_card(v["normalized"] or event)
    return {"ok": True, "event": v["normalized"], "inbox_card": card, "approval_required": True}
