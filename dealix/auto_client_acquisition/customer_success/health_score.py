"""
Customer Health Score + Churn Risk Predictor.

Scores each customer 0-100 based on 4 dimensions:
    - Engagement   (logins, drafts approved, replies acted on)
    - Outcomes     (demos booked, deals stage progression, paid customers)
    - Adoption     (channels enabled, integrations connected)
    - Sentiment    (NPS, support tickets, churn signals)

Churn risk buckets:
    healthy   (>= 75)  → upsell candidate
    stable    (60-74)  → maintain
    at_risk   (40-59)  → CSM outreach
    critical  (< 40)   → immediate intervention

Pure-function — no DB / FastAPI deps. Testable in unit tests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class HealthScore:
    customer_id: str
    overall: float                # 0-100
    engagement: float             # 0-100
    outcomes: float               # 0-100
    adoption: float               # 0-100
    sentiment: float              # 0-100
    bucket: str                   # healthy/stable/at_risk/critical
    churn_risk_pct: float         # 0-100
    drivers: list[str]            # top 3 reasons for the score
    recommended_action: str       # next CSM action
    upsell_candidate: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_engagement(
    *, logins_last_30d: int = 0, drafts_approved_last_30d: int = 0,
    replies_acted_on_last_30d: int = 0,
) -> float:
    """0-100 score from engagement signals."""
    score = 0.0
    # Logins: 1 per workday is healthy → 22 logins in 30d → 30 points
    score += min(30, logins_last_30d * 1.4)
    # Drafts approved: 50/month target → 30 points if hit
    score += min(40, drafts_approved_last_30d * 0.8)
    # Replies acted on: 10/month is healthy → 30 points
    score += min(30, replies_acted_on_last_30d * 3)
    return min(100.0, score)


def compute_outcomes(
    *, demos_booked_last_30d: int = 0, deals_stage_progressed_last_30d: int = 0,
    paid_customers_last_30d: int = 0, pipeline_value_sar: float = 0,
) -> float:
    """0-100 score from outcomes (the 'value delivered' axis)."""
    score = 0.0
    # Demos: 5/month is healthy → 30 points
    score += min(30, demos_booked_last_30d * 6)
    # Stage progression: 10 deals moved → 30 points
    score += min(30, deals_stage_progressed_last_30d * 3)
    # Paid customers from Dealix-sourced leads: 1+ → 25 points
    score += min(25, paid_customers_last_30d * 25)
    # Pipeline value: 100K SAR → 15 points
    score += min(15, pipeline_value_sar / 7000)
    return min(100.0, score)


def compute_adoption(
    *, channels_enabled: int = 0, integrations_connected: int = 0,
    sectors_targeted: int = 0, total_drafts_lifetime: int = 0,
) -> float:
    """0-100 score from product adoption breadth."""
    score = 0.0
    # Channels: 4 = perfect (Gmail+LinkedIn+Phone+Partner)
    score += min(30, channels_enabled * 7.5)
    # Integrations: 2+ = great
    score += min(25, integrations_connected * 12.5)
    # Sectors: 2-3 active is healthy
    score += min(20, sectors_targeted * 7)
    # Lifetime drafts: 100+ = mature usage
    score += min(25, total_drafts_lifetime / 4)
    return min(100.0, score)


def compute_sentiment(
    *, nps: int | None = None, support_tickets_open: int = 0,
    days_since_last_login: int = 0, billing_failures: int = 0,
) -> float:
    """0-100 score from sentiment / risk signals."""
    score = 70.0  # neutral baseline
    if nps is not None:
        # NPS scale: -100 to +100 → map to ±30
        score += (nps / 100) * 30
    # Support tickets: every open ticket reduces 8 points
    score -= min(40, support_tickets_open * 8)
    # Login recency: > 14 days idle = -20
    if days_since_last_login >= 14:
        score -= 20
    elif days_since_last_login >= 7:
        score -= 8
    # Billing failures = -15 each
    score -= min(30, billing_failures * 15)
    return max(0.0, min(100.0, score))


def compute_health(
    customer_id: str,
    *,
    # Engagement signals
    logins_last_30d: int = 0,
    drafts_approved_last_30d: int = 0,
    replies_acted_on_last_30d: int = 0,
    # Outcomes
    demos_booked_last_30d: int = 0,
    deals_stage_progressed_last_30d: int = 0,
    paid_customers_last_30d: int = 0,
    pipeline_value_sar: float = 0,
    # Adoption
    channels_enabled: int = 0,
    integrations_connected: int = 0,
    sectors_targeted: int = 0,
    total_drafts_lifetime: int = 0,
    # Sentiment
    nps: int | None = None,
    support_tickets_open: int = 0,
    days_since_last_login: int = 0,
    billing_failures: int = 0,
) -> HealthScore:
    """
    Composite health score with weights:
        Engagement 25%, Outcomes 35%, Adoption 20%, Sentiment 20%.
    """
    engagement = compute_engagement(
        logins_last_30d=logins_last_30d,
        drafts_approved_last_30d=drafts_approved_last_30d,
        replies_acted_on_last_30d=replies_acted_on_last_30d,
    )
    outcomes = compute_outcomes(
        demos_booked_last_30d=demos_booked_last_30d,
        deals_stage_progressed_last_30d=deals_stage_progressed_last_30d,
        paid_customers_last_30d=paid_customers_last_30d,
        pipeline_value_sar=pipeline_value_sar,
    )
    adoption = compute_adoption(
        channels_enabled=channels_enabled,
        integrations_connected=integrations_connected,
        sectors_targeted=sectors_targeted,
        total_drafts_lifetime=total_drafts_lifetime,
    )
    sentiment = compute_sentiment(
        nps=nps, support_tickets_open=support_tickets_open,
        days_since_last_login=days_since_last_login,
        billing_failures=billing_failures,
    )

    overall = round(
        engagement * 0.25 + outcomes * 0.35
        + adoption * 0.20 + sentiment * 0.20, 1,
    )

    if overall >= 75:
        bucket = "healthy"; churn_risk = max(2.0, 100 - overall)
    elif overall >= 60:
        bucket = "stable"; churn_risk = 100 - overall
    elif overall >= 40:
        bucket = "at_risk"; churn_risk = 100 - overall + 10
    else:
        bucket = "critical"; churn_risk = min(95, 100 - overall + 25)

    # Top 3 drivers — what's hurting/helping most
    dim_scores = [
        ("engagement", engagement), ("outcomes", outcomes),
        ("adoption", adoption), ("sentiment", sentiment),
    ]
    sorted_dim = sorted(dim_scores, key=lambda x: x[1])
    drivers = []
    if sorted_dim[0][1] < 50:
        drivers.append(f"weak_{sorted_dim[0][0]}:{sorted_dim[0][1]:.0f}")
    if sorted_dim[1][1] < 50:
        drivers.append(f"weak_{sorted_dim[1][0]}:{sorted_dim[1][1]:.0f}")
    if days_since_last_login >= 7:
        drivers.append(f"idle_{days_since_last_login}d")
    if support_tickets_open > 0:
        drivers.append(f"open_tickets:{support_tickets_open}")
    if not drivers and overall >= 75:
        drivers.append("all_dimensions_healthy")

    # Action recommendation
    if bucket == "critical":
        action = "csm_immediate_outreach_within_24h"
    elif bucket == "at_risk":
        action = "csm_check_in_within_3_days"
    elif bucket == "stable":
        if outcomes < 50:
            action = "share_best_practices_for_outcomes"
        else:
            action = "maintain_quarterly_check_in"
    else:  # healthy
        action = "upsell_review_or_referral_ask"

    upsell_candidate = (
        bucket == "healthy" and outcomes >= 70 and adoption >= 60
    )

    return HealthScore(
        customer_id=customer_id,
        overall=overall,
        engagement=round(engagement, 1),
        outcomes=round(outcomes, 1),
        adoption=round(adoption, 1),
        sentiment=round(sentiment, 1),
        bucket=bucket,
        churn_risk_pct=round(churn_risk, 1),
        drivers=drivers[:3],
        recommended_action=action,
        upsell_candidate=upsell_candidate,
    )
