"""Integration test for the GovernedPipeline (Phase 8 + Trust Plane)."""

from __future__ import annotations

import pytest

from dealix.execution import GovernedPipeline
from dealix.trust.policy import PolicyDecision


@pytest.mark.asyncio
async def test_governed_pipeline_emits_decisions(sample_lead_payload, mock_router):
    """The governed pipeline must produce DecisionOutputs from the underlying run."""
    mock_router.run.return_value.content = (
        '{"pain_points":[{"text":"slow","category":"performance","severity":0.8}],'
        '"urgency_score":0.9,"likely_offer":"X","recommended_next_step":"call","key_phrases":[]}'
    )

    governed = GovernedPipeline()
    result = await governed.run(
        payload=sample_lead_payload,
        auto_book=False,
        auto_proposal=False,
    )

    assert result.underlying.lead.id
    # At minimum we expect pain + icp + qualification decisions
    assert len(result.decisions) >= 2

    # Every decision must carry classifications
    for d in result.decisions:
        assert d.approval_class is not None
        assert d.reversibility_class is not None
        assert d.sensitivity_class is not None


@pytest.mark.asyncio
async def test_governed_pipeline_audits_every_step(sample_lead_payload, mock_router):
    mock_router.run.return_value.content = '{"ok": true}'
    governed = GovernedPipeline()
    result = await governed.run(
        payload=sample_lead_payload,
        auto_book=False,
    )
    # Every emitted decision produces an audit entry
    assert len(result.audit_trail) >= len(result.decisions)


@pytest.mark.asyncio
async def test_governed_pipeline_escalates_high_stakes_actions(sample_lead_payload, mock_router):
    """When a tier-A lead is detected and a proposal is auto-generated,
    the proposal-send NextAction should be ESCALATED (never auto-allowed)."""
    mock_router.run.return_value.content = '{"ok": true}'
    governed = GovernedPipeline()
    result = await governed.run(
        payload=sample_lead_payload,
        auto_book=False,
        auto_proposal=True,  # force proposal generation
    )

    # Find any proposal_send action in the policy results
    proposal_sends = [(d, a, r) for d, a, r in result.policy_results if a == "proposal_send"]
    # If a proposal was generated, its send action must not be ALLOW
    if proposal_sends:
        for _d, _a, r in proposal_sends:
            assert (
                r.decision != PolicyDecision.ALLOW
            ), f"proposal_send was {r.decision.value} — should be ESCALATE"


@pytest.mark.asyncio
async def test_governed_pipeline_creates_approval_requests(sample_lead_payload, mock_router):
    """Escalated actions must yield pending approval requests."""
    mock_router.run.return_value.content = '{"ok": true}'
    governed = GovernedPipeline()
    result = await governed.run(
        payload=sample_lead_payload,
        auto_book=False,
        auto_proposal=True,
    )

    # Count escalations vs approval requests — they should roughly match
    n_escalations = sum(
        1 for _, _, r in result.policy_results if r.decision == PolicyDecision.ESCALATE
    )
    assert len(result.approval_requests) == n_escalations
