"""Marketing campaigns and lead source attribution."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class Campaign(TenantModel):
    """Marketing campaign for tracking lead sources and ROI."""
    __tablename__ = "campaigns"

    name = Column(String(255), nullable=False)
    campaign_type = Column(String(50))  # meta_ctwa, linkedin, google_ads, email, whatsapp, referral, manual
    channel = Column(String(50))  # whatsapp, email, linkedin, instagram, google, tiktok
    status = Column(String(50), default="draft", index=True)  # draft, active, paused, completed
    budget = Column(Numeric(12, 2))
    currency = Column(String(3), default="SAR")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    target_industry = Column(String(100))
    target_criteria = Column(JSONB, default=dict)
    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    deals_closed = Column(Integer, default=0)
    revenue_generated = Column(Numeric(12, 2), default=0)
    cost_per_lead = Column(Numeric(10, 2))
    settings = Column(JSONB, default=dict)
    updated_at = Column(DateTime(timezone=True))


class LeadSource(TenantModel):
    """Tracks how each lead was acquired (UTM, campaign, referral)."""
    __tablename__ = "lead_sources"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    source = Column(String(100))  # google, facebook, linkedin, whatsapp, direct, referral
    medium = Column(String(100))  # cpc, organic, social, email, referral
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_content = Column(String(255))
    utm_term = Column(String(255))
    referrer_url = Column(Text)
    landing_page = Column(Text)
