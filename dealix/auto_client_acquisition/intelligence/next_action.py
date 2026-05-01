"""
Next-Best-Action engine.

Takes a fully-scored account and returns:
    action: one of  call | gmail_draft | linkedin_manual | partner_intro |
                    enrich_more | block | wait_followup
    rationale: one-line explanation
    priority_bucket: P0 | P1 | P2 | P3 | BLOCKED

Formula for priority_score (0..100):
    0.30 * fit_score        (max 40 → 12 contribution)
    + 0.25 * intent_score   (max 30 → 7.5 contribution)
    + 0.20 * urgency_score  (max 30 → 6 contribution)
    + 0.15 * revenue_score  (max 15 → 2.25 contribution)
    - 0.10 * risk_score     (subtract up to 10)

Then mapped to a bucket:
    >=  60 → P0
    >=  45 → P1
    >=  30 → P2
    <   30 → P3
    risk > 50 OR opt_out → BLOCKED
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class NextAction:
    action: str
    rationale: str
    priority_bucket: str
    priority_score: float
    fit_contribution: float
    intent_contribution: float
    urgency_contribution: float
    revenue_contribution: float
    risk_penalty: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_priority(
    *,
    fit_score: float,
    intent_score: float,
    urgency_score: float,
    revenue_score: float,
    risk_score: float,
) -> float:
    """Apply the weighted formula. Clamp to [0, 100]."""
    score = (
        0.30 * fit_score
        + 0.25 * intent_score
        + 0.20 * urgency_score
        + 0.15 * revenue_score
        - 0.10 * risk_score
    )
    return max(0.0, min(100.0, round(score, 1)))


def decide(
    *,
    fit_score: float = 0,
    intent_score: float = 0,
    urgency_score: float = 0,
    revenue_score: float = 0,
    risk_score: float = 0,
    opt_out: bool = False,
    has_business_email: bool = False,
    has_phone: bool = False,
    has_linkedin_handle: bool = False,
    is_potential_partner: bool = False,
    sector: str | None = None,
    allowed_use: str | None = None,
) -> NextAction:
    """Return the recommended next-best-action for this account."""
    priority_score = compute_priority(
        fit_score=fit_score, intent_score=intent_score,
        urgency_score=urgency_score, revenue_score=revenue_score,
        risk_score=risk_score,
    )

    # Block conditions (override score)
    if opt_out:
        return NextAction(
            action="block",
            rationale="opt_out_true",
            priority_bucket="BLOCKED",
            priority_score=priority_score,
            fit_contribution=fit_score * 0.30,
            intent_contribution=intent_score * 0.25,
            urgency_contribution=urgency_score * 0.20,
            revenue_contribution=revenue_score * 0.15,
            risk_penalty=risk_score * 0.10,
        )
    if risk_score > 50:
        return NextAction(
            action="block",
            rationale=f"risk_score_too_high:{risk_score:.0f}",
            priority_bucket="BLOCKED",
            priority_score=priority_score,
            fit_contribution=fit_score * 0.30,
            intent_contribution=intent_score * 0.25,
            urgency_contribution=urgency_score * 0.20,
            revenue_contribution=revenue_score * 0.15,
            risk_penalty=risk_score * 0.10,
        )
    if not allowed_use or allowed_use in {"unknown", ""}:
        return NextAction(
            action="block",
            rationale="allowed_use_missing",
            priority_bucket="BLOCKED",
            priority_score=priority_score,
            fit_contribution=fit_score * 0.30,
            intent_contribution=intent_score * 0.25,
            urgency_contribution=urgency_score * 0.20,
            revenue_contribution=revenue_score * 0.15,
            risk_penalty=risk_score * 0.10,
        )

    # Bucket from score
    if priority_score >= 60:
        bucket = "P0"
    elif priority_score >= 45:
        bucket = "P1"
    elif priority_score >= 30:
        bucket = "P2"
    else:
        bucket = "P3"

    # Action selection
    if is_potential_partner:
        action = "partner_intro"
        rationale = "agency_or_consulting_partner_path"
    elif bucket in ("P0", "P1") and has_business_email:
        action = "gmail_draft"
        rationale = f"{bucket}_high_intent_business_email_present"
    elif bucket in ("P0", "P1") and has_phone:
        action = "call"
        rationale = f"{bucket}_high_intent_phone_only"
    elif bucket == "P2" and has_linkedin_handle:
        action = "linkedin_manual"
        rationale = "P2_with_linkedin_present"
    elif bucket == "P2" and has_business_email:
        action = "gmail_draft"
        rationale = "P2_business_email_lower_priority_drip"
    elif bucket == "P2":
        action = "call"
        rationale = "P2_phone_only"
    elif bucket == "P3":
        action = "wait_followup"
        rationale = "P3_low_priority_revisit_in_30d"
    else:
        action = "enrich_more"
        rationale = "needs_more_data_before_outreach"

    contributions = NextAction(
        action=action,
        rationale=rationale,
        priority_bucket=bucket,
        priority_score=priority_score,
        fit_contribution=round(fit_score * 0.30, 2),
        intent_contribution=round(intent_score * 0.25, 2),
        urgency_contribution=round(urgency_score * 0.20, 2),
        revenue_contribution=round(revenue_score * 0.15, 2),
        risk_penalty=round(risk_score * 0.10, 2),
    )
    return contributions
