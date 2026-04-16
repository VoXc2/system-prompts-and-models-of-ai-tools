"""Sovereign evidence packs and line items."""

from sqlalchemy import Column, String, Text, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class SovereignEvidencePack(TenantModel):
    __tablename__ = "sovereign_evidence_packs"

    track = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    assumptions = Column(JSONB, default=list)
    assumptions_ar = Column(JSONB, default=list)
    policy_notes = Column(JSONB, default=list)
    alternatives = Column(JSONB, default=list)
    financial_model_version = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="draft")

    items = relationship(
        "SovereignEvidenceItem",
        back_populates="pack",
        cascade="all, delete-orphan",
    )


class SovereignEvidenceItem(TenantModel):
    __tablename__ = "sovereign_evidence_items"

    pack_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sovereign_evidence_packs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    source = Column(String(500), nullable=False)
    content_summary = Column(Text, nullable=False)
    content_summary_ar = Column(Text, nullable=False)
    provenance_source = Column(String(500), nullable=False)
    provenance_confidence = Column(Float, nullable=False)
    provenance_freshness_seconds = Column(Integer, nullable=False)
    provenance_model_version = Column(String(100), nullable=False)

    pack = relationship("SovereignEvidencePack", back_populates="items")
