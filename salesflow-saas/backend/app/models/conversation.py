"""Unified conversation inbox - all channels in one thread."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import TenantModel


class Conversation(TenantModel):
    """A conversation thread with a lead/customer across any channel."""
    __tablename__ = "conversations"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    channel = Column(String(50), nullable=False)  # whatsapp, email, sms, phone, web_form
    status = Column(String(50), default="open", index=True)  # open, waiting, resolved, closed
    subject = Column(String(500))
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    messages_count = Column(Integer, default=0)
    unread_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True))
    last_message_preview = Column(String(500))
    sentiment = Column(String(50))  # positive, neutral, negative
    ai_summary = Column(Text)
    tags = Column(JSONB, default=list)
    is_ai_managed = Column(Boolean, default=False)
    extra_data = Column("metadata", JSONB, default=dict)
    updated_at = Column(DateTime(timezone=True))

    messages = relationship("ConversationMessage", back_populates="conversation", order_by="ConversationMessage.created_at")


class ConversationMessage(TenantModel):
    """Individual message within a conversation."""
    __tablename__ = "conversation_messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(20), nullable=False)  # user, contact, ai, system
    sender_id = Column(UUID(as_uuid=True), nullable=True)  # user_id if from team member
    channel = Column(String(50))  # whatsapp, email, sms
    direction = Column(String(10), nullable=False)  # inbound, outbound
    content_type = Column(String(50), default="text")  # text, image, document, template, audio
    content = Column(Text)
    status = Column(String(50), default="sent", index=True)  # pending, sent, delivered, read, failed
    external_id = Column(String(255))  # WhatsApp message ID, email ID, etc.
    extra_data = Column("metadata", JSONB, default=dict)

    conversation = relationship("Conversation", back_populates="messages")
