"""Sovereign Decision Plane: AI recommendations and contradiction tracking."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class AIRecommendation(TenantModel):
    __tablename__ = "ai_recommendations"

    recommendation_type = Column(String(80), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    summary = Column(Text, nullable=False)
    summary_ar = Column(Text, nullable=True)
    evidence_sources = Column(JSONB, default=list)
    assumptions = Column(JSONB, default=list)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    freshness_at = Column(DateTime(timezone=True), nullable=True)
    model_version = Column(String(100), nullable=False)
    model_lane = Column(String(50), nullable=False)
    policy_notes = Column(Text, nullable=True)
    alternatives = Column(JSONB, nullable=True)
    status = Column(String(30), nullable=False, default="draft", index=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    target_entity_type = Column(String(80), nullable=False, index=True)
    target_entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    provenance_chain = Column(JSONB, nullable=True)

    approved_by = relationship("User", foreign_keys=[approved_by_id])
    contradictions = relationship("ContradictionRecord", back_populates="recommendation")


class ContradictionRecord(TenantModel):
    __tablename__ = "contradiction_records"

    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("ai_recommendations.id"), nullable=True, index=True)
    intended_action = Column(Text, nullable=False)
    claimed_action = Column(Text, nullable=False)
    actual_tool_call = Column(Text, nullable=True)
    side_effects = Column(JSONB, nullable=True)
    contradiction_status = Column(String(30), nullable=False, default="none")
    resolution_notes = Column(Text, nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    recommendation = relationship("AIRecommendation", foreign_keys=[recommendation_id], back_populates="contradictions")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
