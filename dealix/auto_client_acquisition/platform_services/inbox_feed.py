"""Deterministic unified inbox feed for demos — merges intel cards + platform inbox card."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.intelligence_layer.intel_command_feed import build_intel_command_feed
from auto_client_acquisition.platform_services.event_bus import EventType
from auto_client_acquisition.platform_services.unified_inbox import event_to_inbox_card


def build_inbox_feed() -> dict[str, Any]:
    intel = build_intel_command_feed()
    items: list[dict[str, Any]] = []
    for c in intel.get("cards") if isinstance(intel.get("cards"), list) else []:
        items.append({"source_layer": "intelligence", "format": "command_card", "payload": c})
    lead_card = event_to_inbox_card(
        {
            "event_type": EventType.LEAD_RECEIVED.value,
            "source": "trusted_simulation",
            "channel_id": "website_form",
            "lead_name": "عميل تجريبي",
        }
    )
    items.append({"source_layer": "platform", "format": "inbox_card", "payload": lead_card})
    email_card = event_to_inbox_card(
        {
            "event_type": EventType.EMAIL_RECEIVED.value,
            "channel_id": "gmail",
            "subject_ar": "استفسار عن الباقات",
        }
    )
    items.append({"source_layer": "platform", "format": "inbox_card", "payload": email_card})
    review_card = event_to_inbox_card(
        {
            "event_type": EventType.REVIEW_CREATED.value,
            "channel_id": "google_business_profile",
            "rating": 2,
        }
    )
    items.append({"source_layer": "platform", "format": "inbox_card", "payload": review_card})
    return {"items": items, "count": len(items), "demo": True, "approval_required": False}
