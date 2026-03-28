"""External integrations and webhook events."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class IntegrationAccount(TenantModel):
    """Connected external service account."""
    __tablename__ = "integration_accounts"

    provider = Column(String(100), nullable=False)  # meta, google, linkedin, apollo, hunter, vapi, sendgrid
    account_name = Column(String(255))
    account_id = Column(String(255))
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    token_expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    scopes = Column(JSONB, default=list)
    settings = Column(JSONB, default=dict)
    last_synced_at = Column(DateTime(timezone=True))


class WebhookEvent(TenantModel):
    """Log of incoming webhook events."""
    __tablename__ = "webhook_events"

    source = Column(String(100), nullable=False)  # whatsapp, meta, stripe, vapi
    event_type = Column(String(255))
    payload = Column(JSONB)
    status = Column(String(50), default="received")  # received, processing, processed, failed
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
