"""Pricing engine — quotes + setup + monthly + post-service plan."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service


def quote_service(
    service_id: str,
    *,
    company_size: str = "small",
    urgency: str = "normal",
    channels_count: int = 1,
) -> dict[str, Any]:
    """Quote a service with company-size + urgency + channels multipliers."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    p_min = float(s.pricing_min_sar)
    p_max = float(s.pricing_max_sar)
    if p_min == 0 and p_max == 0:
        return {
            "service_id": service_id,
            "is_free": True,
            "estimated_min_sar": 0,
            "estimated_max_sar": 0,
            "currency": "SAR",
            "notes_ar": "خدمة مجانية. تتطلب اعتماد قبل التسليم.",
        }

    size_mult = {"micro": 0.8, "small": 1.0, "medium": 1.3, "large": 1.7}.get(
        company_size, 1.0,
    )
    urgency_mult = {"normal": 1.0, "rush": 1.3, "asap": 1.5}.get(urgency, 1.0)
    ch_mult = 1.0 + max(0, channels_count - 1) * 0.15

    return {
        "service_id": service_id,
        "estimated_min_sar": round(p_min * size_mult * urgency_mult * ch_mult),
        "estimated_max_sar": round(p_max * size_mult * urgency_mult * ch_mult),
        "currency": "SAR",
        "factors": {
            "company_size": company_size,
            "urgency": urgency,
            "channels_count": channels_count,
        },
        "pricing_model": s.pricing_model,
    }


def calculate_setup_fee(service_id: str) -> dict[str, Any]:
    """Suggest a setup fee for monthly services."""
    s = get_service(service_id)
    if s is None or s.pricing_model != "monthly":
        return {"setup_fee_sar": 0, "currency": "SAR"}
    base = s.pricing_min_sar
    return {
        "setup_fee_sar": int(base * 1.0),  # ~one month equivalent
        "includes_ar": [
            "ربط القنوات (واتساب/إيميل/تقويم)",
            "استيراد القوائم وتصنيف المصادر",
            "تدريب الفريق على Approval Center",
            "بناء أول Proof Pack",
        ],
        "currency": "SAR",
    }


def calculate_monthly_offer(service_id: str) -> dict[str, Any]:
    """Return monthly-pricing detail (for monthly services only)."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    if s.pricing_model != "monthly":
        return {
            "service_id": service_id,
            "is_monthly": False,
            "notes_ar": "هذه الخدمة ليست شهرية.",
        }
    return {
        "service_id": service_id,
        "is_monthly": True,
        "monthly_sar": s.pricing_min_sar,
        "annual_discount_pct": 15,
        "annual_total_sar": int(s.pricing_min_sar * 12 * 0.85),
        "currency": "SAR",
    }


def recommend_plan_after_service(
    service_id: str,
    *,
    outcome: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """After a service runs, recommend an upgrade plan."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    outcome = outcome or {}

    upgrade_targets = list(s.upgrade_path) or ["growth_os_monthly"]
    next_id = upgrade_targets[0]
    next_s = get_service(next_id)

    return {
        "from_service": service_id,
        "recommended_upgrade": next_id,
        "name_ar": next_s.name_ar if next_s else next_id,
        "monthly_sar": next_s.pricing_min_sar if next_s else 0,
        "reason_ar": (
            f"بعد إثبات قيمة {s.name_ar}، الخطوة الطبيعية هي "
            f"الاستمرار مع {next_s.name_ar if next_s else next_id} "
            "للحصول على نتائج شهرية مستمرة."
        ),
    }
