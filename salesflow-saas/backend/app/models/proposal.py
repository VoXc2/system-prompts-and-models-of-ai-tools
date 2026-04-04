from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Numeric
from app.models.compat import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class Proposal(TenantModel):
    __tablename__ = "proposals"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    title = Column(String(255))
    content = Column(JSONB, nullable=False)
    total_amount = Column(Numeric(12, 2))
    currency = Column(String(3), default="SAR")
    status = Column(String(50), default="draft")  # draft, sent, viewed, accepted, rejected
    valid_until = Column(Date)
    sent_at = Column(DateTime(timezone=True))
    viewed_at = Column(DateTime(timezone=True))

    deal = relationship("Deal", back_populates="proposals")
    lead = relationship("Lead")
