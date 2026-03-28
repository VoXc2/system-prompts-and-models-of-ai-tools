"""
AI Agent models - Tracks agent configurations, campaigns, and conversations.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class AIAgent(TenantModel):
    """AI Sales Agent configuration per tenant."""
    __tablename__ = "ai_agents"

    name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)  # sales, discovery, support, qualifier
    industry = Column(String(100))
    personality = Column(Text)  # Custom personality/system prompt override
    is_active = Column(Boolean, default=True)
    auto_reply = Column(Boolean, default=True)  # Auto-reply to incoming messages
    auto_discover = Column(Boolean, default=False)  # Auto-discover leads
    auto_outreach = Column(Boolean, default=False)  # Auto-send outreach
    max_messages_per_day = Column(Integer, default=100)
    messages_sent_today = Column(Integer, default=0)
    total_messages_sent = Column(Integer, default=0)
    total_leads_discovered = Column(Integer, default=0)
    total_deals_closed = Column(Integer, default=0)
    settings = Column(JSONB, default=dict)
    # AI provider settings
    ai_provider = Column(String(50), default="openai")  # openai, anthropic
    ai_model = Column(String(100), default="gpt-4o-mini")

    campaigns = relationship("OutreachCampaign", back_populates="agent")


class OutreachCampaign(TenantModel):
    """Automated outreach campaign."""
    __tablename__ = "outreach_campaigns"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=False)
    name = Column(String(255), nullable=False)
    campaign_type = Column(String(50), default="cold_outreach")  # cold_outreach, warm_followup, reactivation
    industry = Column(String(100))
    channel = Column(String(50), default="whatsapp")  # whatsapp, email, sms
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    target_criteria = Column(JSONB, default=dict)  # Filters for target leads
    sequence = Column(JSONB, default=list)  # Array of message steps
    total_leads = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    leads_converted = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    settings = Column(JSONB, default=dict)

    agent = relationship("AIAgent", back_populates="campaigns")


class AIConversation(TenantModel):
    """AI-managed conversation with a lead/customer."""
    __tablename__ = "ai_conversations"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=True)
    channel = Column(String(50), default="whatsapp")
    status = Column(String(50), default="active")  # active, paused, escalated, closed
    sentiment = Column(String(50))  # positive, negative, neutral
    intent = Column(String(100))  # inquiry, interested, ready_to_buy, etc.
    lead_score = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True))
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalation_reason = Column(Text)
    ai_summary = Column(Text)  # AI-generated conversation summary
    extra_data = Column("metadata", JSONB, default=dict)


class DiscoveredLead(TenantModel):
    """Lead discovered by AI agents from external sources."""
    __tablename__ = "discovered_leads"

    name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    source = Column(String(100))  # google_maps, instagram, twitter, directory, ai_generated
    source_url = Column(Text)
    business_name = Column(String(255))
    business_type = Column(String(100))
    industry = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    rating = Column(Numeric(3, 2))
    ai_score = Column(Integer, default=50)
    ai_priority = Column(String(20), default="medium")  # low, medium, high, urgent
    ai_notes = Column(Text)
    status = Column(String(50), default="new")  # new, contacted, converted, rejected
    converted_lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    extra_data = Column("metadata", JSONB, default=dict)
