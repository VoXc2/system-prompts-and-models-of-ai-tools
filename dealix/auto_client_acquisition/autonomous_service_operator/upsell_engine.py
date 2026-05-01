"""Upsell engine — recommend the next service after current one delivers."""

from __future__ import annotations

from typing import Any

# Mapping: completed_service → next_recommended_service.
_UPSELL_MAP: dict[str, str] = {
    "free_growth_diagnostic": "first_10_opportunities_sprint",
    "list_intelligence": "growth_os_monthly",
    "first_10_opportunities_sprint": "growth_os_monthly",
    "self_growth_operator": "growth_os_monthly",
    "email_revenue_rescue": "growth_os_monthly",
    "meeting_booking_sprint": "growth_os_monthly",
    "partner_sprint": "agency_partner_program",
    "agency_partner_program": "growth_os_monthly",
    "whatsapp_compliance_setup": "growth_os_monthly",
    "linkedin_lead_gen_setup": "growth_os_monthly",
    "executive_growth_brief": "growth_os_monthly",
    "growth_os_monthly": "growth_os_monthly",  # already at top — annual upgrade
}

_UPSELL_PRICING_AR: dict[str, str] = {
    "first_10_opportunities_sprint": "499–1,500 ريال (Sprint)",
    "growth_os_monthly": "2,999 ريال شهرياً (أو سنوي بخصم 15%)",
    "agency_partner_program": "10,000–50,000 ريال (Setup) + Revenue Share",
}


def recommend_upsell_after_service(
    *,
    completed_service_id: str,
    pilot_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Recommend an upsell based on the completed service + metrics.

    Strong outcomes (csat ≥ 8 + pipeline ≥ 25K OR meetings ≥ 2) → upsell now.
    Weak outcomes (pipeline < 5K + meetings = 0) → iterate, don't upsell.
    Otherwise: gentle upsell.
    """
    next_id = _UPSELL_MAP.get(completed_service_id, "growth_os_monthly")
    metrics = pilot_metrics or {}
    pipeline_sar = float(metrics.get("pipeline_sar", 0))
    meetings = int(metrics.get("meetings", 0))
    csat = int(metrics.get("csat", 0))

    if csat >= 8 and (pipeline_sar >= 25_000 or meetings >= 2):
        verdict = "upsell_now"
        urgency_ar = (
            "النتائج قوية — اعرض الترقية اليوم مع خصم سنوي 15%."
        )
    elif pipeline_sar < 5_000 and meetings == 0:
        verdict = "iterate_first"
        urgency_ar = (
            "النتائج ضعيفة هذه الجولة. اقترح زاوية مختلفة قبل الترقية."
        )
    else:
        verdict = "gentle_upsell"
        urgency_ar = (
            "النتائج واعدة. اعرض Pilot موسّع 30 يوم قبل الاشتراك الشهري."
        )

    return {
        "completed_service_id": completed_service_id,
        "recommended_next_service_id": next_id,
        "verdict": verdict,
        "pricing_ar": _UPSELL_PRICING_AR.get(next_id, "حسب الحاجة"),
        "urgency_ar": urgency_ar,
        "approval_required": True,
    }


def build_upsell_card(
    *,
    completed_service_id: str,
    pilot_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an Arabic upsell card to deliver after Proof Pack."""
    rec = recommend_upsell_after_service(
        completed_service_id=completed_service_id,
        pilot_metrics=pilot_metrics,
    )
    return {
        "type": "upsell",
        "title_ar": f"الترقية المقترحة بعد {completed_service_id}",
        "summary_ar": rec["urgency_ar"],
        "next_service_id": rec["recommended_next_service_id"],
        "pricing_ar": rec["pricing_ar"],
        "verdict": rec["verdict"],
        "buttons_ar": ["ابدأ الترقية", "اشرح أكثر", "لاحقاً"],
        "approval_required": True,
        "live_send_allowed": False,
    }
