"""Suppression list — contacts who must not be contacted."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TenantModel


class SuppressionEntry(TenantModel):
    """A contact on the do-not-contact list."""
    __tablename__ = "suppression_list"

    contact_phone = Column(String(20), index=True)
    contact_email = Column(String(255), index=True)
    channel = Column(String(50), nullable=False, index=True)  # whatsapp, email, sms, all
    reason = Column(String(100), nullable=False)  # opt_out, complaint, bounced, manual, legal
    source = Column(String(100))  # user_request, system, admin, webhook
    suppressed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    suppressed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
