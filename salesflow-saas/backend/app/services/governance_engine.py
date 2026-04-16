"""
Governance & Policy Engine — Dealix Sovereign Growth OS
═══════════════════════════════════════════════════════
Policy-as-Code enforcement for all strategic operations.

Every sensitive action passes through this engine before execution:
  1. Authority check (who can approve what)
  2. Policy gates (mandatory conditions)
  3. Risk assessment
  4. Audit trail
  5. HITL routing

Principles:
  - No silent decisions
  - No uncited financial assumption
  - No sensitive action without policy check
  - No production action without rollback
  - No strategic initiative without owner + SLA + expected ROI
"""
from __future__ import annotations

import enum
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger("dealix.governance")


# ── Approval Matrix ───────────────────────────────────────────

class ApprovalThreshold(BaseModel):
    """Defines who can approve what, at what financial threshold."""
    action_type: str
    max_amount_sar: Optional[float] = None  # None = unlimited
    required_role: str       # agent, manager, director, cxo, board
    requires_risk_memo: bool = False
    requires_compliance_check: bool = False
    requires_financial_impact: bool = False
    requires_rollback_plan: bool = False


# Default approval matrix
APPROVAL_MATRIX: List[ApprovalThreshold] = [
    # Partnerships
    ApprovalThreshold(action_type="partnership.sign_referral", max_amount_sar=100_000, required_role="manager"),
    ApprovalThreshold(action_type="partnership.sign_rev_share", max_amount_sar=500_000, required_role="director",
                      requires_risk_memo=True, requires_financial_impact=True),
    ApprovalThreshold(action_type="partnership.sign_jv", max_amount_sar=None, required_role="cxo",
                      requires_risk_memo=True, requires_compliance_check=True,
                      requires_financial_impact=True, requires_rollback_plan=True),
    # M&A
    ApprovalThreshold(action_type="ma.submit_loi", max_amount_sar=5_000_000, required_role="cxo",
                      requires_risk_memo=True, requires_compliance_check=True,
                      requires_financial_impact=True, requires_rollback_plan=True),
    ApprovalThreshold(action_type="ma.submit_offer", max_amount_sar=None, required_role="board",
                      requires_risk_memo=True, requires_compliance_check=True,
                      requires_financial_impact=True, requires_rollback_plan=True),
    # Expansion
    ApprovalThreshold(action_type="expansion.launch_market", max_amount_sar=1_000_000, required_role="director",
                      requires_risk_memo=True, requires_compliance_check=True,
                      requires_financial_impact=True),
    ApprovalThreshold(action_type="expansion.stop_loss", max_amount_sar=None, required_role="cxo",
                      requires_risk_memo=True),
    # Capital
    ApprovalThreshold(action_type="capital.commit_opex", max_amount_sar=50_000, required_role="manager"),
    ApprovalThreshold(action_type="capital.commit_capex", max_amount_sar=500_000, required_role="director",
                      requires_financial_impact=True),
    ApprovalThreshold(action_type="capital.commit_capex", max_amount_sar=None, required_role="cxo",
                      requires_financial_impact=True, requires_rollback_plan=True),
    # Data/Privacy
    ApprovalThreshold(action_type="data.bulk_outreach", max_amount_sar=None, required_role="manager",
                      requires_compliance_check=True),
    ApprovalThreshold(action_type="data.share_with_partner", max_amount_sar=None, required_role="director",
                      requires_compliance_check=True),
]


# ── Policy Gates ──────────────────────────────────────────────

class PolicyGate(BaseModel):
    """A condition that MUST be true before an action can proceed."""
    id: str
    description: str
    description_ar: str
    check_fn_name: str  # Name of the check function
    severity: str = "blocking"  # blocking | warning
    applies_to: List[str] = Field(default_factory=list)  # action_types


POLICY_GATES: List[PolicyGate] = [
    PolicyGate(
        id="PG-001", description="Risk memo must exist before term sheet",
        description_ar="يجب وجود مذكرة مخاطر قبل إرسال Term Sheet",
        check_fn_name="check_risk_memo_exists",
        applies_to=["partnership.sign_rev_share", "partnership.sign_jv", "ma.submit_loi", "ma.submit_offer"],
    ),
    PolicyGate(
        id="PG-002", description="Compliance clearance required for new market entry",
        description_ar="يجب الحصول على موافقة الامتثال قبل دخول سوق جديد",
        check_fn_name="check_compliance_clearance",
        applies_to=["expansion.launch_market"],
    ),
    PolicyGate(
        id="PG-003", description="Financial inputs must be < 30 days old for valuation",
        description_ar="البيانات المالية يجب أن تكون أحدث من ٣٠ يوماً للتقييم",
        check_fn_name="check_financial_freshness",
        applies_to=["ma.submit_loi", "ma.submit_offer"],
    ),
    PolicyGate(
        id="PG-004", description="PDPL consent must be verified before bulk outreach",
        description_ar="يجب التحقق من موافقة PDPL قبل الإرسال الجماعي",
        check_fn_name="check_pdpl_consent",
        applies_to=["data.bulk_outreach"],
    ),
    PolicyGate(
        id="PG-005", description="No acquisition offer without completed DD",
        description_ar="لا يجوز تقديم عرض استحواذ بدون إكمال الفحص النافي للجهالة",
        check_fn_name="check_dd_completed",
        applies_to=["ma.submit_offer"],
    ),
]


# ── Audit Entry ───────────────────────────────────────────────

class AuditEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action_type: str
    actor: str              # agent name or user email
    decision: str           # approved, denied, escalated, auto_approved
    amount_sar: Optional[float] = None
    policy_gates_checked: List[str] = Field(default_factory=list)
    policy_gates_passed: List[str] = Field(default_factory=list)
    policy_gates_failed: List[str] = Field(default_factory=list)
    approval_level: str = ""
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ── Governance Engine ─────────────────────────────────────────

class GovernanceEngine:
    """
    Central governance engine. All strategic actions pass through here.

    Usage:
        engine = get_governance_engine()
        result = await engine.evaluate(
            tenant_id=...,
            action_type="ma.submit_loi",
            actor="valuation_synergy",
            amount_sar=5_000_000,
            context={...}
        )
        if result.decision == "approved":
            # proceed
        elif result.decision == "escalated":
            # wait for HITL
    """

    def __init__(self):
        self._audit_log: List[AuditEntry] = []
        self._approval_matrix = APPROVAL_MATRIX
        self._policy_gates = POLICY_GATES

    async def evaluate(
        self,
        tenant_id: UUID,
        action_type: str,
        actor: str,
        amount_sar: Optional[float] = None,
        context: Optional[Dict] = None,
    ) -> AuditEntry:
        """
        Evaluate whether an action is permitted.

        Returns an AuditEntry with decision:
          - "auto_approved" — all checks pass, within agent authority
          - "escalated" — requires human approval (HITL)
          - "denied" — policy gate failed (blocking)
        """
        context = context or {}
        gates_checked = []
        gates_passed = []
        gates_failed = []

        # 1. Check policy gates
        applicable_gates = [g for g in self._policy_gates if action_type in g.applies_to]
        for gate in applicable_gates:
            gates_checked.append(gate.id)
            passed = self._run_gate_check(gate, context)
            if passed:
                gates_passed.append(gate.id)
            else:
                gates_failed.append(gate.id)
                if gate.severity == "blocking":
                    entry = AuditEntry(
                        tenant_id=tenant_id,
                        action_type=action_type,
                        actor=actor,
                        decision="denied",
                        amount_sar=amount_sar,
                        policy_gates_checked=gates_checked,
                        policy_gates_passed=gates_passed,
                        policy_gates_failed=gates_failed,
                        rationale=f"Blocked by policy gate {gate.id}: {gate.description}",
                    )
                    self._audit_log.append(entry)
                    logger.warning(f"[Governance] DENIED {action_type} by {actor}: {gate.id}")
                    return entry

        # 2. Check approval matrix
        threshold = self._find_threshold(action_type, amount_sar)
        required_role = threshold.required_role if threshold else "agent"

        # Agents can auto-approve only agent-level actions
        if required_role == "agent":
            decision = "auto_approved"
        else:
            decision = "escalated"

        entry = AuditEntry(
            tenant_id=tenant_id,
            action_type=action_type,
            actor=actor,
            decision=decision,
            amount_sar=amount_sar,
            policy_gates_checked=gates_checked,
            policy_gates_passed=gates_passed,
            policy_gates_failed=gates_failed,
            approval_level=required_role,
            rationale=f"Requires {required_role} approval" if decision == "escalated" else "All gates passed, within authority",
            metadata={"threshold": threshold.model_dump() if threshold else {}},
        )
        self._audit_log.append(entry)
        logger.info(f"[Governance] {decision.upper()} {action_type} by {actor} (level={required_role})")
        return entry

    def get_audit_log(self, tenant_id: Optional[UUID] = None, limit: int = 100) -> List[AuditEntry]:
        entries = self._audit_log
        if tenant_id:
            entries = [e for e in entries if e.tenant_id == tenant_id]
        return entries[-limit:]

    def get_pending_escalations(self, tenant_id: Optional[UUID] = None) -> List[AuditEntry]:
        entries = [e for e in self._audit_log if e.decision == "escalated"]
        if tenant_id:
            entries = [e for e in entries if e.tenant_id == tenant_id]
        return entries

    def _find_threshold(self, action_type: str, amount: Optional[float]) -> Optional[ApprovalThreshold]:
        matches = [t for t in self._approval_matrix if t.action_type == action_type]
        if not matches:
            return None
        if amount is None:
            return matches[-1]  # Highest threshold
        for t in matches:
            if t.max_amount_sar is None or amount <= t.max_amount_sar:
                return t
        return matches[-1]

    def _run_gate_check(self, gate: PolicyGate, context: Dict) -> bool:
        """Run a policy gate check. Returns True if passed."""
        checks = {
            "check_risk_memo_exists": lambda c: bool(c.get("risk_memo")),
            "check_compliance_clearance": lambda c: bool(c.get("compliance_cleared")),
            "check_financial_freshness": lambda c: c.get("financial_data_age_days", 999) <= 30,
            "check_pdpl_consent": lambda c: bool(c.get("pdpl_consent_verified")),
            "check_dd_completed": lambda c: bool(c.get("dd_completed")),
        }
        fn = checks.get(gate.check_fn_name)
        if fn is None:
            logger.warning(f"[Governance] Unknown gate check: {gate.check_fn_name}")
            return True  # Unknown gates pass by default (fail-open for now)
        return fn(context)


# ── Singleton ─────────────────────────────────────────────────

_engine: Optional[GovernanceEngine] = None


def get_governance_engine() -> GovernanceEngine:
    global _engine
    if _engine is None:
        _engine = GovernanceEngine()
    return _engine
