"""
Policy evaluator — Trust Plane's gatekeeper.

This is a lightweight in-process policy engine that evaluates a
DecisionOutput (or a raw action) against a set of rules and returns
one of: ALLOW, DENY, ESCALATE.

In production, this should be backed by OPA/Rego. The interface is
designed so the internals can be swapped without changing callers.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from dealix.classifications import (
    NEVER_AUTO_EXECUTE,
    ApprovalClass,
    ReversibilityClass,
    SensitivityClass,
)
from dealix.contracts.decision import DecisionOutput, NextAction


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass
class PolicyResult:
    decision: PolicyDecision
    rule_name: str
    reason: str
    required_approvers: int = 0

    @property
    def is_allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW


@dataclass
class PolicyRule:
    name: str
    description: str
    # callable that returns None (no match) or a PolicyResult
    evaluate: Callable[[NextAction, DecisionOutput], PolicyResult | None]


# ─────────────────────────────────────────────────────────────
# Built-in rules
# ─────────────────────────────────────────────────────────────


def _rule_never_auto_execute(action: NextAction, decision: DecisionOutput) -> PolicyResult | None:
    if action.action_type in NEVER_AUTO_EXECUTE:
        return PolicyResult(
            decision=PolicyDecision.ESCALATE,
            rule_name="never_auto_execute",
            reason=(
                f"Action '{action.action_type}' is on the NEVER_AUTO_EXECUTE list — "
                "executive approval required"
            ),
            required_approvers=2,
        )
    return None


def _rule_r3_blocks_auto(action: NextAction, decision: DecisionOutput) -> PolicyResult | None:
    if action.reversibility_class == ReversibilityClass.R3:
        return PolicyResult(
            decision=PolicyDecision.ESCALATE,
            rule_name="r3_blocks_auto",
            reason="R3 (irreversible) actions require human approval",
            required_approvers=max(1, action.approval_class.minimum_approvers),
        )
    return None


def _rule_a2_plus_requires_evidence(
    action: NextAction, decision: DecisionOutput
) -> PolicyResult | None:
    if action.approval_class in (ApprovalClass.A2, ApprovalClass.A3):
        if len(decision.evidence) == 0:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                rule_name="a2_plus_requires_evidence",
                reason="A2/A3 actions require at least one Evidence item in the decision",
            )
    return None


def _rule_s3_requires_pdpl_check(
    action: NextAction, decision: DecisionOutput
) -> PolicyResult | None:
    if action.sensitivity_class == SensitivityClass.S3:
        # In a real deployment this checks the PDPL register for lawful basis
        # + purpose + consent status for the entity.
        pdpl_checked = any(p.policy_name == "pdpl_lawful_basis" for p in action.policy_requirements)
        if not pdpl_checked:
            return PolicyResult(
                decision=PolicyDecision.ESCALATE,
                rule_name="s3_requires_pdpl_check",
                reason="S3 (personal data) actions require an explicit PDPL lawful basis check",
                required_approvers=1,
            )
    return None


def _rule_low_confidence_high_stakes(
    action: NextAction, decision: DecisionOutput
) -> PolicyResult | None:
    if decision.is_high_stakes and decision.confidence < 0.6:
        return PolicyResult(
            decision=PolicyDecision.ESCALATE,
            rule_name="low_confidence_high_stakes",
            reason=(
                f"High-stakes decision with confidence {decision.confidence:.2f} < 0.6 "
                "requires human review"
            ),
            required_approvers=1,
        )
    return None


def _rule_approval_class_routing(
    action: NextAction, decision: DecisionOutput
) -> PolicyResult | None:
    if not action.approval_class.requires_approval:
        return None
    return PolicyResult(
        decision=PolicyDecision.ESCALATE,
        rule_name="approval_class_routing",
        reason=f"Approval class {action.approval_class.value} requires approval",
        required_approvers=action.approval_class.minimum_approvers,
    )


DEFAULT_RULES: list[PolicyRule] = [
    PolicyRule(
        name="never_auto_execute",
        description="Block actions that are always human-in-the-loop",
        evaluate=_rule_never_auto_execute,
    ),
    PolicyRule(
        name="r3_blocks_auto",
        description="R3 (irreversible) actions always escalate",
        evaluate=_rule_r3_blocks_auto,
    ),
    PolicyRule(
        name="a2_plus_requires_evidence",
        description="A2/A3 actions must carry evidence",
        evaluate=_rule_a2_plus_requires_evidence,
    ),
    PolicyRule(
        name="s3_requires_pdpl_check",
        description="Personal data actions require PDPL lawful basis",
        evaluate=_rule_s3_requires_pdpl_check,
    ),
    PolicyRule(
        name="low_confidence_high_stakes",
        description="High-stakes + low confidence escalates",
        evaluate=_rule_low_confidence_high_stakes,
    ),
    PolicyRule(
        name="approval_class_routing",
        description="Approval class A1+ escalates",
        evaluate=_rule_approval_class_routing,
    ),
]


class PolicyEvaluator:
    """Evaluate actions within a decision against the rule set.

    Returns the FIRST matching rule's result in precedence order.
    """

    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self.rules = rules if rules is not None else DEFAULT_RULES

    def evaluate(self, action: NextAction, decision: DecisionOutput) -> PolicyResult:
        """Evaluate one action; returns ALLOW if no rule matches."""
        for rule in self.rules:
            result = rule.evaluate(action, decision)
            if result is not None:
                return result
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            rule_name="default_allow",
            reason="No blocking rule matched",
        )

    def evaluate_all(self, decision: DecisionOutput) -> list[tuple[NextAction, PolicyResult]]:
        """Evaluate every NextAction in a decision."""
        return [(a, self.evaluate(a, decision)) for a in decision.next_actions]
