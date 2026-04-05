"""
Autonomous Upgrade Director — persistent memory for hourly research cycles.

Platform-scoped (no tenant): improves the codebase as a whole.
Does not perform external network scans by default; human/CI attaches findings.
"""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from app.models.compat import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UpgradeDirectorCycle(BaseModel):
    __tablename__ = "upgrade_director_cycles"
    __table_args__ = (Index("ix_ud_cycles_created", "created_at"),)

    # draft | completed | failed
    status = Column(String(20), nullable=False, default="draft", index=True)
    source = Column(String(40), nullable=False, default="hourly_celery")  # hourly_celery | manual | ci
    cycle_started_at = Column(DateTime(timezone=True), nullable=False)
    cycle_completed_at = Column(DateTime(timezone=True), nullable=True)
    # Phases 1–12 condensed: scan, filter, research notes, scores, risk, plan, sandbox, test, decision...
    phases = Column(JSONB, nullable=False, default=dict)
    local_scan_snapshot = Column(JSONB, nullable=True)
    executive_summary = Column(Text, nullable=True)
    machine_summary = Column(JSONB, nullable=True)
    next_cycle_focus = Column(JSONB, nullable=False, default=list)

    candidates = relationship(
        "UpgradeCandidateRecord", back_populates="cycle", cascade="all, delete-orphan"
    )


class UpgradeCandidateRecord(BaseModel):
    __tablename__ = "upgrade_candidate_records"
    __table_args__ = (Index("ix_ud_candidate_cycle", "cycle_id"),)

    cycle_id = Column(
        UUID(as_uuid=True), ForeignKey("upgrade_director_cycles.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(120), nullable=True, index=True)
    version = Column(String(80), nullable=True)
    release_date = Column(String(32), nullable=True)
    official_source = Column(Text, nullable=True)
    # Full machine-readable object (user contract) + extras
    payload = Column(JSONB, nullable=False, default=dict)
    recommended_action = Column(String(32), nullable=False, default="watchlist", index=True)
    weighted_score = Column(String(32), nullable=True)
    confidence = Column(String(32), nullable=True)
    decision_reason = Column(Text, nullable=True)

    cycle = relationship("UpgradeDirectorCycle", back_populates="candidates")
