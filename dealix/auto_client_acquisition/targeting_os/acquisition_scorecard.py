"""Acquisition scorecard — يقيس النتائج بشكل deterministic."""

from __future__ import annotations

from typing import Any


def calculate_pipeline_created(opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum expected_value_sar across opportunities."""
    total = sum(float(o.get("expected_value_sar", 0)) for o in opportunities or [])
    return {
        "opportunities_count": len(opportunities or []),
        "pipeline_sar": round(total, 2),
    }


def calculate_meetings_booked(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Count meetings by status."""
    drafted = sum(1 for e in events or [] if e.get("status") == "drafted")
    confirmed = sum(1 for e in events or [] if e.get("status") == "confirmed")
    completed = sum(1 for e in events or [] if e.get("status") == "completed")
    return {
        "drafted": drafted, "confirmed": confirmed, "completed": completed,
        "total": drafted + confirmed + completed,
    }


def calculate_risks_blocked(actions: list[dict[str, Any]]) -> dict[str, Any]:
    """Count actions that were blocked by policy/contactability."""
    blocked = [a for a in actions or [] if a.get("status") == "blocked"]
    by_reason: dict[str, int] = {}
    for a in blocked:
        reason = a.get("block_reason", "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {"total": len(blocked), "by_reason": by_reason}


def calculate_productivity_score(metrics: dict[str, Any]) -> dict[str, Any]:
    """Compute a productivity score 0..100 from key acquisition metrics."""
    accounts = int(metrics.get("accounts_researched", 0))
    drafts = int(metrics.get("drafts_created", 0))
    approvals = int(metrics.get("approvals_received", 0))
    replies = int(metrics.get("positive_replies", 0))
    meetings = int(metrics.get("meetings_booked", 0))

    score = 0
    score += min(20, accounts // 3)
    score += min(20, drafts * 2)
    score += min(20, approvals * 4)
    score += min(20, replies * 5)
    score += min(20, meetings * 8)
    score = max(0, min(100, score))

    if score >= 70:
        verdict = "strong"
    elif score >= 40:
        verdict = "decent"
    else:
        verdict = "needs_focus"

    return {"score": score, "verdict": verdict}


def build_acquisition_scorecard(metrics: dict[str, Any]) -> dict[str, Any]:
    """Build a comprehensive Arabic acquisition scorecard."""
    pipeline = calculate_pipeline_created(metrics.get("opportunities", []))
    meetings = calculate_meetings_booked(metrics.get("events", []))
    risks = calculate_risks_blocked(metrics.get("actions", []))
    productivity = calculate_productivity_score(metrics)

    return {
        "summary_ar": [
            f"الحسابات المُحلّلة: {metrics.get('accounts_researched', 0)}",
            f"أصحاب القرار المُعرَّفين: {metrics.get('decision_makers_mapped', 0)}",
            f"رسائل drafts: {metrics.get('drafts_created', 0)}",
            f"اعتمادات: {metrics.get('approvals_received', 0)}",
            f"ردود إيجابية: {metrics.get('positive_replies', 0)}",
            f"اجتماعات: {meetings['total']}",
            f"Pipeline متأثر: {pipeline['pipeline_sar']:.0f} ريال",
            f"مخاطر تم منعها: {risks['total']}",
        ],
        "pipeline": pipeline,
        "meetings": meetings,
        "risks_blocked": risks,
        "productivity_score": productivity,
    }
