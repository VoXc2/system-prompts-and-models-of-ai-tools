"""Unified event types and field validation — no transport."""

from __future__ import annotations

from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Stable event type names for platform ingest and internal cards."""

    LEAD_RECEIVED = "lead_received"
    EXTERNAL_SEND_REQUESTED = "external_send_requested"
    PAYMENT_INTENT = "payment_intent"
    WHATSAPP_MESSAGE_REQUESTED = "whatsapp_message_requested"
    REVIEW_REQUIRED = "review_required"
    DRAFT_CREATED = "draft_created"
    # Omni-channel extensions (dotted names) — backward compatible with existing types.
    EMAIL_RECEIVED = "email.received"
    CALENDAR_MEETING_SCHEDULED = "calendar.meeting_scheduled"
    SOCIAL_COMMENT_RECEIVED = "social.comment_received"
    SOCIAL_DM_RECEIVED = "social.dm_received"
    LEAD_FORM_SUBMITTED = "lead.form_submitted"
    PAYMENT_PAID = "payment.paid"
    PAYMENT_FAILED = "payment.failed"
    REVIEW_CREATED = "review.created"
    PARTNER_SUGGESTED = "partner.suggested"
    ACTION_APPROVED = "action.approved"
    ACTION_BLOCKED = "action.blocked"


_REQUIRED: dict[EventType, tuple[str, ...]] = {
    EventType.LEAD_RECEIVED: ("source", "channel_id"),
    EventType.EXTERNAL_SEND_REQUESTED: ("channel_id", "action"),
    EventType.PAYMENT_INTENT: ("amount_halalas", "currency"),
    EventType.WHATSAPP_MESSAGE_REQUESTED: ("intent", "audience"),
    EventType.REVIEW_REQUIRED: ("reason_code",),
    EventType.DRAFT_CREATED: ("draft_kind",),
    EventType.EMAIL_RECEIVED: ("channel_id", "subject_ar"),
    EventType.CALENDAR_MEETING_SCHEDULED: ("channel_id", "title_ar"),
    EventType.SOCIAL_COMMENT_RECEIVED: ("channel_id", "snippet_ar"),
    EventType.SOCIAL_DM_RECEIVED: ("channel_id", "sender_hint"),
    EventType.LEAD_FORM_SUBMITTED: ("source", "channel_id"),
    EventType.PAYMENT_PAID: ("amount_halalas", "currency"),
    EventType.PAYMENT_FAILED: ("amount_halalas", "reason_code"),
    EventType.REVIEW_CREATED: ("channel_id", "rating"),
    EventType.PARTNER_SUGGESTED: ("partner_name_ar", "sector"),
    EventType.ACTION_APPROVED: ("action_id", "actor"),
    EventType.ACTION_BLOCKED: ("action_id", "reason_code"),
}


def validate_event(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Validate ``event_type`` and required keys. Unknown types are rejected
    (forces explicit extension rather than silent typos).
    """
    errors: list[str] = []
    raw_type = payload.get("event_type")
    if not isinstance(raw_type, str) or not raw_type.strip():
        return {"valid": False, "errors": ["event_type_required"], "normalized": None}

    try:
        et = EventType(raw_type.strip())
    except ValueError:
        return {"valid": False, "errors": [f"unknown_event_type:{raw_type}"], "normalized": None}

    for key in _REQUIRED[et]:
        if key not in payload or payload[key] in (None, ""):
            errors.append(f"missing_field:{key}")

    normalized = {"event_type": et.value, **{k: v for k, v in payload.items() if k != "event_type"}}
    normalized["event_type"] = et.value
    return {"valid": len(errors) == 0, "errors": errors, "normalized": normalized if not errors else None}
