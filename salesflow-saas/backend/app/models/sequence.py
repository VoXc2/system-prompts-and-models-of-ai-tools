"""Sales sequences - automated multi-step follow-up workflows."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class Sequence(TenantModel):
    """A multi-step automated sales sequence."""
    __tablename__ = "sequences"

    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    channel = Column(String(50), default="whatsapp")  # whatsapp, email, multi
    status = Column(String(50), default="active")  # draft, active, paused, archived
    total_steps = Column(Integer, default=0)
    total_enrolled = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    settings = Column(JSONB, default=dict)


class SequenceStep(TenantModel):
    """Individual step in a sales sequence."""
    __tablename__ = "sequence_steps"

    sequence_id = Column(UUID(as_uuid=True), ForeignKey("sequences.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)  # send_whatsapp, send_email, create_task, update_status, wait, ai_reply
    delay_days = Column(Integer, default=0)
    delay_hours = Column(Integer, default=0)
    channel = Column(String(50))  # whatsapp, email, sms
    template_name = Column(String(255))
    message_content = Column(Text)
    ai_generated = Column(Boolean, default=False)  # AI generates message dynamically
    settings = Column(JSONB, default=dict)


class SequenceEnrollment(TenantModel):
    """A lead enrolled in a sequence."""
    __tablename__ = "sequence_enrollments"

    sequence_id = Column(UUID(as_uuid=True), ForeignKey("sequences.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    current_step = Column(Integer, default=0)
    status = Column(String(50), default="active")  # active, paused, completed, replied, converted, bounced
    enrolled_at = Column(DateTime(timezone=True))
    next_step_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    reply_received = Column(Boolean, default=False)
    extra_data = Column("metadata", JSONB, default=dict)
