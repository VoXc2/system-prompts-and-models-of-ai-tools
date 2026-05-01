"""Optional English labels for revenue offer JSON (?lang=en) — keeps all Arabic keys."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from auto_client_acquisition.revenue_launch.offer_builder import (
    build_499_pilot_offer,
    build_growth_os_pilot_offer,
    build_private_beta_offer,
)

_EN_BY_OFFER_ID: dict[str, dict[str, Any]] = {
    "private_beta_shell": {
        "title_en": "Private beta — Dealix",
        "summary_en": "Limited pilot: opportunities, drafts, approvals, and proof — no live outbound by default.",
        "includes_en": ["Diagnostic or opportunity sprint", "Approval cards", "Trial proof pack"],
    },
    "pilot_7d_499": {
        "title_en": "Pilot — 7 days (499 SAR)",
        "summary_en": "Ten B2B opportunities with why-now, Arabic message drafts, contactability review, 7-day follow-up plan, short proof pack.",
        "deliverables_en": [
            "Short growth diagnostic or 3 sample opportunities",
            "10 B2B opportunities with why-now",
            "10 Arabic message drafts",
            "Contactability and risk review",
            "7-day follow-up plan",
            "Short proof pack",
        ],
        "payment_en": "Manual invoice or payment link via Moyasar dashboard — no in-app API charge at this stage.",
    },
    "growth_os_pilot_30d": {
        "title_en": "Growth OS pilot — 30 days",
        "summary_en": "Wider rhythm: daily brief, opportunities, list intelligence as applicable, channel drafts (no live send), weekly proof.",
        "deliverables_en": [
            "Trial daily brief",
            "10 opportunities + list intelligence where applicable",
            "Channel drafts (no live send)",
            "Weekly proof pack",
        ],
    },
}


def _merge_en(offer: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(offer)
    oid = str(out.get("offer_id") or "")
    extra = _EN_BY_OFFER_ID.get(oid)
    if extra:
        out.update(extra)
    return out


def build_revenue_offers_payload(lang: str) -> dict[str, Any]:
    """Return bundle for GET /revenue-launch/offer; lang 'en' adds *_en fields alongside Arabic."""
    ln = (lang or "ar").lower()
    if ln not in ("ar", "en"):
        ln = "ar"
    p = build_private_beta_offer()
    q = build_499_pilot_offer()
    g = build_growth_os_pilot_offer()
    if ln == "en":
        p = _merge_en(p)
        q = _merge_en(q)
        g = _merge_en(g)
    return {
        "locale": ln,
        "private_beta_shell": p,
        "pilot_499": q,
        "growth_os_pilot": g,
        "no_live_send": True,
        "no_live_charge": True,
        "demo": True,
    }
