"""
Policy Engine — OPA-compatible policy evaluation.

Separates policy decision-making from the application.
Takes JSON input → evaluates rules → returns policy decisions.
"""

from __future__ import annotations

import enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.planes.decision.schemas import (
    ApprovalClass,
    ReversibilityClass,
    SensitivityClass,
)


class PolicyVerdict(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class PolicyInput(BaseModel):
    action: str
    actor_id: str
    actor_role: str
    tenant_id: str
    resource_type: str
    resource_id: Optional[str] = None
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    reversibility: ReversibilityClass = ReversibilityClass.FULLY_REVERSIBLE
    financial_impact_sar: Optional[float] = None
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseModel):
    verdict: PolicyVerdict
    required_approval: Optional[ApprovalClass] = None
    reason: str
    reason_ar: str
    policy_id: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    conditions: list[str] = Field(default_factory=list)


APPROVAL_THRESHOLDS: dict[str, dict[str, Any]] = {
    "discount": {
        "auto": {"max_pct": 5},
        "manager": {"max_pct": 15},
        "director": {"max_pct": 25},
        "vp": {"max_pct": 40},
        "c_level": {"max_pct": 100},
    },
    "commitment_sar": {
        "auto": {"max": 10_000},
        "manager": {"max": 50_000},
        "director": {"max": 500_000},
        "vp": {"max": 2_000_000},
        "c_level": {"max": 10_000_000},
        "board": {"max": float("inf")},
    },
}


def evaluate_policy(policy_input: PolicyInput) -> PolicyDecision:
    """Evaluate a policy request against the rule set. OPA-compatible interface."""

    if policy_input.reversibility == ReversibilityClass.IRREVERSIBLE:
        if policy_input.sensitivity == SensitivityClass.RESTRICTED:
            return PolicyDecision(
                verdict=PolicyVerdict.REQUIRE_APPROVAL,
                required_approval=ApprovalClass.C_LEVEL,
                reason="Irreversible + restricted sensitivity requires C-level approval",
                reason_ar="إجراء غير قابل للعكس + حساسية مقيدة يتطلب موافقة مستوى تنفيذي",
                policy_id="POL-IRR-REST-001",
            )

    if policy_input.financial_impact_sar:
        amount = policy_input.financial_impact_sar
        thresholds = APPROVAL_THRESHOLDS["commitment_sar"]
        for level, config in thresholds.items():
            if amount <= config["max"]:
                approval = ApprovalClass(level)
                if approval == ApprovalClass.AUTO:
                    return PolicyDecision(
                        verdict=PolicyVerdict.ALLOW,
                        reason=f"Amount {amount} SAR within auto-approval threshold",
                        reason_ar=f"المبلغ {amount} ريال ضمن حد الموافقة التلقائية",
                        policy_id="POL-FIN-001",
                    )
                return PolicyDecision(
                    verdict=PolicyVerdict.REQUIRE_APPROVAL,
                    required_approval=approval,
                    reason=f"Amount {amount} SAR requires {level} approval",
                    reason_ar=f"المبلغ {amount} ريال يتطلب موافقة {level}",
                    policy_id="POL-FIN-001",
                )

    return PolicyDecision(
        verdict=PolicyVerdict.ALLOW,
        reason="No policy constraints triggered",
        reason_ar="لم يتم تفعيل أي قيود سياسية",
        policy_id="POL-DEFAULT",
    )


class EvidencePack(BaseModel):
    pack_id: str
    decision_id: str
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    decision_summary: str
    decision_summary_ar: str
    financial_impact_sar: Optional[float] = None
    alternatives_considered: list[str] = Field(default_factory=list)
    risk_assessment: str = ""
    supporting_documents: list[str] = Field(default_factory=list)
    approval_chain: list[dict[str, Any]] = Field(default_factory=list)
    compliance_checks: list[str] = Field(default_factory=list)


class SaudiComplianceCheck(BaseModel):
    check_id: str
    framework: str  # PDPL, NCA-ECC, NIST-AI-RMF, OWASP-LLM
    control_ref: str
    status: str  # passed, failed, not_applicable, pending
    evidence: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    next_review: Optional[datetime] = None
