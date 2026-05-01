"""Command Feed engine — aggregates events across channels into a daily feed."""

from __future__ import annotations

from typing import Any

from .event_to_card import build_card_from_event


def build_command_feed_for_customer(
    *,
    customer_id: str,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build today's Arabic command feed for a customer."""
    events = events or []
    cards = [build_card_from_event(e) for e in events]
    by_type: dict[str, int] = {}
    by_risk: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
    for c in cards:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
        by_risk[c["risk_level"]] = by_risk.get(c["risk_level"], 0) + 1

    # Sort: high risk first, then medium, then low. Stable.
    risk_order = {"high": 0, "medium": 1, "low": 2}
    cards_sorted = sorted(cards, key=lambda c: risk_order.get(c["risk_level"], 9))

    return {
        "customer_id": customer_id,
        "feed_size": len(cards),
        "by_type": by_type,
        "by_risk": by_risk,
        "cards": cards_sorted,
        "approval_required": True,
    }


def build_command_feed_demo() -> dict[str, Any]:
    """Demo feed with 8 synthetic events across all channels."""
    demo_events = [
        {"event_type": "email.received", "customer_id": "demo",
         "payload": {"from": "ali@example.sa", "subject": "نطلب عرض"}},
        {"event_type": "whatsapp.reply_received", "customer_id": "demo",
         "payload": {"text": "شكرًا، أبغى أعرف باقات الشركات"}},
        {"event_type": "form.submitted", "customer_id": "demo",
         "payload": {"company": "شركة نمو", "role": "Head of Sales"}},
        {"event_type": "review.created", "customer_id": "demo",
         "payload": {"rating": 2, "text": "تأخير في الرد"}},
        {"event_type": "payment.link_created", "customer_id": "demo",
         "payload": {"amount_sar": 499, "description": "Pilot 7d"}},
        {"event_type": "risk.blocked", "customer_id": "demo",
         "payload": {"reason_ar": "محاولة cold WhatsApp بدون opt-in"}},
        {"event_type": "partner.suggested", "customer_id": "demo",
         "payload": {"partner_type": "agency",
                     "reason_ar": "وكالة B2B لديها 20 عميل في قطاع التدريب"}},
        {"event_type": "service.completed", "customer_id": "demo",
         "payload": {"service_id": "first_10_opportunities_sprint"}},
    ]
    return build_command_feed_for_customer(
        customer_id="demo", events=demo_events,
    )
