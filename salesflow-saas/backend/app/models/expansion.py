"""Expansion OS — Market expansion lifecycle models."""
from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Date
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB, default_uuid, Numeric


class ExpansionMarket(TenantModel):
    __tablename__ = "expansion_markets"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False, default="scanning")  # scanning, prioritized, assessment, planning, approved, canary, live, paused, exited
    segment_priority = Column(Integer, default=0)
    regulatory_readiness = Column(JSONB, default=dict)
    pricing_strategy = Column(JSONB, default=dict)
    channel_strategy = Column(JSONB, default=dict)
    gtm_plan = Column(JSONB, default=dict)
    launch_readiness_score = Column(Integer, default=0)
    canary_metrics = Column(JSONB, default=dict)
    stop_loss_threshold = Column(Numeric(14, 2), nullable=True)
    partner_assisted = Column(Boolean, default=False)
    partner_id = Column(UUID(as_uuid=True), nullable=True)
    launch_date = Column(Date, nullable=True)
    post_launch_analytics = Column(JSONB, default=dict)
    investment_amount = Column(Numeric(14, 2), default=0)
    revenue_to_date = Column(Numeric(14, 2), default=0)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
