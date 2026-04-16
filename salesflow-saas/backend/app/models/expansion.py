"""Expansion OS — market expansion lifecycle models."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class ExpansionMarket(TenantModel):
    __tablename__ = "expansion_markets"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    status = Column(String(40), default="scanning")
    # scanning, evaluating, approved, preparing, launched, active, stop_loss, withdrawn
    segment = Column(String(100), nullable=True)
    priority_score = Column(Integer, default=0)
    regulatory_readiness = Column(String(30), default="unknown")  # ready, partial, blocked, unknown
    regulatory_notes = Column(Text, nullable=True)
    market_size_sar = Column(Numeric(16, 2), nullable=True)
    pricing_strategy = Column(JSONB, default=dict)
    channel_strategy = Column(JSONB, default=dict)
    gtm_plan = Column(JSONB, default=dict)
    localization_status = Column(String(30), default="pending")  # pending, in_progress, completed
    launch_readiness_pct = Column(Integer, default=0)
    stop_loss_threshold = Column(JSONB, default=dict)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sponsor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    launched_at = Column(DateTime(timezone=True), nullable=True)
    canary_started_at = Column(DateTime(timezone=True), nullable=True)
    partner_assisted = Column(Boolean, default=False)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=True)
    post_launch_metrics = Column(JSONB, default=dict)
