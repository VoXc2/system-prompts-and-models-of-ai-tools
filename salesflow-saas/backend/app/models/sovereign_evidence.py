"""Sovereign Evidence: assembled evidence packs for decisions."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class EvidencePack(TenantModel):
    __tablename__ = "evidence_packs"

    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    pack_type = Column(String(80), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="assembling", index=True)
    entity_type = Column(String(80), nullable=True, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    sources = Column(JSONB, nullable=False)
    assumptions = Column(JSONB, nullable=True)
    financial_model_version = Column(String(50), nullable=True)
    policy_notes = Column(Text, nullable=True)
    alternatives = Column(JSONB, nullable=True)
    rollback_plan = Column(Text, nullable=True)
    approval_class = Column(String(30), nullable=True)
    reversibility_class = Column(String(30), nullable=True)
    sensitivity = Column(String(30), nullable=False, default="internal")
    assembled_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    assembled_by = relationship("User", foreign_keys=[assembled_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
