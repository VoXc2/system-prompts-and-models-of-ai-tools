"""Monthly ROI / proof pack — demo structures."""

from __future__ import annotations

from typing import Any


def build_demo_proof_pack() -> dict[str, Any]:
    return {
        "executive_summary_ar": "شهر تجريبي: 12 فرصة مؤهلة، 4 اجتماعات بعد موافقة، 0 إرسال بارد، 3 تسريبات إيرادات مكتشفة.",
        "pipeline_created_sar": 180000,
        "qualified_leads": 12,
        "meetings_booked": 4,
        "response_rates": {"whatsapp_opt_in": 0.41, "email": 0.18},
        "revenue_influenced_sar": 42000,
        "top_signals": ["hiring_sales", "booking_link", "new_branch"],
        "best_messages_ar": ["مقدمة قصيرة + سبب الآن + طلب اجتماع 20 دقيقة"],
        "blocked_risky_outreach": 6,
        "revenue_leaks_found": 3,
        "next_month_plan_ar": "توسيع قطاع واحد + ربط proof pack تلقائياً من Revenue Memory.",
        "roi_calculation": calculate_roi_summary(
            subscription_sar=2999,
            influenced_revenue_sar=42000,
            hours_saved=18,
        ),
        "renewal_recommendation_ar": "تجديد مع إضافة أداء مؤهل إذا وُجدت عقود تأهيل.",
    }


def calculate_roi_summary(
    *,
    subscription_sar: float,
    influenced_revenue_sar: float,
    hours_saved: float,
    hourly_cost_sar: float = 350.0,
) -> dict[str, Any]:
    saved_sar = hours_saved * hourly_cost_sar
    multiple = round((influenced_revenue_sar + saved_sar) / subscription_sar, 2) if subscription_sar else 0.0
    return {
        "subscription_sar": subscription_sar,
        "influenced_revenue_sar": influenced_revenue_sar,
        "time_value_sar": round(saved_sar, 2),
        "value_to_price_multiple": multiple,
    }


def grade_account_health(
    *,
    brief_opens_4w: int,
    approvals_4w: int,
    blocks_4w: int,
) -> dict[str, Any]:
    score = min(100, brief_opens_4w * 3 + approvals_4w * 5 + min(blocks_4w, 10) * 2)
    status = "healthy" if score >= 60 else "at_risk"
    return {"health_score": score, "status": status}
