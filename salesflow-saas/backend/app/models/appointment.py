"""Appointment/booking model for Dealix CRM."""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class Appointment(TenantModel):
    """Appointment booking — core feature for salons, clinics, and service businesses."""
    __tablename__ = "appointments"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Booking details
    title = Column(String(255))
    service_type = Column(String(100))  # haircut, consultation, checkup, demo, etc.
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, default=30)

    # Status workflow
    status = Column(String(50), default="pending", index=True)
    # pending -> confirmed -> completed
    # pending -> cancelled
    # confirmed -> no_show

    # Source tracking
    booked_via = Column(String(50))  # voice_ai, whatsapp, web_form, manual, api

    # Contact info (for walk-ins or when no lead exists)
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))

    # Location
    location = Column(String(255))
    notes = Column(Text)

    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_24h_sent = Column(Boolean, default=False)
    reminder_1h_sent = Column(Boolean, default=False)

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100))  # weekly, biweekly, monthly

    extra_data = Column("metadata", JSONB, default=dict)

    # Relationships
    lead = relationship("Lead", backref="appointments")
    customer = relationship("Customer", backref="appointments")
    assigned_user = relationship("User", backref="assigned_appointments", foreign_keys=[assigned_to])
