"""Structured payloads for Dealix Sovereign Growth, Execution & Governance OS."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


class PlaneHealth(BaseModel):
    """Runtime posture for one architectural plane."""

    plane: Literal["decision", "execution", "trust", "data", "operating"]
    status: Literal["healthy", "degraded", "blocked"]
    signals: list[str] = Field(default_factory=list)


class SalesOsSignals(BaseModel):
    """Operational truth for Sales & Revenue OS (funnel + commitments)."""

    total_leads: int
    new_leads_today: int
    total_deals: int
    open_deals_value_sar: Decimal
    closed_won_value_sar: Decimal
    closed_won_count: int
    messages_sent_today: int
    conversion_rate_pct: float
    active_workflows: int
    upcoming_meetings_7d: int
    proposals_draft: int
    proposals_pending_send: int


class PipelineBoard(BaseModel):
    """Generic pipeline slice for executive surfaces."""

    title: str
    title_ar: str
    total: int
    by_stage: dict[str, int]
    items: list[dict[str, Any]] = Field(default_factory=list)


class RiskHeatmap(BaseModel):
    """Lightweight risk posture derived from operational signals."""

    score_0_100: int
    drivers: list[str] = Field(default_factory=list)


class ComplianceMatrixRow(BaseModel):
    """Saudi-ready control mapping row (evidence-backed in product)."""

    control_id: str
    domain: Literal["pdpl", "nca_ecc", "ai_governance"]
    status: Literal["aligned", "partial", "gap"]
    evidence_hint: str
    evidence_hint_ar: str


class ModelRouteRow(BaseModel):
    """Internal routing fabric entry (task → default model slot)."""

    task_type: str
    model_slot: str


class ToolVerificationEntry(BaseModel):
    """Tool / connector verification ledger row (audit-oriented)."""

    tool_id: str
    last_verified_at: datetime | None
    status: Literal["verified", "pending", "failed"]
    connector_version: str | None = None


class ReleaseGateStatus(BaseModel):
    """Operating plane — release / environment gate snapshot."""

    environment: str
    rulesets_required: bool
    oidc_preferred: bool
    last_gate_check_at: datetime | None = None


class SovereignOsSnapshot(BaseModel):
    """Single JSON document for the enterprise command center."""

    generated_at: datetime
    tenant_id: str
    correlation_id: str | None = None

    planes: list[PlaneHealth] = Field(default_factory=list)
    sales_os: SalesOsSignals
    partnership: PipelineBoard
    ma_corp_dev: PipelineBoard
    expansion: PipelineBoard
    pmi_pmo: PipelineBoard
    executive: dict[str, Any] = Field(default_factory=dict)

    approvals_pending: int
    policy_violations_open: int
    risk: RiskHeatmap
    compliance_matrix: list[ComplianceMatrixRow] = Field(default_factory=list)
    model_routing_fabric: list[ModelRouteRow] = Field(default_factory=list)
    tool_verification_ledger: list[ToolVerificationEntry] = Field(default_factory=list)
    release_gate: ReleaseGateStatus
