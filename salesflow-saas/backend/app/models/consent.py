"""PDPL consent management and compliance."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.models.base import TenantModel


class Consent(TenantModel):
    """Records consent given by a contact (PDPL compliance)."""
    __tablename__ = "consents"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    consent_type = Column(String(100), nullable=False)  # marketing_whatsapp, marketing_email, marketing_sms, data_processing, call_recording
    status = Column(String(50), default="granted")  # granted, revoked
    granted_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    source = Column(String(100))  # web_form, whatsapp_optin, manual, api, ctwa_ad
    ip_address = Column(INET)
    legal_basis = Column(String(100))  # consent, contract, legal_obligation, legitimate_interest
    privacy_notice_version = Column(String(50))
    extra_data = Column("metadata", JSONB, default=dict)
