"""Partnership OS — Partner lifecycle management models."""
from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Date
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB, default_uuid, Numeric


class Partner(TenantModel):
    __tablename__ = "partners"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    partner_type = Column(String(50), nullable=False, default="channel")  # channel, strategic, technology, referral
    status = Column(String(30), nullable=False, default="scouted")  # scouted, evaluating, negotiating, active, inactive, terminated
    strategic_fit_score = Column(Integer, default=0)
    channel_economics = Column(JSONB, default=dict)
    alliance_structure = Column(JSONB, default=dict)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    country = Column(String(100), default="Saudi Arabia")
    city = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)
    revenue_share_pct = Column(Numeric(5, 2), nullable=True)
    exclusivity = Column(Boolean, default=False)
    market_commitment = Column(Text, nullable=True)
    contribution_margin = Column(Numeric(14, 2), default=0)
    health_score = Column(Integer, default=0)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    next_review_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)


class PartnerScorecard(TenantModel):
    __tablename__ = "partner_scorecards"

    partner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # "2026-Q1", "2026-04"
    leads_generated = Column(Integer, default=0)
    deals_closed = Column(Integer, default=0)
    revenue_generated = Column(Numeric(14, 2), default=0)
    contribution_margin = Column(Numeric(14, 2), default=0)
    satisfaction_score = Column(Integer, default=0)
    compliance_score = Column(Integer, default=0)
    overall_grade = Column(String(5), default="C")  # A+, A, B, C, D, F
    notes = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
