"""Self-Growth Mode — Dealix uses its own OS to grow.

Re-exports + extends targeting_os.self_growth_mode with operator-tier wiring.
"""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.self_growth_mode import (
    DEALIX_ICP_FOCUSES,
    build_dealix_self_growth_plan,
    build_free_service_offer,
    build_self_growth_daily_brief,
    build_weekly_learning_report,
    recommend_dealix_targets,
)


def build_operator_self_growth_brief(
    *,
    include_outreach_hint: bool = True,
) -> dict[str, Any]:
    """
    Operator-tier wrapper around the self-growth daily brief.

    Layers in approval-first reminders + reminders to never auto-send.
    """
    base = build_self_growth_daily_brief()
    out = dict(base)
    out["operator_reminders_ar"] = [
        "لا cold WhatsApp — حتى داخل Dealix نفسه.",
        "كل رسالة draft تحتاج اعتمادك قبل الإرسال.",
        "لا scraping LinkedIn — استخدم Lead Forms أو manual research.",
        "كل تواصل يدخل Action Ledger.",
    ]
    if include_outreach_hint:
        out["next_action_ar"] = (
            "اعتمد 3 رسائل اليوم فقط — جودة قبل كمية. "
            "Pilot صغير ناجح > 50 رسالة بدون رد."
        )
    out["approval_required"] = True
    out["live_send_allowed"] = False
    return out


__all__ = [
    "DEALIX_ICP_FOCUSES",
    "build_dealix_self_growth_plan",
    "build_free_service_offer",
    "build_operator_self_growth_brief",
    "build_self_growth_daily_brief",
    "build_weekly_learning_report",
    "recommend_dealix_targets",
]
