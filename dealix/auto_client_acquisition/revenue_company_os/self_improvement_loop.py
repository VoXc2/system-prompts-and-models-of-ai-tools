"""Self-improvement loop — weekly review across services + recommendations."""

from __future__ import annotations

from typing import Any


def build_weekly_self_improvement_report(
    *,
    weekly_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the weekly Arabic self-improvement report.

    Inputs:
        weekly_metrics = {
            "approval_rate": 0.42,
            "reply_rate": 0.05,
            "meeting_rate": 0.02,
            "blocked_actions": 8,
            "service_revenue_sar": {"first_10_opportunities_sprint": 1500, ...},
            "top_objections": ["price", "timing"],
            "channel_outcomes": {"email": "healthy", "whatsapp": "watch", ...},
        }
    """
    m = weekly_metrics or {}
    approval_rate = float(m.get("approval_rate", 0))
    reply_rate = float(m.get("reply_rate", 0))
    meeting_rate = float(m.get("meeting_rate", 0))
    blocked_actions = int(m.get("blocked_actions", 0))
    service_revenue = m.get("service_revenue_sar", {}) or {}
    top_objections = m.get("top_objections", []) or []
    channel_outcomes = m.get("channel_outcomes", {}) or {}

    recommendations: list[str] = []

    if approval_rate < 0.30:
        recommendations.append(
            "approval_rate منخفضة — راجع Saudi Tone + قلل الـ length في الـ drafts."
        )
    elif approval_rate < 0.50:
        recommendations.append(
            "approval_rate متوسطة — جرّب 3 صياغات مختلفة لكل رسالة."
        )

    if reply_rate < 0.03:
        recommendations.append(
            "reply_rate منخفضة — جرّب why-now أوضح + نقاط شراء أحدث."
        )

    if meeting_rate < 0.01:
        recommendations.append(
            "meeting_rate منخفضة — ضع CTA حجز اجتماع أسهل في الرسالة."
        )

    if blocked_actions >= 10:
        recommendations.append(
            f"تم منع {blocked_actions} فعل — راجع contactability + opt-in policies."
        )

    # Best-performing service
    best_service = None
    if service_revenue:
        best_service = max(service_revenue, key=lambda k: service_revenue[k])
        recommendations.append(
            f"الخدمة الأكثر إيراداً: {best_service} — ضاعف الإعلان عنها هذا الأسبوع."
        )

    # Channel risks
    risky_channels = [
        ch for ch, v in channel_outcomes.items() if v == "pause"
    ]
    if risky_channels:
        recommendations.append(
            f"قنوات في حالة pause: {', '.join(risky_channels)} — أوقف الحملات حتى تستعيد السمعة."
        )

    next_experiment = (
        f"اختبر زاوية رسالة جديدة لقطاع 'training' لمدة 7 أيام."
        if not recommendations else
        "ابدأ بأعلى توصية في القائمة قبل أي تجربة جديدة."
    )

    return {
        "captured_metrics": dict(m),
        "summary_ar": [
            f"approval_rate: {approval_rate * 100:.1f}%",
            f"reply_rate: {reply_rate * 100:.1f}%",
            f"meeting_rate: {meeting_rate * 100:.1f}%",
            f"actions blocked: {blocked_actions}",
            f"top objections: {', '.join(top_objections) or 'لا شيء بارز'}",
        ],
        "recommendations_ar": recommendations,
        "next_experiment_ar": next_experiment,
        "best_service_id": best_service,
        "approval_required": True,
    }
