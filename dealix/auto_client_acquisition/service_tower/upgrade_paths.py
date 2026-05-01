"""Upgrade paths — يوصي بالخدمة التالية بعد كل خدمة."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service


def recommend_upgrade(
    service_id: str,
    *,
    results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Recommend the next service for a customer to buy."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    upgrade_targets = list(s.upgrade_path) or ["growth_os_monthly"]
    next_id = upgrade_targets[0]
    next_s = get_service(next_id)

    return {
        "from_service": service_id,
        "from_service_name_ar": s.name_ar,
        "recommended_service_id": next_id,
        "recommended_service_name_ar": next_s.name_ar if next_s else next_id,
        "monthly_sar": next_s.pricing_min_sar if next_s else 0,
        "reason_ar": (
            f"بعد {s.name_ar}، الترقية الطبيعية هي "
            f"{next_s.name_ar if next_s else next_id} للحفاظ على الاستمرارية."
        ),
    }


def build_upsell_message_ar(
    service_id: str,
    next_offer: str,
) -> str:
    """Build a one-paragraph Arabic upsell message."""
    s = get_service(service_id)
    next_s = get_service(next_offer)
    if not s or not next_s:
        return "بعد إثبات النتائج، نوصي بالترقية للخدمة التالية."
    return (
        f"شاكر لك على تجربة {s.name_ar}. "
        f"بناءً على النتائج، الترقية المنطقية هي {next_s.name_ar} "
        "للاستمرار في النمو شهرياً مع نفس مستوى الـ Proof Pack. "
        "أرسل لي تأكيد ونبدأ الأسبوع القادم."
    )


def map_service_to_subscription(service_id: str) -> str:
    """Map any service to its eventual subscription."""
    s = get_service(service_id)
    if s is None:
        return "growth_os_monthly"
    return s.upgrade_path[0] if s.upgrade_path else "growth_os_monthly"
