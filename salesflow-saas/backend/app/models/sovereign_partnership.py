"""Sovereign Partnership: strategic partner management."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Numeric

from app.models.base import TenantModel
from app.models.compat import JSONB


class Partner(TenantModel):
    __tablename__ = "partners"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    partner_type = Column(String(80), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="prospect", index=True)
    strategic_fit_score = Column(Numeric(5, 2), nullable=True)
    channel_economics = Column(JSONB, nullable=True)
    contribution_margin = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="SAR")
    alliance_structure = Column(String(80), nullable=True)
    term_sheet_url = Column(String(1000), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    scorecard_data = Column(JSONB, nullable=True)
