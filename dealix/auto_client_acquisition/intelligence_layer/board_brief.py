"""Founder Shadow Board — weekly brief for founder/board."""

from __future__ import annotations

from typing import Any


def build_board_brief(
    *,
    customer_id: str = "demo",
    customer_name: str = "Demo Saudi B2B Co.",
    week_label: str = "May W1 2026",
    pipeline_added_sar: float = 185_000,
    revenue_won_sar: float = 30_000,
    meetings_booked: int = 14,
    risks_blocked: int = 21,
    leak_recovered_sar: float = 12_000,
) -> dict[str, Any]:
    """Generate the founder/board-ready weekly brief."""
    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "week_label": week_label,
        "decisions_required_ar": [
            "اعتماد رفع price على الـ Growth tier 10% — منافس رفع 15%.",
            "الموافقة على Partnership Sprint مع وكالة B2B في جدة.",
            "اختيار pilot vertical للشهر القادم (clinics vs training).",
        ],
        "top_opportunities_ar": [
            f"شركة العقار الذهبي — اجتماع غداً ({250_000:,} ريال محتمل).",
            f"3 leads inbound من LinkedIn Lead Forms ({36_000:,} ريال).",
            f"Reactivation campaign على 12 عميل خامل ({80_000:,} ريال).",
        ],
        "top_risks_ar": [
            "صفقة 250K معرضة (single-threaded) — تحتاج multi-thread.",
            "تأخر في الرد على 7 leads خلال 72+ ساعة.",
            "تقييم Google 2-نجوم بدون رد — يحتاج ≤24 ساعة.",
        ],
        "key_relationship_ar": (
            "خالد ع. (شريك في وكالة B2B جدة) — اقترح اجتماع 20 دقيقة الأسبوع القادم."
        ),
        "experiment_to_run_ar": (
            "اختبر رسالة قصيرة (≤4 سطور) بدلاً من النسخة الحالية على قطاع real_estate."
        ),
        "metric_to_watch_ar": (
            f"approve_rate الأسبوعي: الهدف ≥45% (آخر أسبوع 38%)."
        ),
        "money_summary": {
            "pipeline_added_sar": pipeline_added_sar,
            "revenue_won_sar": revenue_won_sar,
            "leak_recovered_sar": leak_recovered_sar,
            "risks_blocked_count": risks_blocked,
            "meetings_booked": meetings_booked,
        },
    }
