"""Tests for Dealix contracts — DecisionOutput, classifications, validators."""

from __future__ import annotations

import pytest

from dealix.classifications import (
    NEVER_AUTO_EXECUTE,
    ApprovalClass,
    ReversibilityClass,
    SensitivityClass,
    classify,
)
from dealix.contracts.audit_log import AuditAction, AuditEntry
from dealix.contracts.decision import (
    DecisionOutput,
    Evidence,
    NextAction,
)
from dealix.contracts.event_envelope import EventEnvelope


# ── Classifications ────────────────────────────────────────────
def test_classify_known_action():
    a, r, s = classify("proposal_send")
    assert a == ApprovalClass.A2
    assert r == ReversibilityClass.R2
    assert s == SensitivityClass.S2


def test_classify_unknown_defaults_conservative():
    a, r, s = classify("some_brand_new_action_xyz")
    # Conservative default
    assert a == ApprovalClass.A2
    assert r == ReversibilityClass.R2
    assert s == SensitivityClass.S2


def test_never_auto_execute_includes_expected_actions():
    for critical in (
        "pricing_offer_commit",
        "contract_change",
        "nda_send",
        "payment_terms_change",
        "regulator_communication",
        "sensitive_data_export",
    ):
        assert critical in NEVER_AUTO_EXECUTE


def test_approval_class_properties():
    assert not ApprovalClass.A0.requires_approval
    assert ApprovalClass.A1.requires_approval
    assert ApprovalClass.A3.minimum_approvers == 2


def test_reversibility_class_r3_blocks():
    assert ReversibilityClass.R3.blocks_auto_execution
    assert not ReversibilityClass.R0.blocks_auto_execution


def test_sensitivity_s3_is_pdpl():
    assert SensitivityClass.S3.is_pdpl_scope
    assert not SensitivityClass.S1.is_pdpl_scope


# ── DecisionOutput validation ──────────────────────────────────
def test_decision_low_stakes_works_without_evidence():
    d = DecisionOutput(
        entity_id="lead_1",
        objective="qualify_lead",
        agent_name="icp_matcher",
        recommendation={"tier": "A"},
        confidence=0.9,
        rationale="test",
        approval_class=ApprovalClass.A0,
        reversibility_class=ReversibilityClass.R0,
        sensitivity_class=SensitivityClass.S1,
    )
    assert not d.is_high_stakes
    assert not d.requires_human_approval


def test_decision_high_stakes_requires_evidence():
    with pytest.raises(ValueError, match="Evidence"):
        DecisionOutput(
            entity_id="lead_1",
            objective="recommend_proposal",
            agent_name="proposal",
            recommendation={"send": True},
            confidence=0.9,
            rationale="test",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
            evidence=[],  # missing!
        )


def test_decision_high_stakes_with_evidence_ok():
    d = DecisionOutput(
        entity_id="lead_1",
        objective="recommend_proposal",
        agent_name="proposal",
        recommendation={"send": True},
        confidence=0.9,
        rationale="test",
        approval_class=ApprovalClass.A2,
        reversibility_class=ReversibilityClass.R2,
        sensitivity_class=SensitivityClass.S2,
        evidence=[Evidence(source="test", excerpt="evidence here")],
    )
    assert d.is_high_stakes
    assert d.requires_human_approval


def test_decision_r3_is_high_stakes_even_with_a0():
    # R3 alone is enough to be high-stakes
    with pytest.raises(ValueError, match="Evidence"):
        DecisionOutput(
            entity_id="deal_1",
            objective="irreversible_commit",
            agent_name="test",
            recommendation={"commit": True},
            confidence=0.9,
            rationale="test",
            approval_class=ApprovalClass.A0,
            reversibility_class=ReversibilityClass.R3,
            sensitivity_class=SensitivityClass.S1,
            evidence=[],
        )


def test_decision_has_auto_generated_ids():
    d = DecisionOutput(
        entity_id="x",
        objective="test",
        agent_name="test",
        recommendation={},
        confidence=0.5,
        rationale="r",
        approval_class=ApprovalClass.A0,
        reversibility_class=ReversibilityClass.R0,
        sensitivity_class=SensitivityClass.S0,
    )
    assert d.decision_id.startswith("dec_")
    assert d.schema_version == "1.0"
    assert d.created_at  # ISO string


# ── NextAction ─────────────────────────────────────────────────
def test_next_action_fields():
    na = NextAction(
        action_type="proposal_send",
        description="send proposal",
        approval_class=ApprovalClass.A2,
        reversibility_class=ReversibilityClass.R2,
        sensitivity_class=SensitivityClass.S2,
        payload={"proposal_id": "p1"},
    )
    assert na.action_type == "proposal_send"
    assert na.payload["proposal_id"] == "p1"


# ── EventEnvelope ──────────────────────────────────────────────
def test_event_envelope_cloudevents_required():
    ev = EventEnvelope(
        source="dealix/test",
        type="dealix.test.emitted",
    )
    assert ev.specversion == "1.0"
    assert ev.id.startswith("evt_")
    assert ev.time  # ISO string


def test_event_envelope_carries_classification():
    ev = EventEnvelope(
        source="dealix/phase8",
        type="dealix.lead.intaken",
        approval_class=ApprovalClass.A0,
        reversibility_class=ReversibilityClass.R0,
        sensitivity_class=SensitivityClass.S2,
    )
    assert ev.sensitivity_class == SensitivityClass.S2


# ── AuditEntry ─────────────────────────────────────────────────
def test_audit_entry_minimal():
    entry = AuditEntry(action=AuditAction.DECISION_EMITTED)
    assert entry.audit_id.startswith("aud_")
    assert entry.outcome == "ok"
    assert entry.schema_version == "1.0"


def test_audit_action_enum_values():
    assert AuditAction.POLICY_ESCALATED.value == "policy.escalated"
    assert AuditAction.TOOL_CONTRADICTED.value == "tool.contradicted"
    assert AuditAction.WORKFLOW_COMPENSATED.value == "workflow.compensated"
