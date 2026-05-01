"""Service scorecard — يقيس نجاح كل خدمة بعد تشغيلها."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service


def calculate_service_success_score(
    service_id: str, metrics: dict[str, Any],
) -> dict[str, Any]:
    """Score a service run 0..100 + verdict."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    score = 0

    # Generic outcomes that map to most services.
    drafts_approved = int(metrics.get("drafts_approved", 0))
    positive_replies = int(metrics.get("positive_replies", 0))
    meetings = int(metrics.get("meetings", 0))
    pipeline_sar = float(metrics.get("pipeline_sar", 0))
    risks_blocked = int(metrics.get("risks_blocked", 0))
    customer_satisfaction = int(metrics.get("customer_satisfaction", 0))  # 0..10

    score += min(15, drafts_approved * 3)
    score += min(20, positive_replies * 5)
    score += min(20, meetings * 8)
    score += min(20, int(pipeline_sar / 5_000))
    score += min(10, risks_blocked * 2)
    score += min(15, customer_satisfaction * 1)

    score = max(0, min(100, score))

    if score >= 70:
        verdict = "strong_outcome"
    elif score >= 40:
        verdict = "decent_outcome"
    else:
        verdict = "needs_iteration"

    return {
        "service_id": service_id,
        "score": score,
        "verdict": verdict,
        "captured_metrics": metrics,
    }


def recommend_next_step(metrics: dict[str, Any]) -> dict[str, Any]:
    """Recommend the next step for a customer based on outcome metrics."""
    pipeline_sar = float(metrics.get("pipeline_sar", 0))
    meetings = int(metrics.get("meetings", 0))
    csat = int(metrics.get("customer_satisfaction", 0))

    if csat >= 8 and (pipeline_sar >= 25_000 or meetings >= 2):
        return {
            "action": "upsell_to_growth_os",
            "label_ar": "اعرض Growth OS الشهري — العميل راضٍ والنتائج قوية.",
        }
    if pipeline_sar < 5_000 and meetings == 0:
        return {
            "action": "iterate_offer_or_segment",
            "label_ar": "غيّر زاوية العرض أو القطاع — النتائج ضعيفة.",
        }
    return {
        "action": "extend_pilot",
        "label_ar": "مدّد الـ Pilot لأسبوعين أو جرّب قناة إضافية.",
    }


def build_service_scorecard(
    service_id: str, metrics: dict[str, Any],
) -> dict[str, Any]:
    """Build a full Arabic scorecard for a service run."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    score_obj = calculate_service_success_score(service_id, metrics)
    next_step = recommend_next_step(metrics)
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "score": score_obj.get("score"),
        "verdict": score_obj.get("verdict"),
        "metrics": metrics,
        "next_step": next_step,
        "summary_ar": summarize_scorecard_ar({
            "service_id": service_id,
            **score_obj, "next_step": next_step,
        }),
    }


def summarize_scorecard_ar(scorecard: dict[str, Any]) -> str:
    s = get_service(scorecard.get("service_id", ""))
    name = s.name_ar if s else scorecard.get("service_id", "?")
    score = scorecard.get("score", 0)
    verdict = scorecard.get("verdict", "?")
    next_step = (scorecard.get("next_step") or {}).get("label_ar", "")
    return (
        f"{name}: درجة {score} ({verdict}). الخطوة التالية: {next_step}"
    )
