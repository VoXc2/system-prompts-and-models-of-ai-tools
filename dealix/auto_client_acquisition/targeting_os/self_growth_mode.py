"""Dealix self-growth plan — drafts and targets only, no auto outreach."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.account_finder import recommend_accounts


def build_dealix_self_growth_plan() -> dict[str, Any]:
    return {
        "focus_ar": "وكالات B2B ومستشارو نمو في الرياض وجدة",
        "weekly_goal": "5 ديمو + 2 pilot",
        "constraints_ar": "لا scraping، لا إرسال آلي — مسودات وموافقة فقط.",
        "demo": True,
    }


def recommend_dealix_targets(sector_focus: str, city_focus: str) -> dict[str, Any]:
    return recommend_accounts(sector_focus or "saas", city_focus or "الرياض", "Dealix Growth OS", "partner_channel", limit=8)


def build_free_service_offer(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_company": target.get("company"),
        "offer_ar": "تشخيص نمو مجاني: 3 فرص + رسالة واحدة + تقرير مخاطر مصغر.",
        "cta_ar": "احجز 15 دقيقة ديمو.",
        "approval_required": True,
        "demo": True,
    }


def build_self_growth_daily_brief() -> dict[str, Any]:
    t = recommend_dealix_targets("agency", "الرياض")
    return {
        "title_ar": "Dealix — Self Growth",
        "top_targets": t["accounts"][:3],
        "actions_ar": ["جهّز ديمو", "أرسل مسودة بريد يدوية بعد الموافقة", "حدّث قائمة المتابعة"],
        "demo": True,
    }


def build_weekly_learning_report(results: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_sector": results.get("best_sector", "training"),
        "best_message_angle": results.get("best_angle", "pilot_7_days"),
        "next_experiment_ar": "اختبر قطاع العيادات الأسبوع القادم.",
        "demo": True,
    }
