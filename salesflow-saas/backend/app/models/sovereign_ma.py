"""Sovereign M&A: acquisition target tracking."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class MATarget(TenantModel):
    __tablename__ = "ma_targets"

    company_name = Column(String(255), nullable=False)
    company_name_ar = Column(String(255), nullable=True)
    sector = Column(String(120), nullable=True, index=True)
    status = Column(String(30), nullable=False, default="sourced", index=True)
    valuation_low = Column(Numeric(15, 2), nullable=True)
    valuation_high = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="SAR")
    synergy_model = Column(JSONB, nullable=True)
    dd_room_access = Column(JSONB, nullable=True)
    investment_memo_url = Column(String(1000), nullable=True)
    board_pack_url = Column(String(1000), nullable=True)
    offer_strategy = Column(JSONB, nullable=True)
    signing_readiness = Column(Boolean, default=False)
    close_readiness = Column(Boolean, default=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    pmi_programs = relationship("PMIProgram", back_populates="ma_target")
