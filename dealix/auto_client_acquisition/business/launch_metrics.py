"""North-star and supporting metrics definitions."""

from __future__ import annotations

from typing import Any


def north_star_metrics() -> dict[str, Any]:
    return {
        "primary": "weekly_qualified_opportunities_accepted_or_drafted",
        "secondary": "meetings_booked_post_approval",
        "guardrail": "blocked_high_risk_outreach_count",
    }


def activation_metrics() -> dict[str, Any]:
    return {
        "time_to_first_brief_view_minutes": "target < 15",
        "time_to_first_opportunity_review": "target < 1 day",
        "first_approved_draft_hours": "target < 72h from signup",
    }


def retention_metrics() -> dict[str, Any]:
    return {
        "weekly_active_brief": "WAU brief opens",
        "proof_pack_open_rate": "target > 60%",
        "expansion_trigger": "multi-seat or performance addon attach",
    }


def revenue_metrics() -> dict[str, Any]:
    return {
        "mrr": "subscriptions + recurring performance (contracted)",
        "nrr": "expansion minus churn",
        "pipeline_influenced_sar": "attributed opportunities tracked in revenue memory",
    }


def ai_quality_metrics() -> dict[str, Any]:
    return {
        "approval_rate": "drafts approved / drafts proposed",
        "blocked_action_rate": "guardrail stops / risky attempts",
        "arabic_tone_checks": "sampled human review weekly",
        "hallucination_checks": "grounding to project chunks + radar evidence",
    }
