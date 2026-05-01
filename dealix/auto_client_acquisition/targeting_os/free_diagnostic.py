"""Free growth diagnostic — small preview, upsell to pilot."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.account_finder import recommend_accounts


def build_free_growth_diagnostic(company_profile: dict[str, Any]) -> dict[str, Any]:
    sector = str(company_profile.get("sector") or "b2b")
    city = str(company_profile.get("city") or "الرياض")
    acc = recommend_accounts(sector, city, company_profile.get("offer") or "خدمة", company_profile.get("goal") or "نمو", limit=3)
    opps = acc["accounts"][:3]
    return {
        "opportunities": opps,
        "sample_message_ar": "نقدّم تجربة 7 أيام مع مسودات معتمدة — هل نرسل ملخصاً؟",
        "risk_ar": "تأكد من opt-in قبل أي واتساب جماعي.",
        "next_step_ar": "اطلب Pilot بـ 499 ريال أو ما يعادله بعد الاتفاق.",
        "demo": True,
    }


def analyze_uploaded_list_preview(contacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Thin wrapper shape for router; full analysis uses platform import preview."""
    return {"row_count": len(contacts), "hint_ar": "استخدم POST /api/v1/platform/contacts/import-preview للتحليل الكامل.", "demo": True}


def recommend_paid_pilot_offer(diagnostic: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "First 10 Opportunities Sprint",
        "price_hint_sar": "499-1500",
        "includes_ar": ["10 فرص", "10 مسودات", "Proof Pack مصغر"],
        "demo": True,
    }


def build_mini_proof_plan() -> dict[str, Any]:
    return {"week_1": ["فرص", "مسودات"], "week_2": ["متابعة", "تقرير"], "demo": True}
