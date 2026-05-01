"""Tests for the Trust Plane — Policy evaluator, Approval center, Audit."""

from __future__ import annotations

from dealix.classifications import (
    ApprovalClass,
    ReversibilityClass,
    SensitivityClass,
)
from dealix.contracts.audit_log import AuditAction, AuditEntry
from dealix.contracts.decision import (
    DecisionOutput,
    Evidence,
    NextAction,
    PolicyRequirement,
)
from dealix.trust.approval import ApprovalCenter, ApprovalStatus
from dealix.trust.audit import InMemoryAuditSink
from dealix.trust.policy import PolicyDecision, PolicyEvaluator
from dealix.trust.tool_verification import ToolVerificationLedger


def _low_stakes_decision() -> DecisionOutput:
    return DecisionOutput(
        entity_id="lead_1",
        objective="qualify",
        agent_name="test",
        recommendation={},
        confidence=0.9,
        rationale="test",
        approval_class=ApprovalClass.A0,
        reversibility_class=ReversibilityClass.R0,
        sensitivity_class=SensitivityClass.S1,
    )


def _high_stakes_decision() -> DecisionOutput:
    return DecisionOutput(
        entity_id="lead_1",
        objective="send_proposal",
        agent_name="proposal",
        recommendation={},
        confidence=0.9,
        rationale="test",
        approval_class=ApprovalClass.A2,
        reversibility_class=ReversibilityClass.R2,
        sensitivity_class=SensitivityClass.S2,
        evidence=[Evidence(source="test", excerpt="e")],
    )


# ═══════════════════════════════════════════════════════════════
# PolicyEvaluator
# ═══════════════════════════════════════════════════════════════
class TestPolicyEvaluator:
    def test_allow_low_stakes_a0(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="icp_match",
            description="score lead",
            approval_class=ApprovalClass.A0,
            reversibility_class=ReversibilityClass.R0,
            sensitivity_class=SensitivityClass.S1,
        )
        result = evaluator.evaluate(action, _low_stakes_decision())
        assert result.decision == PolicyDecision.ALLOW
        assert result.rule_name == "default_allow"

    def test_never_auto_execute_escalates(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="pricing_offer_commit",
            description="commit pricing",
            approval_class=ApprovalClass.A0,  # even A0 is not enough
            reversibility_class=ReversibilityClass.R0,
            sensitivity_class=SensitivityClass.S1,
        )
        result = evaluator.evaluate(action, _high_stakes_decision())
        assert result.decision == PolicyDecision.ESCALATE
        assert result.rule_name == "never_auto_execute"
        assert result.required_approvers >= 2

    def test_r3_always_escalates(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="some_irreversible_action",
            description="irreversible",
            approval_class=ApprovalClass.A0,
            reversibility_class=ReversibilityClass.R3,
            sensitivity_class=SensitivityClass.S1,
        )
        result = evaluator.evaluate(action, _high_stakes_decision())
        assert result.decision == PolicyDecision.ESCALATE
        assert result.rule_name == "r3_blocks_auto"

    def test_a2_without_evidence_denied(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="proposal_send",
            description="send proposal",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        # Create a decision without evidence — using A0 decision hull so
        # the pydantic validator doesn't block us (we're testing the policy layer)
        decision = _low_stakes_decision()
        result = evaluator.evaluate(action, decision)
        assert result.decision == PolicyDecision.DENY
        assert result.rule_name == "a2_plus_requires_evidence"

    def test_s3_requires_pdpl_check(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="sensitive_data_action",
            description="touch personal data",
            approval_class=ApprovalClass.A1,
            reversibility_class=ReversibilityClass.R1,
            sensitivity_class=SensitivityClass.S3,
            policy_requirements=[],  # no PDPL check present
        )
        result = evaluator.evaluate(action, _high_stakes_decision())
        # Reaches NEVER_AUTO list first if `sensitive_data_action` were there,
        # otherwise cascades through rules
        assert result.decision in (PolicyDecision.ESCALATE, PolicyDecision.DENY)

    def test_s3_with_pdpl_check_still_escalates_on_approval(self):
        evaluator = PolicyEvaluator()
        action = NextAction(
            action_type="crm_contact_upsert",
            description="upsert contact",
            approval_class=ApprovalClass.A1,
            reversibility_class=ReversibilityClass.R1,
            sensitivity_class=SensitivityClass.S3,
            policy_requirements=[
                PolicyRequirement(
                    policy_name="pdpl_lawful_basis",
                    description="lawful basis checked",
                ),
            ],
        )
        # With PDPL check present, S3 rule doesn't escalate; but A1 still does
        result = evaluator.evaluate(action, _high_stakes_decision())
        assert result.decision == PolicyDecision.ESCALATE
        assert result.rule_name in ("approval_class_routing", "low_confidence_high_stakes")

    def test_low_confidence_high_stakes_escalates(self):
        evaluator = PolicyEvaluator()
        low_conf = DecisionOutput(
            entity_id="x",
            objective="send",
            agent_name="test",
            recommendation={},
            confidence=0.3,
            rationale="unsure",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
            evidence=[Evidence(source="s", excerpt="e")],
        )
        action = NextAction(
            action_type="crm_deal_create",
            description="create deal",
            approval_class=ApprovalClass.A1,
            reversibility_class=ReversibilityClass.R1,
            sensitivity_class=SensitivityClass.S2,
        )
        result = evaluator.evaluate(action, low_conf)
        # low_confidence rule precedes approval_class_routing
        assert result.decision == PolicyDecision.ESCALATE
        assert result.rule_name in ("low_confidence_high_stakes", "approval_class_routing")

    def test_evaluate_all_returns_one_per_action(self):
        evaluator = PolicyEvaluator()
        decision = _high_stakes_decision()
        decision.next_actions = [
            NextAction(
                action_type="icp_match",
                description="a",
                approval_class=ApprovalClass.A0,
                reversibility_class=ReversibilityClass.R0,
                sensitivity_class=SensitivityClass.S1,
            ),
            NextAction(
                action_type="proposal_send",
                description="b",
                approval_class=ApprovalClass.A2,
                reversibility_class=ReversibilityClass.R2,
                sensitivity_class=SensitivityClass.S2,
            ),
        ]
        results = evaluator.evaluate_all(decision)
        assert len(results) == 2
        assert results[0][1].decision == PolicyDecision.ALLOW
        assert results[1][1].decision == PolicyDecision.ESCALATE


# ═══════════════════════════════════════════════════════════════
# ApprovalCenter
# ═══════════════════════════════════════════════════════════════
class TestApprovalCenter:
    def test_submit_creates_pending_request(self):
        center = ApprovalCenter()
        decision = _high_stakes_decision()
        action = decision.next_actions
        action = NextAction(
            action_type="proposal_send",
            description="send",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        req = center.submit(decision, action, required_approvers=2)
        assert req.status == ApprovalStatus.PENDING
        assert req.approvers_needed == 2
        assert req.expires_at is not None

    def test_grant_decrements_counter(self):
        center = ApprovalCenter()
        decision = _high_stakes_decision()
        action = NextAction(
            action_type="proposal_send",
            description="send",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        req = center.submit(decision, action, required_approvers=2)
        center.grant(req.request_id, "approver_1")
        assert req.approvers_needed == 1
        assert req.status == ApprovalStatus.PENDING
        center.grant(req.request_id, "approver_2")
        assert req.approvers_needed == 0
        assert req.status == ApprovalStatus.GRANTED

    def test_grant_same_approver_twice_is_noop(self):
        center = ApprovalCenter()
        decision = _high_stakes_decision()
        action = NextAction(
            action_type="proposal_send",
            description="send",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        req = center.submit(decision, action, required_approvers=2)
        center.grant(req.request_id, "approver_1")
        center.grant(req.request_id, "approver_1")
        assert req.approvers_needed == 1

    def test_reject_flips_status(self):
        center = ApprovalCenter()
        decision = _high_stakes_decision()
        action = NextAction(
            action_type="proposal_send",
            description="send",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        req = center.submit(decision, action, required_approvers=1)
        center.reject(req.request_id, "mgr_1", reason="not a fit")
        assert req.status == ApprovalStatus.REJECTED
        assert req.rejected_by == "mgr_1"

    def test_list_pending(self):
        center = ApprovalCenter()
        decision = _high_stakes_decision()
        action = NextAction(
            action_type="proposal_send",
            description="send",
            approval_class=ApprovalClass.A2,
            reversibility_class=ReversibilityClass.R2,
            sensitivity_class=SensitivityClass.S2,
        )
        center.submit(decision, action, required_approvers=1)
        pending = center.list_pending()
        assert len(pending) == 1
        assert pending[0].entity_id == decision.entity_id


# ═══════════════════════════════════════════════════════════════
# Audit sink
# ═══════════════════════════════════════════════════════════════
class TestAuditSink:
    def test_append_and_recent(self):
        sink = InMemoryAuditSink()
        for i in range(5):
            sink.append(AuditEntry(action=AuditAction.DECISION_EMITTED, decision_id=f"d_{i}"))
        recent = sink.recent(limit=3)
        assert len(recent) == 3
        assert recent[-1].decision_id == "d_4"

    def test_filter(self):
        sink = InMemoryAuditSink()
        sink.append(AuditEntry(action=AuditAction.DECISION_EMITTED, entity_id="e_1"))
        sink.append(AuditEntry(action=AuditAction.POLICY_ALLOWED, entity_id="e_2"))
        sink.append(AuditEntry(action=AuditAction.POLICY_ESCALATED, entity_id="e_1"))

        entries_for_e1 = sink.filter(entity_id="e_1")
        assert len(entries_for_e1) == 2


# ═══════════════════════════════════════════════════════════════
# Tool verification
# ═══════════════════════════════════════════════════════════════
class TestToolVerification:
    def test_verified_when_matches(self):
        ledger = ToolVerificationLedger()
        inv = ledger.record(
            tool_name="hubspot.get_contact",
            agent_name="crm",
            intended_action="read contact 123",
            actual_action="read contact 123",
        )
        assert inv.verification_status == "verified"
        assert not inv.contradiction_flag
        assert len(ledger.contradictions()) == 0

    def test_contradicted_when_mismatches(self):
        ledger = ToolVerificationLedger()
        ledger.record(
            tool_name="hubspot.update_contact",
            agent_name="crm",
            intended_action="update contact 123",
            actual_action="update contact 456",  # wrong one!
        )
        assert len(ledger.contradictions()) == 1

    def test_for_decision_filters(self):
        ledger = ToolVerificationLedger()
        ledger.record(
            tool_name="t1",
            agent_name="a",
            intended_action="x",
            actual_action="x",
            decision_id="dec_A",
        )
        ledger.record(
            tool_name="t2",
            agent_name="a",
            intended_action="y",
            actual_action="y",
            decision_id="dec_B",
        )
        assert len(ledger.for_decision("dec_A")) == 1
