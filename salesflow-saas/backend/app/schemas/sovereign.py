"""Pydantic schemas for Sovereign Growth OS API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Partnership OS ──────────────────────────────────────────────

class PartnerCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    partner_type: str = "channel"
    website: Optional[str] = None
    country: str = "SA"
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class PartnerResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    partner_type: str
    status: str
    strategic_fit_score: int
    tier: str
    country: str
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    activated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PartnerScorecardResponse(BaseModel):
    id: str
    partner_id: str
    period: str
    revenue_generated_sar: float
    leads_referred: int
    deals_closed: int
    contribution_margin_pct: float
    health_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── M&A OS ──────────────────────────────────────────────────────

class AcquisitionTargetCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    industry: Optional[str] = None
    country: str = "SA"
    estimated_value_sar: Optional[float] = None
    revenue_sar: Optional[float] = None
    rationale: Optional[str] = None
    rationale_ar: Optional[str] = None


class AcquisitionTargetResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    status: str
    industry: Optional[str] = None
    strategic_fit_score: int
    estimated_value_sar: Optional[float] = None
    revenue_sar: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DDStreamResponse(BaseModel):
    id: str
    target_id: str
    stream_type: str
    status: str
    sla_hours: int
    documents_requested: int
    documents_received: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Expansion OS ────────────────────────────────────────────────

class ExpansionMarketCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    country: str
    region: Optional[str] = None
    segment: Optional[str] = None
    market_size_sar: Optional[float] = None


class ExpansionMarketResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    country: str
    status: str
    priority_score: int
    regulatory_readiness: str
    launch_readiness_pct: int
    launched_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── PMI OS ──────────────────────────────────────────────────────

class PMIProgramCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    source_type: str
    source_id: str
    synergy_target_sar: Optional[float] = None


class PMIProgramResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str] = None
    source_type: str
    status: str
    day1_ready: bool
    synergy_target_sar: Optional[float] = None
    synergy_realized_sar: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Executive OS ────────────────────────────────────────────────

class ExecutiveApprovalCreate(BaseModel):
    resource_type: str
    resource_id: str
    action: str
    approval_class: str
    financial_impact_sar: Optional[float] = None
    rationale: Optional[str] = None
    rationale_ar: Optional[str] = None
    risk_summary: Optional[str] = None
    risk_summary_ar: Optional[str] = None


class ExecutiveApprovalResponse(BaseModel):
    id: str
    resource_type: str
    action: str
    approval_class: str
    sensitivity_class: str
    reversibility_class: str
    status: str
    financial_impact_sar: Optional[float] = None
    rationale: Optional[str] = None
    rationale_ar: Optional[str] = None
    evidence_pack_id: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BoardMemoCreate(BaseModel):
    title: str
    title_ar: Optional[str] = None
    memo_type: str
    summary: Optional[str] = None
    summary_ar: Optional[str] = None


class BoardMemoResponse(BaseModel):
    id: str
    title: str
    title_ar: Optional[str] = None
    memo_type: str
    status: str
    submitted_at: Optional[datetime] = None
    meeting_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyViolationResponse(BaseModel):
    id: str
    violation_type: str
    severity: str
    description: str
    description_ar: Optional[str] = None
    status: str
    policy_ref: Optional[str] = None
    detected_by: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiskHeatmapResponse(BaseModel):
    id: str
    category: str
    risk_name: str
    risk_name_ar: Optional[str] = None
    probability: str
    impact: str
    score: int
    status: str
    last_reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ForecastResponse(BaseModel):
    id: str
    period: str
    category: str
    forecast_sar: Optional[float] = None
    actual_sar: Optional[float] = None
    variance_pct: Optional[float] = None

    class Config:
        from_attributes = True


class ComplianceMatrixResponse(BaseModel):
    id: str
    framework: str
    control_id: str
    control_name: str
    control_name_ar: Optional[str] = None
    status: str
    last_assessed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Planes Health ───────────────────────────────────────────────

class PlaneHealth(BaseModel):
    plane: str
    status: str
    components: list[dict[str, Any]] = Field(default_factory=list)
    last_check: datetime = Field(default_factory=datetime.utcnow)
