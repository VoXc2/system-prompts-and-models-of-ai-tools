"""Sovereign PMI: post-merger integration programs and tasks."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class PMIProgram(TenantModel):
    __tablename__ = "pmi_programs"

    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    ma_target_id = Column(UUID(as_uuid=True), ForeignKey("ma_targets.id"), nullable=True, index=True)
    status = Column(String(30), nullable=False, default="planning", index=True)
    day1_readiness = Column(JSONB, nullable=True)
    integration_plan_30 = Column(JSONB, nullable=True)
    integration_plan_60 = Column(JSONB, nullable=True)
    integration_plan_90 = Column(JSONB, nullable=True)
    synergy_realization = Column(JSONB, nullable=True)
    risk_register = Column(JSONB, nullable=True)
    escalation_rules = Column(JSONB, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    ma_target = relationship("MATarget", foreign_keys=[ma_target_id], back_populates="pmi_programs")
    owner = relationship("User", foreign_keys=[owner_id])
    tasks = relationship("PMITask", back_populates="program")


class PMITask(TenantModel):
    __tablename__ = "pmi_tasks"

    program_id = Column(UUID(as_uuid=True), ForeignKey("pmi_programs.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    priority = Column(String(20), nullable=False, default="medium")
    phase = Column(String(20), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    depends_on = Column(JSONB, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    program = relationship("PMIProgram", foreign_keys=[program_id], back_populates="tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
