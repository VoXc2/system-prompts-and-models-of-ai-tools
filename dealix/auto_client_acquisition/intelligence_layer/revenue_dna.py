"""Revenue DNA — extract the company's growth fingerprint."""

from __future__ import annotations

from collections import Counter
from typing import Any


def extract_revenue_dna(
    *,
    customer_id: str,
    won_deals: list[dict[str, Any]] | None = None,
    replies: list[dict[str, Any]] | None = None,
    objections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Compute the customer's growth DNA.

    Inputs are optional; missing inputs return sensible defaults
    so the dashboard always has something to render.
    """
    won_deals = won_deals or []
    replies = replies or []
    objections = objections or []

    # Best channel = channel that produced the most won_deals
    chan_counter: Counter[str] = Counter()
    seg_counter: Counter[str] = Counter()
    angle_counter: Counter[str] = Counter()
    cycle_days: list[float] = []
    for d in won_deals:
        chan_counter[d.get("channel", "?")] += 1
        seg_counter[d.get("segment", "?")] += 1
        angle_counter[d.get("message_angle", "?")] += 1
        if "cycle_days" in d:
            cycle_days.append(float(d["cycle_days"]))

    # Common objection
    obj_counter: Counter[str] = Counter()
    for o in objections:
        obj_counter[o.get("objection_id", "?")] += 1

    next_experiment_ar = (
        "اختبر رسالة قصيرة (≤4 سطور) + CTA واحد على القناة الأنجح."
        if len(won_deals) >= 5 else
        "ركّز على بناء أول 10 deals عبر «10 فرص في 10 دقائق»."
    )

    return {
        "customer_id": customer_id,
        "best_channel": (chan_counter.most_common(1)[0][0] if chan_counter else "whatsapp"),
        "best_segment": (seg_counter.most_common(1)[0][0] if seg_counter else "inbound_lead"),
        "best_message_angle": (
            angle_counter.most_common(1)[0][0] if angle_counter
            else "value_first_short_arabic"
        ),
        "common_objection": (obj_counter.most_common(1)[0][0] if obj_counter else "send_offer_whatsapp"),
        "fastest_conversion_days": round(
            min(cycle_days) if cycle_days else 0, 1
        ),
        "median_conversion_days": round(
            sorted(cycle_days)[len(cycle_days) // 2] if cycle_days else 0, 1
        ),
        "deals_observed": len(won_deals),
        "next_experiment_ar": next_experiment_ar,
    }


def build_revenue_dna_demo() -> dict[str, Any]:
    """Demo Revenue DNA with realistic Saudi B2B values."""
    return extract_revenue_dna(
        customer_id="demo",
        won_deals=[
            {"channel": "whatsapp", "segment": "inbound_lead",
             "message_angle": "value_first_short_arabic", "cycle_days": 18},
            {"channel": "whatsapp", "segment": "existing_customer",
             "message_angle": "expansion_offer", "cycle_days": 12},
            {"channel": "email", "segment": "referral",
             "message_angle": "warm_intro", "cycle_days": 25},
            {"channel": "whatsapp", "segment": "event_lead",
             "message_angle": "value_first_short_arabic", "cycle_days": 30},
            {"channel": "whatsapp", "segment": "inbound_lead",
             "message_angle": "value_first_short_arabic", "cycle_days": 15},
        ],
        objections=[
            {"objection_id": "send_offer_whatsapp"},
            {"objection_id": "send_offer_whatsapp"},
            {"objection_id": "price_high"},
        ],
    )
