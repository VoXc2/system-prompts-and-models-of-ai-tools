"""Durable Checkpoint — persisted workflow state for crash-safe resume.

Replaces the in-memory FlowRevision storage in openclaw/durable_flow.py
with database-backed checkpoints that survive restarts.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import TenantModel


class DurableCheckpoint(TenantModel):
    __tablename__ = "durable_checkpoints"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence_num", name="uq_run_sequence"),
    )

    flow_name = Column(String(120), nullable=False, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    revision_id = Column(String(64), nullable=False)
    sequence_num = Column(Integer, nullable=False, default=0)
    note = Column(Text, nullable=True)
    state = Column(JSONB, default=dict)
    correlation_id = Column(String(64), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running", index=True)  # running, completed, failed
