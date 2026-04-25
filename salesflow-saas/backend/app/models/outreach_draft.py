"""OutreachDraft — DB-persisted draft queue for all outreach channels.

Every generated message starts as status='draft'. Sami reviews and
approves before any send. Approved drafts are dispatched via existing
Celery send tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

try:
    from app.database import Base
except ImportError:
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(String(64), index=True)
    company = Column(String(255), nullable=False)
    contact_name = Column(String(255), default="")
    contact_email = Column(String(255), default="")
    contact_phone = Column(String(32), default="")
    channel = Column(String(20), nullable=False)  # email | whatsapp | sms | linkedin
    subject = Column(String(500), default="")
    body = Column(Text, nullable=False)
    followup_2d = Column(Text, default="")
    followup_5d = Column(Text, default="")
    call_script = Column(Text, default="")
    sector = Column(String(100), default="")
    city = Column(String(100), default="")
    pain_hypothesis = Column(Text, default="")
    fit_score = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    status = Column(String(20), default="draft", index=True)
    # draft | approved | sent | replied | opted_out | bounced | skipped
    approval_required = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    approved_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    reply_text = Column(Text, nullable=True)
    reply_category = Column(String(50), nullable=True)
    next_action = Column(String(100), nullable=True)
    source = Column(String(100), default="daily_pipeline")
    metadata_ = Column("metadata", JSON, default=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "batch_id": self.batch_id,
            "company": self.company,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "channel": self.channel,
            "subject": self.subject,
            "body": self.body[:200] + "..." if len(self.body or "") > 200 else self.body,
            "sector": self.sector,
            "city": self.city,
            "fit_score": self.fit_score,
            "risk_score": self.risk_score,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "reply_category": self.reply_category,
            "next_action": self.next_action,
        }
