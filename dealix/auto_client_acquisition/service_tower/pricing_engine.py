"""Deterministic SAR quotes — hints only, not binding contracts."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def quote_service(
    service_id: str,
    company_size: str = "smb",
    urgency: str = "normal",
    channels_count: int = 1,
) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    if not svc:
        return {"ok": False, "error": "unknown_service", "demo": True}
    pr = svc.get("pricing_range_sar") or {"min": 0, "max": 0}
    lo = int(pr.get("min", 0))
    hi = int(pr.get("max", lo))
    mult = 1.0
    if (company_size or "").lower() in ("enterprise", "large"):
        mult *= 1.15
    if (urgency or "").lower() == "high":
        mult *= 1.1
    mult += 0.05 * max(0, min(channels_count, 6) - 1)
    lo_q = int(lo * mult)
    hi_q = int(hi * mult)
    return {
        "ok": True,
        "service_id": service_id,
        "quoted_range_sar": {"min": lo_q, "max": hi_q},
        "factors": {"company_size": company_size, "urgency": urgency, "channels_count": channels_count},
        "not_binding": True,
        "demo": True,
    }


def recommend_plan_after_service(service_id: str, outcome: str) -> dict[str, Any]:
    outcome_l = (outcome or "").lower()
    svc = get_service_by_id(service_id)
    nxt = (svc or {}).get("upgrade_path") or "growth_os"
    if "churn" in outcome_l:
        nxt = "executive_growth_brief"
    return {"next_plan": nxt, "reason_ar": "مسار ترقية افتراضي حسب الكتالوج.", "demo": True}


def calculate_setup_fee(service_id: str) -> dict[str, Any]:
    q = quote_service(service_id, company_size="smb", urgency="normal", channels_count=1)
    r = q.get("quoted_range_sar") or {}
    setup = int((r.get("min", 0) + r.get("max", 0)) // 4)
    return {"service_id": service_id, "setup_fee_hint_sar": setup, "demo": True}


def calculate_monthly_offer(service_id: str) -> dict[str, Any]:
    if service_id == "growth_os":
        return {"service_id": service_id, "monthly_hint_sar": 2999, "demo": True}
    if service_id == "self_growth_operator":
        return {"service_id": service_id, "monthly_hint_sar": 999, "demo": True}
    return {"service_id": service_id, "monthly_hint_sar": None, "note_ar": "خدمة مشروع/سباق — لا اشتراك افتراضي.", "demo": True}
