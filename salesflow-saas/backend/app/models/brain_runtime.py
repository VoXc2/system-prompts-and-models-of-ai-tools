"""Runtime tables for Brain OS — agent sessions and skill invocations (observable state)."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Integer
from app.models.compat import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


class BrainAgentSession(TenantModel):
    __tablename__ = "brain_agent_sessions"
    __table_args__ = (
        Index("ix_brain_session_tenant_agent", "tenant_id", "agent_key"),
        Index("ix_brain_session_corr", "tenant_id", "correlation_id"),
    )

    agent_key = Column(String(80), nullable=False, index=True)
    state = Column(String(20), nullable=False, default="running", index=True)
    correlation_id = Column(String(80), nullable=True, index=True)
    input_payload = Column(JSONB, nullable=False, default=dict)
    output_payload = Column(JSONB, nullable=True)
    error_text = Column(Text, nullable=True)
    heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    invocations = relationship("BrainSkillInvocation", back_populates="session", cascade="all, delete-orphan")


class BrainSkillInvocation(TenantModel):
    __tablename__ = "brain_skill_invocations"
    __table_args__ = (Index("ix_brain_skill_session", "tenant_id", "session_id"),)

    session_id = Column(
        UUID(as_uuid=True), ForeignKey("brain_agent_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_key = Column(String(80), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    attempts = Column(Integer, nullable=False, default=1)
    result = Column(JSONB, nullable=False, default=dict)
    error = Column(Text, nullable=True)

    session = relationship("BrainAgentSession", back_populates="invocations")
