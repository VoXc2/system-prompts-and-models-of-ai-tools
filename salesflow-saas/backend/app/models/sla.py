from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import TenantModel


class SLAPolicy(TenantModel):
    """SLA policies for pipeline hygiene and response time tracking."""
    __tablename__ = "sla_policies"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    entity_type = Column(String(50), nullable=False, index=True)  # lead, deal, ticket
    stage = Column(String(50), index=True)  # specific stage or null for all
    priority = Column(String(20), default="normal", index=True)  # low, normal, high, urgent

    # Time limits (in minutes)
    first_response_minutes = Column(Integer, default=60)  # max time to first response
    follow_up_minutes = Column(Integer, default=1440)  # max time between follow-ups (24h default)
    stage_max_minutes = Column(Integer)  # max time in a stage before escalation
    resolution_minutes = Column(Integer)  # max time to close/resolve

    # Escalation
    escalation_enabled = Column(Boolean, default=True)
    escalation_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalation_notify_channels = Column(JSONB, default=list)  # ["email", "whatsapp", "notification"]

    # Business hours
    business_hours_only = Column(Boolean, default=True)
    business_hours = Column(JSONB, default=dict)  # {"start": "09:00", "end": "17:00", "timezone": "Asia/Riyadh", "days": [0,1,2,3,6]}

    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SLABreach(TenantModel):
    """Tracks individual SLA breaches for reporting and accountability."""
    __tablename__ = "sla_breaches"

    policy_id = Column(UUID(as_uuid=True), ForeignKey("sla_policies.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    breach_type = Column(String(50), nullable=False, index=True)  # first_response, follow_up, stage_timeout, resolution
    breached_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    exceeded_by_minutes = Column(Integer)  # how many minutes over SLA
    escalated = Column(Boolean, default=False)
    notes = Column(Text)

    policy = relationship("SLAPolicy")
