"""Decision Plane — Structured AI decision-making with evidence and governance."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class DecisionStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    ROLLED_BACK = "rolled_back"


class DecisionImpact(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    financial_sar: float = 0.0
    revenue_impact_pct: float = 0.0
    risk_level: str = "low"  # low, medium, high, critical
    affected_stakeholders: list[str] = Field(default_factory=list)
    market_segments: list[str] = Field(default_factory=list)


class DecisionAlternative(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    alt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    estimated_impact: DecisionImpact = Field(default_factory=DecisionImpact)
    recommended: bool = False


class StructuredDecision(BaseModel):
    """A business-critical decision with full governance metadata.
    
    Executive view: the decision, its financial impact, alternatives, 
    risks, required authority, and reversibility.
    """
    model_config = ConfigDict(from_attributes=True)
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    title_ar: str = ""
    summary: str = ""
    summary_ar: str = ""
    os_module: str  # sales, partnership, ma, expansion, pmi, executive
    status: DecisionStatus = DecisionStatus.DRAFT
    
    impact: DecisionImpact = Field(default_factory=DecisionImpact)
    alternatives: list[DecisionAlternative] = Field(default_factory=list)
    recommended_action: str = ""
    recommended_action_ar: str = ""
    
    approval_class: str = "R0_AUTO"
    reversibility: str = "REVERSIBLE"
    sensitivity: str = "INTERNAL"
    required_approvers: list[str] = Field(default_factory=list)
    
    evidence_pack_id: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    created_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: datetime | None = None
    decided_by: str | None = None
    
    metadata: dict[str, Any] = Field(default_factory=dict)


class DecisionEngine:
    """Produces structured, evidence-backed, approval-aware decisions."""
    
    def __init__(self):
        self._decisions: dict[str, StructuredDecision] = {}
    
    def create_decision(
        self,
        title: str,
        os_module: str,
        created_by: str,
        title_ar: str = "",
        summary: str = "",
        summary_ar: str = "",
        impact: DecisionImpact | None = None,
        approval_class: str = "R0_AUTO",
        reversibility: str = "REVERSIBLE",
        sensitivity: str = "INTERNAL",
    ) -> StructuredDecision:
        decision = StructuredDecision(
            title=title,
            title_ar=title_ar,
            summary=summary,
            summary_ar=summary_ar,
            os_module=os_module,
            impact=impact or DecisionImpact(),
            approval_class=approval_class,
            reversibility=reversibility,
            sensitivity=sensitivity,
            created_by=created_by,
        )
        self._decisions[decision.decision_id] = decision
        return decision
    
    def add_alternative(self, decision_id: str, alternative: DecisionAlternative) -> StructuredDecision:
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        decision.alternatives.append(alternative)
        return decision
    
    def propose(self, decision_id: str, recommended_action: str, recommended_action_ar: str = "") -> StructuredDecision:
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        decision.status = DecisionStatus.PROPOSED
        decision.recommended_action = recommended_action
        decision.recommended_action_ar = recommended_action_ar
        return decision
    
    def approve(self, decision_id: str, approved_by: str, evidence_pack_id: str | None = None) -> StructuredDecision:
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        decision.status = DecisionStatus.APPROVED
        decision.decided_by = approved_by
        decision.decided_at = datetime.now(timezone.utc)
        decision.evidence_pack_id = evidence_pack_id
        return decision
    
    def reject(self, decision_id: str, rejected_by: str, reason: str = "") -> StructuredDecision:
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        decision.status = DecisionStatus.REJECTED
        decision.decided_by = rejected_by
        decision.decided_at = datetime.now(timezone.utc)
        decision.metadata["rejection_reason"] = reason
        return decision
    
    def get(self, decision_id: str) -> StructuredDecision | None:
        return self._decisions.get(decision_id)
    
    def list_by_module(self, os_module: str) -> list[StructuredDecision]:
        return [d for d in self._decisions.values() if d.os_module == os_module]
    
    def list_pending(self, tenant_id: str | None = None) -> list[StructuredDecision]:
        return [d for d in self._decisions.values() if d.status == DecisionStatus.PROPOSED]


decision_engine = DecisionEngine()
