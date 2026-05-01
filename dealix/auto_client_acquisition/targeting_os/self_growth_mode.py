"""Self-Growth Mode — Dealix يستهدف عملاءه ويصنع فرصاً لنفسه."""

from __future__ import annotations

from typing import Any

from .account_finder import recommend_accounts
from .buyer_role_mapper import map_buying_committee
from .daily_autopilot import (
    build_daily_targeting_brief,
    recommend_today_actions,
)


# Dealix's own ICP (deterministic).
DEALIX_ICP_FOCUSES: tuple[dict[str, str], ...] = (
    {"sector": "agency", "city": "Riyadh", "label_ar": "وكالات تسويق B2B في الرياض"},
    {"sector": "training", "city": "Riyadh", "label_ar": "شركات تدريب B2B في الرياض"},
    {"sector": "consulting", "city": "Riyadh", "label_ar": "شركات استشارات نمو"},
    {"sector": "saas", "city": "Riyadh", "label_ar": "SaaS سعودية صغيرة-متوسطة"},
    {"sector": "real_estate", "city": "Jeddah", "label_ar": "وسطاء عقار B2B في جدة"},
)


def recommend_dealix_targets(
    *,
    sector_focus: str | None = None,
    city_focus: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Build Dealix's own daily target list."""
    sector = sector_focus or DEALIX_ICP_FOCUSES[0]["sector"]
    city = city_focus or DEALIX_ICP_FOCUSES[0]["city"]
    accounts = recommend_accounts(
        sector=sector, city=city, goal="self_growth",
        offer="Pilot 7 أيام لاستخراج 10 فرص B2B",
        limit=limit,
    )
    committee = map_buying_committee(sector=sector, company_size="small",
                                     goal="fill_pipeline")
    return {
        "icp": {"sector": sector, "city": city},
        "targets": accounts,
        "buying_committee_template": committee,
        "approval_required": True,
        "live_send_allowed": False,
        "notes_ar": (
            "هذه قائمة استهداف Dealix لنفسه. كل تواصل draft فقط، "
            "ولا يُرسل إلا بعد اعتماد المؤسس."
        ),
    }


def build_free_service_offer(target: dict[str, Any]) -> dict[str, Any]:
    """Build a 'Free Growth Diagnostic' offer card for a single target."""
    company = target.get("name", "?")
    return {
        "target_company": company,
        "offer_id": "free_growth_diagnostic",
        "title_ar": f"تشخيص نمو مجاني لـ{company}",
        "deliverables_ar": [
            "3 فرص B2B مناسبة لقطاعكم.",
            "1 رسالة عربية مخصصة.",
            "1 تقرير مخاطر سريع.",
            "1 خطة Pilot مقترحة.",
        ],
        "delivery_time": "خلال 24 ساعة عمل",
        "price": 0,
        "currency": "SAR",
        "follow_up_offer_ar": (
            "إذا أعجبكم، نكمل Pilot 7 أيام بـ499 ريال أو مجاني مقابل case study."
        ),
        "approval_required": True,
    }


def build_self_growth_daily_brief(
    *,
    sector_focus: str | None = None,
    city_focus: str | None = None,
) -> dict[str, Any]:
    """Build today's self-growth brief for Dealix (founder-facing)."""
    sector = sector_focus or DEALIX_ICP_FOCUSES[0]["sector"]
    city = city_focus or DEALIX_ICP_FOCUSES[0]["city"]
    company_brief = build_daily_targeting_brief({"sector": sector, "city": city})
    actions = recommend_today_actions({"sector": sector, "city": city})

    targets = recommend_dealix_targets(
        sector_focus=sector, city_focus=city, limit=10,
    )

    return {
        "icp": {"sector": sector, "city": city},
        "company_brief": company_brief,
        "today_actions": actions,
        "top_10_targets": targets["targets"]["accounts"][:10],
        "recommended_first_action_ar": (
            "ابعث 3 رسائل Free Diagnostic مخصصة هذا الصباح، "
            "ثم تابع 2 ديمو من الأمس."
        ),
    }


def build_weekly_learning_report(
    results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a weekly Arabic learning report from Dealix's own results."""
    r = results or {}
    diagnostics = int(r.get("free_diagnostics_delivered", 0))
    pilots = int(r.get("paid_pilots_started", 0))
    meetings = int(r.get("meetings_held", 0))
    case_studies = int(r.get("case_studies_published", 0))
    revenue = float(r.get("revenue_sar", 0))

    return {
        "week_metrics": {
            "free_diagnostics": diagnostics,
            "paid_pilots": pilots,
            "meetings": meetings,
            "case_studies": case_studies,
            "revenue_sar": revenue,
        },
        "learning_questions_ar": [
            "أي قطاع رد أكثر هذا الأسبوع؟",
            "أي رسالة نجحت؟ ولماذا؟",
            "أي قناة فعّالة (إيميل / لينكدإن / شركاء)؟",
            "أي اعتراض تكرر أكثر من مرتين؟",
            "ما العرض الذي يبيع بسهولة؟",
        ],
        "next_week_experiments_ar": [
            "جرّب angle جديد لقطاع التدريب: ROI ملموس لـHR.",
            "أرسل Free Diagnostic لـ20 وكالة تسويق.",
            "اعقد ديمو واحد مع شركة SaaS سعودية.",
            "اطلب أول case study من أنجح Pilot.",
        ],
    }


def build_dealix_self_growth_plan() -> dict[str, Any]:
    """Top-level monthly plan for Dealix using its own OS to grow."""
    return {
        "icp_focuses": list(DEALIX_ICP_FOCUSES),
        "monthly_targets": {
            "free_diagnostics_delivered": 30,
            "paid_pilots_started": 6,
            "growth_os_subscriptions": 3,
            "agency_partners_signed": 1,
            "case_studies_published": 1,
        },
        "operating_loop_ar": [
            "كل صباح: اعرض 10 شركات جديدة + 5 رسائل drafts.",
            "كل ظهر: راجع الردود + جدول 1-2 ديمو.",
            "كل مساء: حدّث Proof Ledger + أرسل Free Diagnostic لـ3 شركات.",
            "كل أسبوع: اكتب learning report + جرّب angle جديد.",
            "كل شهر: راجع Service Excellence Score لكل خدمة.",
        ],
    }
