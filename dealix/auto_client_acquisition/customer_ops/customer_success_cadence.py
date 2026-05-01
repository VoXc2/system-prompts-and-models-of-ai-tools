"""Customer Success cadence — weekly check-ins + at-risk alerts."""

from __future__ import annotations

from typing import Any

# Cadence types Dealix supports.
CADENCE_TYPES: tuple[str, ...] = (
    "weekly_check_in",
    "monthly_proof_review",
    "quarterly_business_review",
    "at_risk_alert",
    "renewal_30_day",
    "renewal_7_day",
)


def build_weekly_check_in(
    *,
    customer_id: str = "",
    company_name: str = "",
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a weekly check-in agenda + Arabic talking points."""
    m = metrics or {}
    drafts = int(m.get("drafts_approved", 0))
    replies = int(m.get("replies", 0))
    meetings = int(m.get("meetings", 0))
    risks = int(m.get("risks_blocked", 0))
    pipeline = float(m.get("pipeline_sar", 0))

    return {
        "customer_id": customer_id,
        "company_name": company_name,
        "type": "weekly_check_in",
        "agenda_ar": [
            "مراجعة آخر Proof Pack (5 دقائق).",
            "أبرز فرصة في الـ pipeline (5 دقائق).",
            "أبرز خطر في القنوات (5 دقائق).",
            "خطة الأسبوع القادم (5 دقائق).",
            "أي مساعدة من فريقنا؟ (5 دقائق).",
        ],
        "talking_points_ar": [
            f"اعتمدتم {drafts} رسالة هذا الأسبوع، ووصلكم {replies} رد.",
            f"تم تجهيز {meetings} اجتماع.",
            f"تم منع {risks} مخاطر تلقائياً.",
            f"Pipeline متأثر بقيمة {pipeline:.0f} ريال.",
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_at_risk_alert(
    *,
    customer_id: str = "",
    days_inactive: int = 0,
    drafts_pending: int = 0,
    last_proof_pack_days_ago: int = 0,
) -> dict[str, Any]:
    """Build an at-risk alert when a customer shows churn signals."""
    risk_score = 0
    reasons: list[str] = []

    if days_inactive >= 14:
        risk_score += 40
        reasons.append(f"العميل غير نشط منذ {days_inactive} يوم.")
    elif days_inactive >= 7:
        risk_score += 20
        reasons.append(f"انخفاض النشاط منذ {days_inactive} يوم.")

    if drafts_pending >= 10:
        risk_score += 25
        reasons.append(f"{drafts_pending} مسودة معلقة بدون اعتماد.")
    elif drafts_pending >= 5:
        risk_score += 10
        reasons.append(f"تراكم {drafts_pending} مسودة بدون اعتماد.")

    if last_proof_pack_days_ago >= 14:
        risk_score += 30
        reasons.append(
            f"آخر Proof Pack قبل {last_proof_pack_days_ago} يوم — يتجاوز SLA."
        )

    risk_score = min(100, risk_score)
    if risk_score >= 60:
        severity = "high"
        action_ar = "أرسل إيميل personal من المؤسس + احجز QBR هذا الأسبوع."
    elif risk_score >= 30:
        severity = "medium"
        action_ar = "أرسل Proof Pack ملخص + اقترح ديمو لخدمة جديدة."
    else:
        severity = "low"
        action_ar = "متابعة weekly check-in عادية."

    return {
        "customer_id": customer_id,
        "type": "at_risk_alert",
        "risk_score": risk_score,
        "severity": severity,
        "reasons_ar": reasons,
        "recommended_action_ar": action_ar,
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_customer_success_plan(
    *,
    customer_id: str = "",
    bundle_id: str = "growth_starter",
) -> dict[str, Any]:
    """Build a 30-day customer success cadence plan."""
    cadence_by_bundle = {
        "growth_starter": [
            "Day 1: kick-off call + intake.",
            "Day 3: review first 3 opportunities + drafts.",
            "Day 7: deliver Proof Pack v1.",
            "Day 14: weekly check-in + upsell offer.",
            "Day 30: monthly proof review + renewal/upgrade decision.",
        ],
        "executive_growth_os": [
            "Day 1: onboarding + connect channels.",
            "Day 7: first weekly Proof Pack.",
            "Day 14: weekly check-in + Founder Shadow Board v1.",
            "Day 21: monthly proof review.",
            "Day 30: QBR + annual upgrade conversation.",
        ],
        "partnership_growth": [
            "Day 1: partner ICP intake.",
            "Day 5: 20 partners list + 10 outreach drafts.",
            "Day 10: 5 partner meetings booked.",
            "Day 14: weekly check-in.",
            "Day 30: partner scorecard + revenue share setup.",
        ],
    }

    return {
        "customer_id": customer_id,
        "bundle_id": bundle_id,
        "cadence_ar": cadence_by_bundle.get(
            bundle_id, cadence_by_bundle["growth_starter"],
        ),
        "default_cadence_type": "weekly_check_in",
        "approval_required": True,
    }
