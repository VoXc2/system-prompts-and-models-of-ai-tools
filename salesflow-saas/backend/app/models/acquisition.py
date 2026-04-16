"""M&A / Corporate Development OS — full acquisition lifecycle models."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class AcquisitionTarget(TenantModel):
    __tablename__ = "acquisition_targets"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    status = Column(String(40), default="sourced")
    # sourced, screening, dd_active, offer_stage, negotiation, signed, closed, passed, withdrawn
    industry = Column(String(100), nullable=True)
    country = Column(String(100), default="SA")
    strategic_fit_score = Column(Integer, default=0)
    estimated_value_sar = Column(Numeric(16, 2), nullable=True)
    revenue_sar = Column(Numeric(14, 2), nullable=True)
    ebitda_sar = Column(Numeric(14, 2), nullable=True)
    employee_count = Column(Integer, nullable=True)
    ownership_structure = Column(JSONB, default=dict)
    management_team = Column(JSONB, default=dict)
    rationale = Column(Text, nullable=True)
    rationale_ar = Column(Text, nullable=True)
    deal_lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sponsor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    dd_streams = relationship("DDStream", back_populates="target", lazy="dynamic")
    valuations = relationship("ValuationModel", back_populates="target", lazy="dynamic")


class DDStream(TenantModel):
    __tablename__ = "dd_streams"

    target_id = Column(UUID(as_uuid=True), ForeignKey("acquisition_targets.id"), nullable=False, index=True)
    stream_type = Column(String(50), nullable=False)  # legal, financial, product, security, commercial, tax, hr
    status = Column(String(30), default="pending")  # pending, in_progress, completed, blocked, waived
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sla_hours = Column(Integer, default=168)  # 7 days default
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    findings = Column(JSONB, default=dict)
    risk_flags = Column(JSONB, default=list)
    documents_requested = Column(Integer, default=0)
    documents_received = Column(Integer, default=0)
    room_access_granted = Column(Boolean, default=False)

    target = relationship("AcquisitionTarget", back_populates="dd_streams")


class ValuationModel(TenantModel):
    __tablename__ = "valuation_models"

    target_id = Column(UUID(as_uuid=True), ForeignKey("acquisition_targets.id"), nullable=False, index=True)
    method = Column(String(50), nullable=False)  # dcf, comparable, precedent, asset_based, lbo
    low_sar = Column(Numeric(16, 2), nullable=True)
    mid_sar = Column(Numeric(16, 2), nullable=True)
    high_sar = Column(Numeric(16, 2), nullable=True)
    assumptions = Column(JSONB, default=dict)
    synergy_model = Column(JSONB, default=dict)
    prepared_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved = Column(Boolean, default=False)

    target = relationship("AcquisitionTarget", back_populates="valuations")


class InvestmentCommitteePack(TenantModel):
    __tablename__ = "ic_packs"

    target_id = Column(UUID(as_uuid=True), ForeignKey("acquisition_targets.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    status = Column(String(30), default="draft")  # draft, submitted, approved, rejected
    executive_summary = Column(Text, nullable=True)
    executive_summary_ar = Column(Text, nullable=True)
    financial_highlights = Column(JSONB, default=dict)
    risk_assessment = Column(JSONB, default=dict)
    synergy_estimate_sar = Column(Numeric(14, 2), nullable=True)
    recommendation = Column(String(30), nullable=True)  # proceed, pass, defer
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    decision_at = Column(DateTime(timezone=True), nullable=True)
    decision_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
