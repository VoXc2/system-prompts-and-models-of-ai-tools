"""Sovereign Expansion: market expansion tracking."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class ExpansionMarket(TenantModel):
    __tablename__ = "expansion_markets"

    market_name = Column(String(255), nullable=False)
    market_name_ar = Column(String(255), nullable=True)
    country_code = Column(String(3), nullable=False, index=True)
    region = Column(String(120), nullable=True)
    status = Column(String(30), nullable=False, default="scanning", index=True)
    priority_score = Column(Numeric(5, 2), nullable=True)
    compliance_readiness = Column(JSONB, nullable=True)
    localization_status = Column(JSONB, nullable=True)
    pricing_plan = Column(JSONB, nullable=True)
    channel_plan = Column(JSONB, nullable=True)
    launch_date = Column(DateTime(timezone=True), nullable=True)
    stop_loss_threshold = Column(Numeric(12, 2), nullable=True)
    actual_vs_forecast = Column(JSONB, nullable=True)
    currency = Column(String(3), default="SAR")
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
