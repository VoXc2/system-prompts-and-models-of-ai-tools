"""
Dealix pipeline adapter — integrates the Trust Plane with the Phase 8 pipeline.

This sits ABOVE `auto_client_acquisition.pipeline.AcquisitionPipeline` and
produces:
    * A list of DecisionOutputs (one per decision-plane agent)
    * Policy evaluations for every NextAction
    * Approval requests for escalated actions
    * Audit log entries for every step

It does NOT modify the existing pipeline — it composes with it. That means
existing callers keep working while Dealix-aware callers can opt into
governance by calling `GovernedPipeline.run()` instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.agents.intake import LeadSource
from auto_client_acquisition.pipeline import AcquisitionPipeline, PipelineResult
from dealix.contracts.audit_log import AuditAction, AuditEntry
from dealix.contracts.builders import (
    from_icp_match,
    from_pain_extraction,
    from_proposal_draft,
    from_qualification,
)
from dealix.contracts.decision import DecisionOutput
from dealix.trust.approval import ApprovalCenter, ApprovalRequest
from dealix.trust.audit import AuditSink, InMemoryAuditSink
from dealix.trust.policy import PolicyDecision, PolicyEvaluator, PolicyResult


@dataclass
class GovernedPipelineResult:
    """Full result including governance artifacts."""

    underlying: PipelineResult
    decisions: list[DecisionOutput] = field(default_factory=list)
    policy_results: list[tuple[DecisionOutput, str, PolicyResult]] = field(default_factory=list)
    approval_requests: list[ApprovalRequest] = field(default_factory=list)
    audit_trail: list[AuditEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "underlying": self.underlying.to_dict(),
            "decisions": [d.model_dump(mode="json") for d in self.decisions],
            "policy_results": [
                {
                    "decision_id": d.decision_id,
                    "action_type": action_type,
                    "decision": pr.decision.value,
                    "rule": pr.rule_name,
                    "reason": pr.reason,
                    "required_approvers": pr.required_approvers,
                }
                for d, action_type, pr in self.policy_results
            ],
            "approval_requests": [a.to_dict() for a in self.approval_requests],
            "audit_trail_count": len(self.audit_trail),
        }


class GovernedPipeline:
    """Pipeline wrapper that runs Phase 8 + the Dealix Trust Plane."""

    def __init__(
        self,
        *,
        policy_evaluator: PolicyEvaluator | None = None,
        approval_center: ApprovalCenter | None = None,
        audit_sink: AuditSink | None = None,
    ) -> None:
        self.pipeline = AcquisitionPipeline()
        self.policy = policy_evaluator or PolicyEvaluator()
        self.approvals = approval_center or ApprovalCenter()
        self.audit = audit_sink or InMemoryAuditSink()

    async def run(
        self,
        payload: dict[str, Any],
        *,
        source: LeadSource | str = LeadSource.WEBSITE,
        use_llm_pain: bool = True,
        auto_book: bool = True,
        auto_proposal: bool = False,
    ) -> GovernedPipelineResult:
        """Run the underlying pipeline, then overlay governance."""
        # Step 1 — run the existing pipeline unchanged
        underlying = await self.pipeline.run(
            payload=payload,
            source=source,
            use_llm_pain=use_llm_pain,
            auto_book=auto_book,
            auto_proposal=auto_proposal,
        )

        result = GovernedPipelineResult(underlying=underlying)
        lead_id = underlying.lead.id

        # Step 2 — lift outputs into DecisionOutput contracts
        if underlying.extraction is not None:
            decision = from_pain_extraction(
                lead_id=lead_id,
                extraction=underlying.extraction,
                message=underlying.lead.message or "",
            )
            result.decisions.append(decision)
            self._audit_decision(result, decision)

        if underlying.fit_score is not None:
            decision = from_icp_match(lead_id=lead_id, fit_score=underlying.fit_score)
            result.decisions.append(decision)
            self._audit_decision(result, decision)

        if underlying.qualification is not None:
            decision = from_qualification(lead_id=lead_id, qualification=underlying.qualification)
            result.decisions.append(decision)
            self._audit_decision(result, decision)

        if underlying.proposal is not None:
            decision = from_proposal_draft(lead_id=lead_id, proposal=underlying.proposal)
            result.decisions.append(decision)
            self._audit_decision(result, decision)

        # Step 3 — run every NextAction through the policy evaluator
        for decision in result.decisions:
            for action in decision.next_actions:
                policy_result = self.policy.evaluate(action, decision)
                result.policy_results.append((decision, action.action_type, policy_result))

                # Audit the evaluation
                result.audit_trail.append(
                    self._emit_audit(
                        action=(
                            AuditAction.POLICY_ALLOWED
                            if policy_result.decision == PolicyDecision.ALLOW
                            else (
                                AuditAction.POLICY_DENIED
                                if policy_result.decision == PolicyDecision.DENY
                                else AuditAction.POLICY_ESCALATED
                            )
                        ),
                        decision_id=decision.decision_id,
                        entity_id=decision.entity_id,
                        approval_class=action.approval_class,
                        reversibility_class=action.reversibility_class,
                        sensitivity_class=action.sensitivity_class,
                        outcome=policy_result.decision.value,
                        reason=policy_result.reason,
                        details={
                            "action_type": action.action_type,
                            "rule": policy_result.rule_name,
                        },
                    )
                )

                # Step 4 — if escalated, create an approval request
                if policy_result.decision == PolicyDecision.ESCALATE:
                    req = self.approvals.submit(
                        decision=decision,
                        action=action,
                        required_approvers=policy_result.required_approvers or 1,
                    )
                    result.approval_requests.append(req)
                    result.audit_trail.append(
                        self._emit_audit(
                            action=AuditAction.APPROVAL_REQUESTED,
                            decision_id=decision.decision_id,
                            entity_id=decision.entity_id,
                            approval_class=action.approval_class,
                            reversibility_class=action.reversibility_class,
                            sensitivity_class=action.sensitivity_class,
                            details={
                                "approval_request_id": req.request_id,
                                "action_type": action.action_type,
                                "approvers_needed": req.approvers_needed,
                            },
                        )
                    )

        return result

    # ── internal ────────────────────────────────────────────────
    def _audit_decision(self, result: GovernedPipelineResult, decision: DecisionOutput) -> None:
        entry = self._emit_audit(
            action=AuditAction.DECISION_EMITTED,
            decision_id=decision.decision_id,
            entity_id=decision.entity_id,
            approval_class=decision.approval_class,
            reversibility_class=decision.reversibility_class,
            sensitivity_class=decision.sensitivity_class,
            details={
                "objective": decision.objective,
                "agent_name": decision.agent_name,
                "confidence": decision.confidence,
                "n_next_actions": len(decision.next_actions),
            },
        )
        result.audit_trail.append(entry)

    def _emit_audit(self, **kwargs: Any) -> AuditEntry:
        entry = AuditEntry(**kwargs)
        self.audit.append(entry)
        return entry
