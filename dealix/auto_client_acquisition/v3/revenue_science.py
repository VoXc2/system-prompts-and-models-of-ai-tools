"""Revenue Science models for Dealix v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FunnelInputs:
    prospects: int
    reply_rate: float
    meeting_rate: float
    close_rate: float
    average_deal_value_sar: float
    monthly_cost_sar: float = 0.0


def forecast_revenue(inputs: FunnelInputs) -> dict[str, Any]:
    replies = inputs.prospects * inputs.reply_rate
    meetings = replies * inputs.meeting_rate
    wins = meetings * inputs.close_rate
    revenue = wins * inputs.average_deal_value_sar
    roi = (revenue / inputs.monthly_cost_sar) if inputs.monthly_cost_sar else None
    return {
        "prospects": inputs.prospects,
        "expected_replies": round(replies, 2),
        "expected_meetings": round(meetings, 2),
        "expected_wins": round(wins, 2),
        "expected_revenue_sar": round(revenue, 2),
        "roi_multiple": round(roi, 2) if roi is not None else None,
        "confidence": {
            "low_revenue_sar": round(revenue * 0.65, 2),
            "base_revenue_sar": round(revenue, 2),
            "high_revenue_sar": round(revenue * 1.35, 2),
        },
    }


def impact_simulation(base: FunnelInputs, improved: FunnelInputs) -> dict[str, Any]:
    base_result = forecast_revenue(base)
    improved_result = forecast_revenue(improved)
    lift = improved_result["expected_revenue_sar"] - base_result["expected_revenue_sar"]
    return {
        "base": base_result,
        "improved": improved_result,
        "incremental_revenue_sar": round(lift, 2),
        "best_action": "Improve reply quality and follow-up speed before increasing volume.",
    }


def churn_risk_score(usage_days_30: int, outcomes_seen: int, support_sentiment: float) -> dict[str, Any]:
    usage_component = max(0, 40 - usage_days_30 * 1.2)
    outcome_component = max(0, 35 - outcomes_seen * 8)
    sentiment_component = max(0, 25 - support_sentiment * 25)
    risk = round(min(100, usage_component + outcome_component + sentiment_component), 2)
    bucket = "critical" if risk >= 70 else "at_risk" if risk >= 45 else "stable" if risk >= 25 else "healthy"
    return {"risk_score": risk, "bucket": bucket, "recommended_action": "Create ROI proof pack and schedule QBR."}


def demo_forecast() -> dict[str, Any]:
    return forecast_revenue(FunnelInputs(400, 0.14, 0.32, 0.22, 18000, 2999))
