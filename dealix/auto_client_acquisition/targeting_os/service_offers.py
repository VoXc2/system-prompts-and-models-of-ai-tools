"""Sellable services metadata — aligns with platform service_catalog where possible."""

from __future__ import annotations

from typing import Any

_SERVICES: list[dict[str, Any]] = [
    {
        "id": "list_intelligence",
        "name_ar": "ذكاء القوائم",
        "target_customer": "شركات عندها CSV عملاء",
        "outcome_ar": "تصنيف وcontactability",
        "pricing_model": "fixed_sprint",
        "price_hint_sar": "499-1500",
        "required_integrations": [],
        "proof_metric": "safe_vs_blocked_ratio",
    },
    {
        "id": "first_10_sprint",
        "name_ar": "سباق 10 فرص",
        "target_customer": "B2B سعودي",
        "outcome_ar": "10 فرص + مسودات",
        "pricing_model": "fixed_sprint",
        "price_hint_sar": "499-1500",
        "required_integrations": [],
        "proof_metric": "opportunities_accepted",
    },
    {
        "id": "growth_os_monthly",
        "name_ar": "Growth OS شهري",
        "target_customer": "فرق مبيعات",
        "outcome_ar": "تشغيل يومي + Proof",
        "pricing_model": "subscription",
        "price_hint_sar": "2999+",
        "required_integrations": ["gmail", "calendar"],
        "proof_metric": "meetings_booked",
    },
    {
        "id": "partner_sprint",
        "name_ar": "سباق شراكات",
        "target_customer": "وكالات",
        "outcome_ar": "قائمة شركاء + مسودات",
        "pricing_model": "project",
        "price_hint_sar": "3000-7500",
        "required_integrations": [],
        "proof_metric": "partner_meetings",
    },
]


def list_targeting_services() -> dict[str, Any]:
    return {"services": list(_SERVICES), "count": len(_SERVICES), "demo": True}


def recommend_service_offer(customer_type: str, goal: str) -> dict[str, Any]:
    ct = (customer_type or "").lower()
    if "agency" in ct:
        return {"recommended": "partner_sprint", "reason_ar": "الوكالات تنقل Dealix لعملائها.", "demo": True}
    if "list" in goal.lower() or "csv" in goal.lower():
        return {"recommended": "list_intelligence", "reason_ar": "تنظيف القائمة أولاً يقلل المخاطر.", "demo": True}
    return {"recommended": "first_10_sprint", "reason_ar": "أسرع إثبات قيمة.", "demo": True}


def build_offer_card(service_id: str) -> dict[str, Any]:
    for s in _SERVICES:
        if s["id"] == service_id:
            return {**s, "buttons": ["اطلب عرضاً", "تفاصيل", "لاحقاً"]}
    return {"error": "unknown_service", "demo": True}


def estimate_service_price(service_id: str) -> dict[str, Any]:
    card = build_offer_card(service_id)
    return {"service_id": service_id, "price_hint_sar": card.get("price_hint_sar"), "demo": True}
