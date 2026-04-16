from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.openclaw.policy import classify_action


class OperatingPlane(str, Enum):
    DECISION = "decision"
    EXECUTION = "execution"
    TRUST = "trust"
    DATA = "data"
    OPERATING = "operating"


class ApprovalClass(str, Enum):
    AUTO = "auto"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    BOARD = "board"
    FORBIDDEN = "forbidden"


class ReversibilityClass(str, Enum):
    R0 = "R0"  # Fully reversible
    R1 = "R1"  # Reversible with operational cost
    R2 = "R2"  # Externally committed but partially reversible
    R3 = "R3"  # Irreversible strategic commitment


class SensitivityClass(str, Enum):
    S0 = "S0"  # Low sensitivity
    S1 = "S1"  # Internal operational
    S2 = "S2"  # Commercially sensitive
    S3 = "S3"  # Regulated / high sensitivity


class EvidenceRef(BaseModel):
    type: str = Field(default="memo")
    ref: str
    title: Optional[str] = None


class GovernanceContract(BaseModel):
    action: str
    plane: OperatingPlane
    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_class: SensitivityClass
    requires_human_approval: bool
    policy_tags: List[str] = Field(default_factory=list)
    rationale_ar: str


class GovernanceTrace(BaseModel):
    trace_id: str
    correlation_id: str


def _clean_text(value: str) -> str:
    return (value or "").strip().lower()


def _pick_action(channel: str, resource_type: str, action_hint: Optional[str]) -> str:
    if action_hint and action_hint.strip():
        return action_hint.strip()
    ch = _clean_text(channel)
    if ch == "whatsapp":
        return "send_whatsapp"
    if ch == "email":
        return "send_email"
    if ch == "sms":
        return "send_sms"
    rt = _clean_text(resource_type)
    if "signature" in rt or "contract" in rt:
        return "send_contract_for_signature"
    return f"{ch or 'unknown'}:{rt or 'generic_action'}"


def _infer_plane(resource_type: str, payload: Dict[str, Any]) -> OperatingPlane:
    rt = _clean_text(resource_type)
    payload_text = _clean_text(str(payload))
    merged = f"{rt} {payload_text}"
    if any(k in merged for k in ("rollout", "release", "deploy", "environment", "prod", "ci", "cd")):
        return OperatingPlane.OPERATING
    if any(k in merged for k in ("data_sharing", "pdpl", "pii", "privacy", "consent", "export")):
        return OperatingPlane.DATA
    if any(k in merged for k in ("term_sheet", "discount", "offer", "pricing", "board", "strategy")):
        return OperatingPlane.DECISION
    if any(k in merged for k in ("onboarding", "activation", "pmi", "integration", "handoff")):
        return OperatingPlane.EXECUTION
    return OperatingPlane.TRUST


def _infer_reversibility(action: str, resource_type: str, payload: Dict[str, Any]) -> ReversibilityClass:
    merged = _clean_text(f"{action} {resource_type} {payload}")
    if any(
        k in merged
        for k in (
            "acquisition_offer",
            "exclusive",
            "market_commitment",
            "close_approval",
            "capital_commitment",
            "prod_rollout",
            "board_commitment",
        )
    ):
        return ReversibilityClass.R3
    if any(k in merged for k in ("term_sheet", "rev_share", "signature", "contract", "partnership_activation")):
        return ReversibilityClass.R2
    if any(k in merged for k in ("send_whatsapp", "send_email", "send_sms", "discount")):
        return ReversibilityClass.R1
    return ReversibilityClass.R0


def _infer_sensitivity(resource_type: str, payload: Dict[str, Any]) -> SensitivityClass:
    merged = _clean_text(f"{resource_type} {payload}")
    if any(k in merged for k in ("pdpl", "pii", "personal_data", "data_sharing", "financial", "legal", "board")):
        return SensitivityClass.S3
    if any(k in merged for k in ("discount", "pricing", "contract", "term_sheet", "valuation")):
        return SensitivityClass.S2
    if any(k in merged for k in ("internal", "ops", "workflow", "approval")):
        return SensitivityClass.S1
    return SensitivityClass.S0


def _infer_approval_class(
    *,
    policy_class: str,
    requires_approval: bool,
    reversibility: ReversibilityClass,
    sensitivity: SensitivityClass,
) -> ApprovalClass:
    if policy_class == "C":
        return ApprovalClass.FORBIDDEN
    if reversibility == ReversibilityClass.R3 or sensitivity == SensitivityClass.S3:
        return ApprovalClass.BOARD
    if requires_approval or reversibility == ReversibilityClass.R2 or sensitivity == SensitivityClass.S2:
        return ApprovalClass.EXECUTIVE
    if reversibility == ReversibilityClass.R1 or sensitivity == SensitivityClass.S1:
        return ApprovalClass.MANAGER
    return ApprovalClass.AUTO


def _coerce_enum(value: Any, enum_cls):
    if not value:
        return None
    try:
        return enum_cls(value)
    except Exception:
        return None


def build_governance_bundle(
    *,
    channel: str,
    resource_type: str,
    payload: Optional[Dict[str, Any]] = None,
    action_hint: Optional[str] = None,
    governance_input: Optional[Dict[str, Any]] = None,
    evidence_refs: Optional[List[Dict[str, Any]]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload_data = payload or {}
    provided = governance_input or {}
    action = _pick_action(channel, resource_type, action_hint)
    policy = classify_action(action)

    plane = _coerce_enum(provided.get("plane"), OperatingPlane) or _infer_plane(resource_type, payload_data)
    reversibility = _coerce_enum(provided.get("reversibility_class"), ReversibilityClass) or _infer_reversibility(
        action,
        resource_type,
        payload_data,
    )
    sensitivity = _coerce_enum(provided.get("sensitivity_class"), SensitivityClass) or _infer_sensitivity(
        resource_type,
        payload_data,
    )
    approval_class = _coerce_enum(provided.get("approval_class"), ApprovalClass) or _infer_approval_class(
        policy_class=policy.action_class,
        requires_approval=policy.requires_approval,
        reversibility=reversibility,
        sensitivity=sensitivity,
    )

    requires_human_approval = bool(policy.requires_approval or approval_class != ApprovalClass.AUTO)
    policy_tags = list(dict.fromkeys(
        [
            f"policy_class:{policy.action_class}",
            f"plane:{plane.value}",
            f"reversibility:{reversibility.value}",
            f"sensitivity:{sensitivity.value}",
            "pdpl_aware" if sensitivity == SensitivityClass.S3 else "standard_control",
        ]
    ))
    rationale = "قرار حساس أو التزام طويل العمر — يلزم تتبع، أدلة، واعتماد بشري قبل الالتزام."
    if approval_class == ApprovalClass.AUTO:
        rationale = "إجراء منخفض المخاطر وقابل للعكس — يسمح بالأتمتة مع التتبع."
    contract = GovernanceContract(
        action=action,
        plane=plane,
        approval_class=approval_class,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        requires_human_approval=requires_human_approval,
        policy_tags=policy_tags,
        rationale_ar=rationale,
    )

    clean_evidence: List[EvidenceRef] = []
    for item in evidence_refs or []:
        ref = (item or {}).get("ref")
        if ref:
            clean_evidence.append(EvidenceRef(type=(item or {}).get("type") or "memo", ref=str(ref), title=(item or {}).get("title")))

    trace = GovernanceTrace(
        trace_id=f"trace_{uuid4().hex}",
        correlation_id=correlation_id or f"corr_{uuid4().hex}",
    )
    violations: List[str] = []
    if not policy.allowed:
        violations.append(f"policy_blocked:{policy.reason}")
    if approval_class == ApprovalClass.AUTO and policy.requires_approval:
        violations.append("contract_conflict:auto_with_policy_gate")

    return {
        "contract": contract.model_dump(),
        "policy": policy.as_dict(),
        "trace": trace.model_dump(),
        "evidence_refs": [e.model_dump() for e in clean_evidence],
        "violations": violations,
    }
