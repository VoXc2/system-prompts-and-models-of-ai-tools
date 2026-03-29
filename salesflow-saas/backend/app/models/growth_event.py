"""Growth attribution events — tracks every touchpoint in the customer journey."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.models.base import TenantModel


class GrowthEvent(TenantModel):
    """A single touchpoint in the customer journey (for multi-touch attribution)."""
    __tablename__ = "growth_events"

    # Who
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    anonymous_id = Column(String(255), index=True)  # Before lead is identified

    # What
    event_type = Column(String(100), nullable=False, index=True)  # page_view, form_submit, cta_click, demo_booked, deal_created, deal_won
    event_category = Column(String(50), index=True)  # awareness, consideration, decision, retention

    # Where from
    source = Column(String(100), index=True)  # google, linkedin, whatsapp, direct, referral
    medium = Column(String(100))  # organic, cpc, social, email, referral
    campaign = Column(String(255))
    content = Column(String(255))  # ad variant, CTA variant
    term = Column(String(255))  # search term

    # UTM tracking
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_content = Column(String(255))
    utm_term = Column(String(255))

    # Context
    page_url = Column(Text)
    referrer_url = Column(Text)
    landing_page = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    device_type = Column(String(50))  # mobile, desktop, tablet
    country = Column(String(10))
    city = Column(String(100))

    # Value
    revenue_attributed = Column(Numeric(12, 2), default=0)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True, index=True)

    # Engagement
    session_id = Column(String(255))
    duration_seconds = Column(Integer)

    extra_data = Column("metadata", JSONB, default=dict)
