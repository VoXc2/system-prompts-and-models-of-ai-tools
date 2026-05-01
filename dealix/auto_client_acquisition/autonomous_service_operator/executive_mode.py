"""Executive Mode — CEO command center + daily brief + revenue risks."""

from __future__ import annotations

from typing import Any


def build_executive_daily_brief(
    *,
    company_name: str = "",
    sector: str = "saas",
) -> dict[str, Any]:
    """Build the CEO's daily brief (Arabic)."""
    return {
        "title_ar": f"موجز اليوم التنفيذي — {company_name or '(الشركة)'}",
        "summary_ar": [
            f"3 قرارات تنتظر اعتمادك في قطاع {sector}.",
            "5 رسائل drafts معدّة بـ Saudi tone.",
            "2 leads متأخرة في المتابعة (>72 ساعة).",
            "1 شريك وكالة جاهز لاجتماع.",
            "1 خطر سمعة على قناة (يحتاج مراجعة).",
        ],
        "priority_decisions_ar": [
            "اعتمد 5 رسائل إيميل (10 دقائق).",
            "راجع 12 رقم بدون مصدر واضح قبل أي واتساب.",
            "احجز ديمو شريك الوكالة.",
        ],
        "metric_to_watch_ar": (
            "نسبة approval_rate الأسبوعية — هي المؤشر الأقوى لجودة "
            "الـ targeting + الـ Saudi Tone."
        ),
        "buttons_ar": ["اعرض القرارات", "Proof Pack", "لاحقاً"],
        "approval_required": True,
    }


def build_revenue_risks_summary(
    *,
    open_risks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a 3-risk summary (Arabic)."""
    open_risks = open_risks or [
        {
            "id": "wa_quality",
            "title_ar": "جودة واتساب",
            "summary_ar": "نسبة الحظر على رقم واتساب الرئيسي تقترب من حد التحذير.",
            "severity": "high",
            "action_ar": "خفّض الحجم 50% + راجع الرسائل.",
        },
        {
            "id": "list_freshness",
            "title_ar": "قائمة قديمة",
            "summary_ar": "60% من القائمة لم يتم تحديثها منذ 9 أشهر.",
            "severity": "medium",
            "action_ar": "شغّل List Intelligence لتنظيفها.",
        },
        {
            "id": "single_threading",
            "title_ar": "صفقة بشخص واحد",
            "summary_ar": "صفقة كبيرة (250K) معتمدة على شخص واحد بدون buying committee.",
            "severity": "high",
            "action_ar": "ادعُ صانع قرار ثانٍ من نفس الشركة.",
        },
    ]
    return {
        "title_ar": "أعلى 3 مخاطر إيراد اليوم",
        "risks": open_risks[:3],
        "approval_required": True,
    }


def build_ceo_command_center(
    *,
    company_name: str = "",
    sector: str = "saas",
) -> dict[str, Any]:
    """Build the full CEO command-center page."""
    return {
        "mode": "ceo",
        "company_name": company_name,
        "daily_brief": build_executive_daily_brief(
            company_name=company_name, sector=sector,
        ),
        "revenue_risks": build_revenue_risks_summary(),
        "next_three_moves_ar": [
            "اعتمد رسائل اليوم (5).",
            "ابدأ Pilot 7 أيام لقطاع جديد (testing).",
            "حدد منسّق Approvals بديل خلال 24 ساعة.",
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }
