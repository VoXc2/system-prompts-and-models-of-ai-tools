"""Daily autopilot — يومياً يبني brief + يقترح أفعال + ينظمها بالأولوية."""

from __future__ import annotations

from typing import Any


def build_daily_targeting_brief(
    company_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build today's Arabic targeting brief for the founder/growth manager."""
    company_profile = company_profile or {}
    sector = company_profile.get("sector", "saas")
    city = company_profile.get("city", "Riyadh")

    return {
        "greeting_ar": "صباح الخير 👋",
        "summary_ar": [
            f"عندك اليوم: 10 شركات جديدة مناسبة في قطاع {sector} ({city}).",
            "5 رسائل drafts تنتظر اعتمادك.",
            "3 leads متأخرة في المتابعة (>72 ساعة).",
            "1 فرصة شريك في جدة جاهزة للتواصل.",
            "1 قناة (واتساب) تحتاج مراجعة سمعة.",
        ],
        "priority_decisions_ar": [
            "اعتمد 5 رسائل إيميل (10 دقائق).",
            "راجع 12 رقم بدون مصدر واضح قبل أي واتساب.",
            "احجز ديمو مع شريك الوكالة هذا الأسبوع.",
        ],
        "do_not_do_today_ar": [
            "لا تفعّل live WhatsApp send.",
            "لا ترفع قائمة باردة بدون تصنيف مصدر.",
            "لا تعد بنتائج مضمونة في الرسائل.",
        ],
    }


def recommend_today_actions(
    company_profile: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return ordered actions for today (deterministic 7-action set)."""
    company_profile = company_profile or {}
    return [
        {"id": "approve_5_email_drafts", "label_ar": "اعتمد 5 مسودات إيميل",
         "minutes": 10, "approval_required": True, "priority": 1},
        {"id": "review_unknown_source_contacts", "label_ar": "راجع 12 رقم بدون مصدر",
         "minutes": 8, "approval_required": True, "priority": 2},
        {"id": "schedule_partner_demo", "label_ar": "احجز ديمو شريك",
         "minutes": 5, "approval_required": True, "priority": 3},
        {"id": "respond_to_overdue_leads", "label_ar": "رد على 3 leads متأخرة",
         "minutes": 12, "approval_required": True, "priority": 4},
        {"id": "review_whatsapp_quality", "label_ar": "راجع مؤشرات سمعة واتساب",
         "minutes": 5, "approval_required": False, "priority": 5},
        {"id": "draft_one_partner_message", "label_ar": "اكتب رسالة شريك وكالة",
         "minutes": 8, "approval_required": True, "priority": 6},
        {"id": "log_proof_events", "label_ar": "حدّث Proof Ledger",
         "minutes": 3, "approval_required": False, "priority": 7},
    ]


def prioritize_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort cards by `priority` (asc), then by `risk_level` (high first)."""
    risk_rank = {"high": 0, "medium": 1, "low": 2, None: 3}
    return sorted(
        cards,
        key=lambda c: (
            int(c.get("priority", 99)),
            risk_rank.get(c.get("risk_level"), 9),
        ),
    )


def build_end_of_day_report(
    day_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build today's Arabic end-of-day report from metrics."""
    m = day_metrics or {}
    accounts = int(m.get("accounts_analyzed", 32))
    opps = int(m.get("opportunities_generated", 10))
    drafts = int(m.get("drafts_approved", 6))
    replies = int(m.get("positive_replies", 2))
    meetings = int(m.get("meetings_drafted", 1))
    risks = int(m.get("risks_blocked", 8))

    return {
        "today_metrics": {
            "accounts_analyzed": accounts,
            "opportunities_generated": opps,
            "drafts_approved": drafts,
            "positive_replies": replies,
            "meetings_drafted": meetings,
            "risks_blocked": risks,
        },
        "summary_ar": [
            f"تم تحليل {accounts} حساب اليوم.",
            f"تم توليد {opps} فرصة جديدة.",
            f"تم اعتماد {drafts} مسودة.",
            f"تم تسجيل {replies} رد إيجابي.",
            f"تم تجهيز {meetings} اجتماع.",
            f"تم منع {risks} مخاطر تلقائياً.",
        ],
        "tomorrow_recommendation_ar": (
            "غداً: ركّز على متابعة الردود الإيجابية أولاً، ثم اعتماد رسائل جديدة، "
            "ثم جدولة 1-2 ديمو إن أمكن."
        ),
    }
