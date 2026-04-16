"""M&A / Corporate Development OS — Acquisition lifecycle models."""
from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Date
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB, default_uuid, Numeric


class AcquisitionTarget(TenantModel):
    __tablename__ = "acquisition_targets"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False, default="sourced")  # sourced, screening, dd_active, valuation, negotiation, offer_sent, closing, closed, abandoned
    strategic_fit_score = Column(Integer, default=0)
    sector = Column(String(100), nullable=True)
    country = Column(String(100), default="Saudi Arabia")
    city = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    annual_revenue = Column(Numeric(14, 2), nullable=True)
    employee_count = Column(Integer, nullable=True)
    ownership_structure = Column(JSONB, default=dict)
    management_team = Column(JSONB, default=dict)
    valuation_range_low = Column(Numeric(14, 2), nullable=True)
    valuation_range_high = Column(Numeric(14, 2), nullable=True)
    synergy_model = Column(JSONB, default=dict)
    offer_amount = Column(Numeric(14, 2), nullable=True)
    dd_status = Column(JSONB, default=dict)  # {"legal": "complete", "financial": "in_progress", ...}
    dd_room_url = Column(String(500), nullable=True)
    investment_committee_approved = Column(Boolean, default=False)
    board_approved = Column(Boolean, default=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    post_close_pmi_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)


class DueDiligenceStream(TenantModel):
    __tablename__ = "dd_streams"

    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    stream_type = Column(String(50), nullable=False)  # legal, financial, product, security, tax, hr, ip
    status = Column(String(30), nullable=False, default="not_started")  # not_started, in_progress, review, complete, flagged
    assigned_to = Column(UUID(as_uuid=True), nullable=True)
    findings = Column(JSONB, default=dict)
    risk_flags = Column(JSONB, default=list)
    documents_requested = Column(Integer, default=0)
    documents_received = Column(Integer, default=0)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
