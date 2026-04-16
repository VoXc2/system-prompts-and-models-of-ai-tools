"""Partnership OS — full partner lifecycle models."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class Partner(TenantModel):
    __tablename__ = "partners"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    partner_type = Column(String(50), nullable=False, default="channel")  # channel, strategic, technology, referral
    status = Column(String(40), nullable=False, default="prospect")  # prospect, evaluating, active, suspended, churned
    strategic_fit_score = Column(Integer, default=0)
    tier = Column(String(20), default="standard")  # standard, silver, gold, platinum
    website = Column(String(500), nullable=True)
    country = Column(String(100), default="SA")
    industry = Column(String(100), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    channel_economics = Column(JSONB, default=dict)
    alliance_structure = Column(JSONB, default=dict)
    notes = Column(Text, nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    sponsor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    scorecards = relationship("PartnerScorecard", back_populates="partner", lazy="dynamic")
    terms = relationship("PartnerTermSheet", back_populates="partner", lazy="dynamic")


class PartnerScorecard(TenantModel):
    __tablename__ = "partner_scorecards"

    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # 2026-Q1, 2026-M04
    revenue_generated_sar = Column(Numeric(14, 2), default=0)
    leads_referred = Column(Integer, default=0)
    deals_closed = Column(Integer, default=0)
    contribution_margin_pct = Column(Numeric(5, 2), default=0)
    satisfaction_score = Column(Integer, default=0)
    health_status = Column(String(30), default="healthy")  # healthy, at_risk, critical
    metrics = Column(JSONB, default=dict)

    partner = relationship("Partner", back_populates="scorecards")


class PartnerTermSheet(TenantModel):
    __tablename__ = "partner_term_sheets"

    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    status = Column(String(30), default="draft")  # draft, pending_approval, approved, signed, expired
    rev_share_pct = Column(Numeric(5, 2), nullable=True)
    exclusivity = Column(Boolean, default=False)
    territory = Column(String(255), nullable=True)
    term_months = Column(Integer, default=12)
    terms_data = Column(JSONB, default=dict)
    approval_class = Column(String(30), default="director")
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    partner = relationship("Partner", back_populates="terms")
