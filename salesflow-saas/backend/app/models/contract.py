"""Contracts and digital signatures."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.models.base import TenantModel


class Contract(TenantModel):
    """Client contract / agreement."""
    __tablename__ = "contracts"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(100))  # msa, sow, nda, subscription, service_agreement
    content = Column(Text)  # HTML/Markdown content
    template_id = Column(String(255))
    total_value = Column(Numeric(14, 2))
    currency = Column(String(3), default="SAR")
    status = Column(String(50), default="draft")  # draft, sent, viewed, signed, expired, cancelled
    sent_at = Column(DateTime(timezone=True))
    viewed_at = Column(DateTime(timezone=True))
    signed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    public_url = Column(Text)  # Public link for client to view/sign
    extra_data = Column("metadata", JSONB, default=dict)


class Signature(TenantModel):
    """Digital signature on a contract."""
    __tablename__ = "signatures"

    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255))
    signer_phone = Column(String(20))
    signer_title = Column(String(255))  # CEO, Manager, etc.
    signer_type = Column(String(50))  # client, company
    signature_data = Column(Text)  # Base64 image or signature hash
    ip_address = Column(INET)
    signed_at = Column(DateTime(timezone=True))
    extra_data = Column("metadata", JSONB, default=dict)
