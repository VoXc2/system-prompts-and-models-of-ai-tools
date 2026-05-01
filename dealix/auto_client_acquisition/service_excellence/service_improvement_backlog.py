"""Improvement backlog — يحوّل الفيدباك إلى bands prioritized."""

from __future__ import annotations

from typing import Any


def build_backlog(service_id: str) -> dict[str, Any]:
    """Build an empty backlog skeleton for a service."""
    return {
        "service_id": service_id,
        "items": [],
        "policies_ar": [
            "كل بند يتضمن: title_ar, impact, effort, owner.",
            "بند بدون proof_metric يُرفض.",
            "بند يخالف PDPL/ToS يُرفض فوراً.",
        ],
    }


def prioritize_backlog_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort backlog items by impact desc, effort asc."""
    impact_rank = {"high": 0, "medium": 1, "low": 2}
    effort_rank = {"low": 0, "medium": 1, "high": 2}
    return sorted(
        items,
        key=lambda i: (
            impact_rank.get(str(i.get("impact", "low")), 9),
            effort_rank.get(str(i.get("effort", "high")), 9),
        ),
    )


def convert_feedback_to_backlog(
    feedback: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert customer feedback items into prioritized backlog items."""
    out: list[dict[str, Any]] = []
    for f in feedback or []:
        text = str(f.get("text", "")).strip()
        if not text:
            continue
        # Heuristic prioritization (deterministic).
        sentiment = f.get("sentiment", "neutral")
        impact = "high" if sentiment == "negative" else "medium"
        effort = "medium"
        out.append({
            "title_ar": text[:120],
            "impact": impact,
            "effort": effort,
            "source": f.get("source", "feedback"),
            "owner": f.get("owner", "service_lead"),
        })
    return prioritize_backlog_items(out)


def recommend_weekly_improvements(service_id: str) -> dict[str, Any]:
    """Recommend 3 weekly improvements for a service."""
    return {
        "service_id": service_id,
        "weekly_plan_ar": [
            "حسّن الرسالة الأولى — اختبر زاوية جديدة لقطاع واحد.",
            "أضف proof_metric حقيقي لو يوجد فجوة.",
            "نظّف backlog: ادمج أو احذف بنود متشابهة.",
        ],
        "approval_required": True,
    }
