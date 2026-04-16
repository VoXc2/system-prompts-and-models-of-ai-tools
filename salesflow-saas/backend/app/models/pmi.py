"""PMI / Strategic PMO OS — post-merger integration models."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class PMIProgram(TenantModel):
    __tablename__ = "pmi_programs"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    source_type = Column(String(40), nullable=False)  # acquisition, partnership, expansion
    source_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(40), default="planning")
    # planning, day1_prep, day1_active, integration, optimization, completed
    day1_ready = Column(Boolean, default=False)
    program_lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    target_completion = Column(DateTime(timezone=True), nullable=True)
    synergy_target_sar = Column(Numeric(14, 2), nullable=True)
    synergy_realized_sar = Column(Numeric(14, 2), default=0)

    workstreams = relationship("PMIWorkstream", back_populates="program", lazy="dynamic")
    risks = relationship("PMIRisk", back_populates="program", lazy="dynamic")
    milestones = relationship("PMIMilestone", back_populates="program", lazy="dynamic")


class PMIWorkstream(TenantModel):
    __tablename__ = "pmi_workstreams"

    program_id = Column(UUID(as_uuid=True), ForeignKey("pmi_programs.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="pending")  # pending, in_progress, completed, blocked
    progress_pct = Column(Integer, default=0)
    dependencies = Column(JSONB, default=list)
    sla_days = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    escalation_count = Column(Integer, default=0)

    program = relationship("PMIProgram", back_populates="workstreams")
    tasks = relationship("PMITask", back_populates="workstream", lazy="dynamic")


class PMITask(TenantModel):
    __tablename__ = "pmi_tasks"

    workstream_id = Column(UUID(as_uuid=True), ForeignKey("pmi_workstreams.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(30), default="pending")  # pending, in_progress, completed, blocked, escalated
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    workstream = relationship("PMIWorkstream", back_populates="tasks")


class PMIMilestone(TenantModel):
    __tablename__ = "pmi_milestones"

    program_id = Column(UUID(as_uuid=True), ForeignKey("pmi_programs.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    milestone_type = Column(String(30), default="30_day")  # day1, 30_day, 60_day, 90_day, custom
    target_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="pending")  # pending, on_track, at_risk, completed, missed

    program = relationship("PMIProgram", back_populates="milestones")


class PMIRisk(TenantModel):
    __tablename__ = "pmi_risks"

    program_id = Column(UUID(as_uuid=True), ForeignKey("pmi_programs.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    probability = Column(String(20), default="medium")  # low, medium, high
    status = Column(String(30), default="open")  # open, mitigating, resolved, accepted
    mitigation = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_sla_hours = Column(Integer, default=72)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    program = relationship("PMIProgram", back_populates="risks")
