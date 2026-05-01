"""
Omni-Channel Event Bus — every channel emits typed events here.

Pure structures + helpers; the actual transport (Redis/Kafka) lives in a
production adapter. This module is testable in isolation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Event taxonomy ────────────────────────────────────────────────
EVENT_TYPES: tuple[str, ...] = (
    # WhatsApp
    "whatsapp.message_received",
    "whatsapp.message_sent",
    "whatsapp.opt_out",
    # Email (Gmail or company SMTP)
    "email.received",
    "email.draft_created",
    "email.sent",
    # Calendar
    "calendar.meeting_scheduled",
    "calendar.meeting_held",
    "calendar.no_show",
    # Social (X / LinkedIn / Instagram / Facebook)
    "social.comment_received",
    "social.dm_received",
    "social.mention_received",
    "social.lead_form_submitted",
    # Website + CRM
    "lead.form_submitted",
    "lead.crm_imported",
    # Payments (Moyasar)
    "payment.initiated",
    "payment.paid",
    "payment.failed",
    "payment.refunded",
    # Reviews / reputation (Google Business Profile)
    "review.created",
    "review.replied",
    # Partners
    "partner.suggested",
    "partner.intro_made",
    # Internal lifecycle
    "action.requested",
    "action.approved",
    "action.rejected",
    "action.executed",
    "action.blocked",
    # Sheets / CRM sync
    "sheet.row_added",
    "crm.deal_updated",
)


# ── Event envelope ────────────────────────────────────────────────
@dataclass(frozen=True)
class PlatformEvent:
    """Immutable platform event."""

    event_id: str
    event_type: str
    channel: str             # whatsapp / gmail / google_calendar / x / ...
    customer_id: str
    occurred_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    actor: str = "system"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "channel": self.channel,
            "customer_id": self.customer_id,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "actor": self.actor,
        }


def make_event(
    *,
    event_type: str,
    channel: str,
    customer_id: str,
    payload: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    actor: str = "system",
    occurred_at: datetime | None = None,
) -> PlatformEvent:
    """Construct a validated event."""
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event_type: {event_type}")
    return PlatformEvent(
        event_id=f"pevt_{uuid.uuid4().hex[:24]}",
        event_type=event_type,
        channel=channel,
        customer_id=customer_id,
        occurred_at=occurred_at or datetime.now(timezone.utc).replace(tzinfo=None),
        payload=payload or {},
        correlation_id=correlation_id,
        actor=actor,
    )
