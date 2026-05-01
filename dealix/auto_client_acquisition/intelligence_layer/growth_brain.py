"""Growth profile from JSON — no LLM required for MVP."""

from __future__ import annotations

import hashlib
import json
from typing import Any

_DEFAULT_BLOCKED = (
    "cold_whatsapp",
    "auto_linkedin_dm",
    "bulk_send_without_approval",
    "purchased_list_bulk",
)


def _growth_brain_id(company: dict[str, Any]) -> str:
    payload = json.dumps(company, ensure_ascii=False, sort_keys=True, default=str)
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return f"gb_{h}"


def build_growth_profile(company: dict[str, Any] | None) -> dict[str, Any]:
    c = company or {}
    company_name = str(c.get("company_name") or c.get("name") or "غير مسمّى")
    sector = str(c.get("sector") or "غير محدد")
    city = str(c.get("city") or "الرياض")
    goal_ar = str(c.get("goal_ar") or c.get("goal") or "تسريع خط أنابيب المبيعات")
    icp_hint_ar = str(c.get("icp_hint_ar") or "قرارات شراء في المؤسسات متوسطة الحجم")
    risk = str(c.get("risk_tolerance") or c.get("risk") or "medium").lower()
    channels_in = c.get("channels")
    channels: list[str] = []
    if isinstance(channels_in, list):
        channels = [str(x).strip().lower() for x in channels_in if str(x).strip()]

    blocked = list(_DEFAULT_BLOCKED)
    if risk == "low":
        blocked = ["cold_whatsapp", "purchased_list_bulk", "auto_linkedin_dm"]
    elif risk == "high":
        blocked = list(_DEFAULT_BLOCKED) + ["unsupervised_payment_capture"]

    tone = "professional_saudi_short"
    if risk == "low":
        tone = "warm_saudi_concise"
    elif risk == "high":
        tone = "formal_saudi_minimal"

    recommended_first_mission = "ten_in_ten_opportunities"
    if c.get("recommended_first_mission"):
        recommended_first_mission = str(c.get("recommended_first_mission"))

    seed_obj = {
        "company_name": company_name,
        "sector": sector,
        "city": city,
        "goal_ar": goal_ar,
        "channels": channels,
        "risk_tolerance": risk,
    }
    return {
        "growth_brain_id": _growth_brain_id(seed_obj),
        "company_name": company_name,
        "sector": sector,
        "city": city,
        "goal_ar": goal_ar,
        "icp_hint_ar": icp_hint_ar,
        "channels_connected": channels or ["whatsapp", "email"],
        "blocked_actions": blocked,
        "recommended_first_mission": recommended_first_mission,
        "tone": tone,
        "best_segments": _suggest_segments(sector),
        "demo": True,
    }


def _suggest_segments(sector: str) -> list[str]:
    s = sector.lower()
    if "training" in s or "تدريب" in s or "consult" in s:
        return ["مدراء الموارد البشرية", "مدراء المبيعات", "رؤساء التعلم والتطوير"]
    if "health" in s or "صح" in s or "clinic" in s:
        return ["مدراء العيادات", "مشتريات طبية", "عمليات"]
    return ["صناع القرار المالي", "مدراء المشتريات", "العمليات"]
