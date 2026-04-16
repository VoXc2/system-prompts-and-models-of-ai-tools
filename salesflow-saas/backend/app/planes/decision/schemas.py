"""Typed structured outputs for all Decision Plane operations."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class SensitivityClass(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ReversibilityClass(str, enum.Enum):
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


class ApprovalClass(str, enum.Enum):
    AUTO = "auto"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"
    BOARD = "board"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionContext(BaseModel):
    trace_id: str
    correlation_id: str
    tenant_id: str
    actor_id: str
    actor_role: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    plane: str = "decision"


class StructuredDecision(BaseModel):
    decision_id: str
    context: DecisionContext
    action: str
    rationale: str
    rationale_ar: str
    alternatives: list[str] = Field(default_factory=list)
    financial_impact_sar: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.LOW
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    reversibility: ReversibilityClass = ReversibilityClass.FULLY_REVERSIBLE
    required_approval: ApprovalClass = ApprovalClass.AUTO
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GuardrailResult(BaseModel):
    passed: bool
    rule_id: str
    rule_name: str
    rule_name_ar: str
    message: str
    message_ar: str
    severity: RiskLevel = RiskLevel.LOW
    blocked: bool = False


class ModelRoutingDecision(BaseModel):
    task_class: str
    selected_model: str
    fallback_model: Optional[str] = None
    reason: str
    estimated_latency_ms: Optional[int] = None
    estimated_cost_usd: Optional[float] = None


class ToolVerification(BaseModel):
    tool_id: str
    tool_name: str
    verified: bool
    version: str
    checksum: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    connector_health: str = "unknown"
