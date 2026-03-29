"""Voice AI call logs and sessions."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class CallLog(TenantModel):
    """Record of a phone call (voice AI or manual)."""
    __tablename__ = "call_logs"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    direction = Column(String(10), nullable=False)  # inbound, outbound
    caller_number = Column(String(20))
    callee_number = Column(String(20))
    status = Column(String(50), index=True)  # ringing, answered, missed, voicemail, completed, failed
    duration_seconds = Column(Integer)
    is_ai_call = Column(Boolean, default=False)
    ai_agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=True)
    transcript = Column(Text)
    ai_summary = Column(Text)
    sentiment = Column(String(50))
    disposition = Column(String(100))  # interested, not_interested, callback, booked_demo, wrong_number
    recording_url = Column(Text)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    extra_data = Column("metadata", JSONB, default=dict)


class VoiceSession(TenantModel):
    """Voice AI session tracking."""
    __tablename__ = "voice_sessions"
    __table_args__ = (
        UniqueConstraint("provider", "external_session_id", name="uq_voice_session_provider_external_id"),
        {"extend_existing": True},
    )

    call_log_id = Column(UUID(as_uuid=True), ForeignKey("call_logs.id"), nullable=True)
    ai_agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=True)
    provider = Column(String(50))  # vapi, retell
    external_session_id = Column(String(255), index=True)
    status = Column(String(50), default="active", index=True)  # active, completed, failed, transferred
    language = Column(String(10), default="ar")
    handoff_to_user = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    handoff_reason = Column(Text)
    turns_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost = Column(Numeric(10, 4))
    extra_data = Column("metadata", JSONB, default=dict)
