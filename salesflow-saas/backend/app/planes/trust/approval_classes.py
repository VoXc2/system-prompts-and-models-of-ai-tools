"""
Trust Plane — Approval, Reversibility & Sensitivity Classes.

Defines the governance framework that gates every autonomous action
in the Dealix Sovereign OS.

فئات الموافقة والحوكمة — مستوى الثقة في نظام ديلكس
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ApprovalClass(str, Enum):
    """Gate level required before an action may execute."""
    R0_AUTO = "R0_AUTO"
    R1_NOTIFY = "R1_NOTIFY"
    R2_APPROVE = "R2_APPROVE"
    R3_COMMITTEE = "R3_COMMITTEE"


class ReversibilityClass(str, Enum):
    """Indicates how easily the effects of an action can be undone."""
    REVERSIBLE = "REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class SensitivityClass(str, Enum):
    """Data-classification level attached to an action's payload."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class PolicyGateResult(BaseModel):
    """Outcome returned by the policy engine for a single action evaluation."""
    model_config = ConfigDict(from_attributes=True)

    allowed: bool
    approval_class: ApprovalClass
    reversibility: ReversibilityClass
    sensitivity: SensitivityClass
    required_approvers: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ── Default governance map ───────────────────────────────────────────
# Each entry: (ApprovalClass, ReversibilityClass, SensitivityClass)

ACTION_POLICY_MAP: dict[str, tuple[ApprovalClass, ReversibilityClass, SensitivityClass]] = {
    # R0 — fully automated
    "lead_capture":               (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "enrichment":                 (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "scoring":                    (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "routing":                    (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "follow_up":                  (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "meeting_reminder":           (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.PUBLIC),
    "memo_draft":                 (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "evidence_pack_assembly":     (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "dd_checklist_orchestration": (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "task_assignment":            (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "sla_reminder":               (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "dashboard_update":           (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "telemetry":                  (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "quality_check":              (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "document_extraction":        (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "connector_sync":             (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "variance_detection":         (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    "anomaly_alert":              (ApprovalClass.R0_AUTO, ReversibilityClass.REVERSIBLE, SensitivityClass.INTERNAL),
    # R2 — require explicit approval
    "term_sheet_send":            (ApprovalClass.R2_APPROVE, ReversibilityClass.PARTIALLY_REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "signature_request":          (ApprovalClass.R2_APPROVE, ReversibilityClass.IRREVERSIBLE, SensitivityClass.RESTRICTED),
    "partnership_activation":     (ApprovalClass.R2_APPROVE, ReversibilityClass.PARTIALLY_REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "market_entry_launch":        (ApprovalClass.R2_APPROVE, ReversibilityClass.PARTIALLY_REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "discount_override":          (ApprovalClass.R2_APPROVE, ReversibilityClass.REVERSIBLE, SensitivityClass.CONFIDENTIAL),
    "data_sharing_sensitive":     (ApprovalClass.R2_APPROVE, ReversibilityClass.PARTIALLY_REVERSIBLE, SensitivityClass.RESTRICTED),
    "prod_rollout":               (ApprovalClass.R2_APPROVE, ReversibilityClass.PARTIALLY_REVERSIBLE, SensitivityClass.INTERNAL),
    # R3 — require committee/board approval
    "ma_offer_send":              (ApprovalClass.R3_COMMITTEE, ReversibilityClass.IRREVERSIBLE, SensitivityClass.RESTRICTED),
    "closing_approval":           (ApprovalClass.R3_COMMITTEE, ReversibilityClass.IRREVERSIBLE, SensitivityClass.RESTRICTED),
    "external_capital_commitment": (ApprovalClass.R3_COMMITTEE, ReversibilityClass.IRREVERSIBLE, SensitivityClass.RESTRICTED),
}


def evaluate_action(action: str, context: dict | None = None) -> PolicyGateResult:
    """Look up *action* in the governance map and return a gate result.

    Unknown actions default to R2_APPROVE / PARTIALLY_REVERSIBLE / CONFIDENTIAL
    to enforce the principle of least privilege.
    """
    default = (
        ApprovalClass.R2_APPROVE,
        ReversibilityClass.PARTIALLY_REVERSIBLE,
        SensitivityClass.CONFIDENTIAL,
    )
    approval, reversibility, sensitivity = ACTION_POLICY_MAP.get(action, default)

    allowed = approval == ApprovalClass.R0_AUTO
    metadata: dict = {}
    if context:
        metadata["context"] = context

    return PolicyGateResult(
        allowed=allowed,
        approval_class=approval,
        reversibility=reversibility,
        sensitivity=sensitivity,
        metadata=metadata,
    )
