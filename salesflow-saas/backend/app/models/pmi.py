"""PMI / Strategic PMO OS — Post-merger integration models."""
from __future__ import annotations
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Date
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB, default_uuid, Numeric


class PMIProgram(TenantModel):
    __tablename__ = "pmi_programs"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    source_type = Column(String(30), nullable=False, default="acquisition")  # acquisition, partnership, expansion
    source_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(30), nullable=False, default="planning")  # planning, day1, active, on_track, at_risk, completed, cancelled
    day1_ready = Column(Boolean, default=False)
    plan_30 = Column(JSONB, default=dict)
    plan_60 = Column(JSONB, default=dict)
    plan_90 = Column(JSONB, default=dict)
    synergy_target = Column(Numeric(14, 2), default=0)
    synergy_realized = Column(Numeric(14, 2), default=0)
    risk_register = Column(JSONB, default=list)
    escalations = Column(JSONB, default=list)
    started_at = Column(DateTime(timezone=True), nullable=True)
    target_completion = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    notes_ar = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)


class PMIWorkstream(TenantModel):
    __tablename__ = "pmi_workstreams"

    program_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(30), nullable=False, default="not_started")  # not_started, in_progress, blocked, completed
    priority = Column(Integer, default=0)
    dependencies = Column(JSONB, default=list)
    tasks_total = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    sla_days = Column(Integer, default=30)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    escalation_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
