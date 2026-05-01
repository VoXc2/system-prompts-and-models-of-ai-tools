"""Service Research Lab — تحسين شهري لكل خدمة (deterministic)."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service

from .competitor_gap import compare_against_categories
from .service_scoring import calculate_service_excellence_score


def build_service_research_brief(service_id: str) -> dict[str, Any]:
    """Research brief: questions to answer about a service this month."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "questions_to_answer_ar": [
            "من أكثر فئة عميل اشترت هذه الخدمة آخر 30 يوم؟",
            "ما متوسط الـ time-to-value الفعلي؟",
            "ما أعلى اعتراض ظهر في الـonboarding؟",
            "ما أكثر deliverable يطلبه العميل بالاسم؟",
            "ما أضعف proof_metric لم يُحقَّق هذا الشهر؟",
            "ما أكثر سعر يقبله العميل بدون تردد؟",
        ],
        "data_sources_ar": [
            "Action Ledger.",
            "Proof Ledger.",
            "Approval Center.",
            "Decision Memory.",
            "Customer feedback.",
        ],
        "approval_required": True,
    }


def generate_feature_hypotheses(service_id: str) -> list[dict[str, Any]]:
    """Generate hypotheses for feature additions/improvements."""
    s = get_service(service_id)
    if s is None:
        return []
    base = [
        {
            "hypothesis_ar": "إضافة exit survey بعد كل deliverable يرفع NPS بـ20%.",
            "effort": "low", "impact": "medium",
        },
        {
            "hypothesis_ar": "اقتراح 3 رسائل بدل 1 في الـapproval card يرفع approval rate 30%.",
            "effort": "medium", "impact": "high",
        },
        {
            "hypothesis_ar": "إضافة Saudi-tone-score مرئية في الواجهة يقلل الرسائل المرفوضة 40%.",
            "effort": "medium", "impact": "high",
        },
        {
            "hypothesis_ar": "ربط Proof Pack بـ Moyasar invoice draft يرفع conversion 25%.",
            "effort": "medium", "impact": "high",
        },
    ]
    if s.pricing_model == "monthly":
        base.append({
            "hypothesis_ar": "تقرير شهري بصيغة فيديو 60 ثانية يرفع retention 15%.",
            "effort": "high", "impact": "medium",
        })
    return base


def recommend_next_experiments(service_id: str) -> dict[str, Any]:
    """Recommend the next 3 experiments to run on a service."""
    hypotheses = generate_feature_hypotheses(service_id)
    # Pick top-3 by impact desc, effort asc.
    impact_rank = {"high": 0, "medium": 1, "low": 2}
    effort_rank = {"low": 0, "medium": 1, "high": 2}
    sorted_h = sorted(
        hypotheses,
        key=lambda h: (impact_rank.get(str(h.get("impact")), 9),
                       effort_rank.get(str(h.get("effort")), 9)),
    )
    return {
        "service_id": service_id,
        "experiments": sorted_h[:3],
        "approval_required": True,
    }


def build_monthly_service_review(service_id: str) -> dict[str, Any]:
    """Build a structured monthly review of a service's performance."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    score = calculate_service_excellence_score(service_id)
    gaps = compare_against_categories(service_id)
    experiments = recommend_next_experiments(service_id)

    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "current_excellence_score": score,
        "competitor_gap_summary": {
            "advantages": gaps.get("dealix_advantages_ar", []),
            "gaps_to_close": gaps.get("gaps_to_close_ar", []),
        },
        "next_experiments": experiments.get("experiments", []),
        "research_brief": build_service_research_brief(service_id),
        "approval_required": True,
    }
