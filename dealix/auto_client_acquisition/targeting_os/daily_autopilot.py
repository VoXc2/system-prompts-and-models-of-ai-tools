"""Daily targeting brief — cards only, no live sends."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.account_finder import recommend_accounts


def build_daily_targeting_brief(company_profile: dict[str, Any]) -> dict[str, Any]:
    sector = str(company_profile.get("sector") or "training")
    city = str(company_profile.get("city") or "الرياض")
    offer = str(company_profile.get("offer") or "Growth OS")
    goal = str(company_profile.get("goal") or "book_more_b2b_meetings")
    acc = recommend_accounts(sector, city, offer, goal, limit=5)
    cards = []
    for a in acc["accounts"][:5]:
        cards.append(
            {
                "type": "new_account",
                "title_ar": f"فرصة: {a['company']}",
                "summary_ar": a.get("why_now_ar", ""),
                "buttons": ["مسودة بريد", "تخطي", "تفاصيل"],
                "approval_required": True,
            }
        )
    cards.append(
        {
            "type": "approval_needed",
            "title_ar": "مراجعات معلّقة",
            "summary_ar": "هناك مسودات بانتظار موافقتك.",
            "buttons": ["افتح المسودات", "لاحقاً"],
            "approval_required": True,
        }
    )
    return {"date": "demo", "cards": cards[:10], "note_ar": "عرض فقط — لا إرسال.", "demo": True}


def recommend_today_actions(company_profile: dict[str, Any]) -> list[str]:
    return [
        "راجع أعلى 3 حسابات في القائمة",
        "اعتمد مسودتي بريد واحدة على الأقل",
        "حدّث حالة opt-in للواتساب",
    ]


def prioritize_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {"approval_needed": 0, "reputation_risk": 1, "new_account": 2}
    return sorted(cards, key=lambda c: order.get(str(c.get("type")), 9))


def build_end_of_day_report(day_metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "accounts_researched": day_metrics.get("accounts_researched", 12),
        "drafts_created": day_metrics.get("drafts_created", 4),
        "approvals_pending": day_metrics.get("approvals_pending", 2),
        "risks_blocked": day_metrics.get("risks_blocked", 3),
        "summary_ar": "تقرير نهاية اليوم — جاهز للمراجعة الإدارية.",
        "demo": True,
    }
