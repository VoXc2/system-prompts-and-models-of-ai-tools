"""Mission Curator — score completed missions and pick the next one."""

from __future__ import annotations


def score_mission(mission: dict[str, object]) -> dict[str, object]:
    """
    Score a completed mission run.

    Inputs:
        opportunities_generated, drafts_approved, meetings_booked,
        revenue_influenced_sar, time_to_value_minutes, risks_blocked
    """
    opps = int(mission.get("opportunities_generated", 0) or 0)
    approved = int(mission.get("drafts_approved", 0) or 0)
    meetings = int(mission.get("meetings_booked", 0) or 0)
    revenue = float(mission.get("revenue_influenced_sar", 0) or 0)
    risks_blocked = int(mission.get("risks_blocked", 0) or 0)
    ttv = float(mission.get("time_to_value_minutes", 9_999) or 9_999)

    score = 0
    score += min(20, opps * 2)
    score += min(20, approved * 4)
    score += min(20, meetings * 5)
    score += min(20, int(revenue / 5_000))
    score += min(10, risks_blocked * 5)
    if ttv <= 10:
        score += 10
    elif ttv <= 60:
        score += 5
    score = max(0, min(100, score))

    if score >= 70:
        verdict = "ship_it_widely"
    elif score >= 40:
        verdict = "iterate"
    else:
        verdict = "rework_or_retire"

    return {"score": score, "verdict": verdict, "ttv_minutes": ttv}


def recommend_next_mission(
    mission_history: list[dict[str, object]] | None = None,
    *,
    growth_brain: dict[str, object] | None = None,
) -> dict[str, object]:
    """
    Pick the next mission to run given history and brain context.

    Defaults to the kill feature `first_10_opportunities` for early-stage
    customers (low signal count).
    """
    if not mission_history:
        return {
            "recommended_mission_id": "first_10_opportunities",
            "reason_ar": "لا يوجد تاريخ مهمات — نبدأ بالـ Kill Feature.",
        }

    # If the kill feature has not yet shipped, ship it first.
    ran_ids = {m.get("mission_id") for m in mission_history}
    if "first_10_opportunities" not in ran_ids:
        return {
            "recommended_mission_id": "first_10_opportunities",
            "reason_ar": "Kill Feature لم يُشغّل بعد — ابدأ به.",
        }

    # Otherwise, pick the next mission by sector/priority.
    priorities = []
    if growth_brain:
        priorities = list(growth_brain.get("growth_priorities", []) or [])

    if "fill_pipeline" in priorities:
        return {
            "recommended_mission_id": "meeting_booking_sprint",
            "reason_ar": "الأولوية ملء الـ pipeline — سبرنت حجز الاجتماعات.",
        }
    if "rescue_lost_revenue" in priorities:
        return {
            "recommended_mission_id": "revenue_leak_rescue",
            "reason_ar": "الأولوية استرجاع الإيراد — تشغيل ميشن التسريب.",
        }
    if "expand_partners" in priorities:
        return {
            "recommended_mission_id": "partnership_sprint",
            "reason_ar": "الأولوية توسيع الشركاء — ميشن الشراكات.",
        }

    # Default deterministic next.
    return {
        "recommended_mission_id": "customer_reactivation",
        "reason_ar": "الافتراضي: إعادة تنشيط العملاء الخاملين.",
    }
