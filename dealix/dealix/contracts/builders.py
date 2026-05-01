"""
DecisionBuilder — helpers to turn existing agent outputs into DecisionOutput contracts.

This module is how Phase 8/9 agents integrate with the Dealix governance layer
WITHOUT being rewritten. Each agent's existing output is wrapped into a
DecisionOutput with the right classifications and NextActions.
"""

from __future__ import annotations

from typing import Any

from dealix.classifications import classify
from dealix.contracts.decision import (
    DecisionOutput,
    Evidence,
    NextAction,
    PolicyRequirement,
)


def _next_action_for(action_type: str, description: str, payload: dict[str, Any]) -> NextAction:
    approval, reversibility, sensitivity = classify(action_type)
    return NextAction(
        action_type=action_type,
        description=description,
        approval_class=approval,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        payload=payload,
        policy_requirements=[],
    )


def from_icp_match(
    *, lead_id: str, fit_score: Any, agent_name: str = "icp_matcher"
) -> DecisionOutput:
    """Wrap an ICPMatcher FitScore as a DecisionOutput."""
    approval, reversibility, sensitivity = classify("icp_match")

    # Build next actions based on the tier
    next_actions: list[NextAction] = []
    if fit_score.tier in ("A", "B"):
        next_actions.append(
            _next_action_for(
                "booking_schedule",
                f"Schedule discovery call — tier {fit_score.tier}",
                {"lead_id": lead_id, "tier": fit_score.tier},
            )
        )
    if fit_score.tier == "A":
        next_actions.append(
            _next_action_for(
                "crm_deal_create",
                "Create deal in CRM for tier-A lead",
                {"lead_id": lead_id},
            )
        )

    return DecisionOutput(
        entity_id=lead_id,
        objective="qualify_lead",
        agent_name=agent_name,
        recommendation={
            "overall_score": fit_score.overall_score,
            "tier": fit_score.tier,
            "reasons": fit_score.reasons,
            "recommendations": fit_score.recommendations,
            "dimensions": {
                "industry_match": fit_score.industry_match,
                "size_match": fit_score.size_match,
                "region_match": fit_score.region_match,
                "budget_match": fit_score.budget_match,
                "pain_match": fit_score.pain_match,
            },
        },
        confidence=fit_score.overall_score,
        rationale="; ".join(fit_score.reasons) or "Computed from ICP weighted score",
        evidence=[],  # ICP match is pure computation — evidence is the input fields, not external sources
        approval_class=approval,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        next_actions=next_actions,
    )


def from_pain_extraction(
    *,
    lead_id: str,
    extraction: Any,
    message: str,
    agent_name: str = "pain_extractor",
    model: str | None = None,
) -> DecisionOutput:
    """Wrap a PainExtractor ExtractionResult as a DecisionOutput."""
    approval, reversibility, sensitivity = classify("pain_extract")

    evidence_items: list[Evidence] = []
    if message:
        evidence_items.append(
            Evidence(
                source="lead.message",
                excerpt=message[:500],
                confidence=1.0,
            )
        )

    return DecisionOutput(
        entity_id=lead_id,
        objective="extract_pain_points",
        agent_name=agent_name,
        model=model,
        recommendation={
            "pain_points": [p.to_dict() for p in extraction.pain_points],
            "urgency_score": extraction.urgency_score,
            "likely_offer": extraction.likely_offer,
            "recommended_next_step": extraction.recommended_next_step,
            "key_phrases": extraction.key_phrases,
            "method": extraction.method,
        },
        confidence=0.8 if extraction.method == "hybrid" else 0.6,
        rationale=(
            f"Extracted {len(extraction.pain_points)} pain signal(s) via {extraction.method}; "
            f"urgency={extraction.urgency_score:.2f}"
        ),
        evidence=evidence_items,
        approval_class=approval,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        next_actions=[],
    )


def from_qualification(
    *,
    lead_id: str,
    qualification: Any,
    agent_name: str = "qualification",
    model: str | None = None,
) -> DecisionOutput:
    """Wrap a QualificationResult as a DecisionOutput."""
    approval, reversibility, sensitivity = classify("qualification_questions")

    next_actions: list[NextAction] = []
    if qualification.bant_score >= 0.75:
        next_actions.append(
            _next_action_for(
                "proposal_generate_draft",
                "Generate proposal draft — BANT score high",
                {"lead_id": lead_id},
            )
        )

    return DecisionOutput(
        entity_id=lead_id,
        objective="qualify_lead_bant",
        agent_name=agent_name,
        model=model,
        recommendation={
            "questions": [q.to_dict() for q in qualification.questions],
            "bant_score": qualification.bant_score,
            "new_status": qualification.new_status.value,
            "budget_clarified": qualification.budget_clarified,
            "authority_confirmed": qualification.authority_confirmed,
            "need_explicit": qualification.need_explicit,
            "timeline_known": qualification.timeline_known,
        },
        confidence=qualification.bant_score,
        rationale=(
            f"BANT coverage {qualification.bant_score:.0%}; "
            f"budget={qualification.budget_clarified}, "
            f"authority={qualification.authority_confirmed}, "
            f"need={qualification.need_explicit}, "
            f"timeline={qualification.timeline_known}"
        ),
        evidence=[],
        approval_class=approval,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        next_actions=next_actions,
    )


def from_proposal_draft(
    *,
    lead_id: str,
    proposal: Any,
    agent_name: str = "proposal",
    model: str | None = None,
) -> DecisionOutput:
    """Wrap a Proposal draft as a DecisionOutput.

    Note: this is the DRAFT action (A0/R0). The actual SEND is a separate
    NextAction that is A2/R2 and requires approval.
    """
    approval, reversibility, sensitivity = classify("proposal_generate_draft")
    send_approval, send_reversibility, send_sensitivity = classify("proposal_send")

    # Evidence: the proposal body itself is the artifact — we point to it
    evidence_items = [
        Evidence(
            source="generated.proposal.body",
            excerpt=proposal.body_markdown[:500]
            + ("…" if len(proposal.body_markdown) > 500 else ""),
            confidence=1.0,
        ),
    ]

    next_actions = [
        NextAction(
            action_type="proposal_send",
            description=f"Send proposal {proposal.id} to lead",
            approval_class=send_approval,
            reversibility_class=send_reversibility,
            sensitivity_class=send_sensitivity,
            payload={
                "proposal_id": proposal.id,
                "lead_id": lead_id,
                "budget_min": proposal.budget_min,
                "budget_max": proposal.budget_max,
                "currency": proposal.currency,
            },
            policy_requirements=[
                PolicyRequirement(
                    policy_name="manager_approval",
                    description="A proposal send must be approved by a manager or higher",
                ),
            ],
        ),
    ]

    return DecisionOutput(
        entity_id=lead_id,
        objective="recommend_proposal",
        agent_name=agent_name,
        model=model,
        recommendation={
            "proposal_id": proposal.id,
            "budget_min": proposal.budget_min,
            "budget_max": proposal.budget_max,
            "currency": proposal.currency,
            "body_preview": proposal.body_markdown[:300],
            "locale": proposal.locale,
            "valid_until": proposal.valid_until.isoformat(),
        },
        confidence=0.75,  # drafts start mid-confidence; human review raises it
        rationale=(
            f"Generated {proposal.locale} proposal {proposal.id} with pricing "
            f"{proposal.budget_min:,.0f}–{proposal.budget_max:,.0f} {proposal.currency}. "
            "Send action requires manager approval per policy."
        ),
        evidence=evidence_items,
        approval_class=approval,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        next_actions=next_actions,
        locale=proposal.locale,
    )
