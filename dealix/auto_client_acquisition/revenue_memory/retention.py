"""
Retention policy — PDPL-compliant data lifecycle for the event store.

Saudi PDPL requires retention to be limited to what's necessary for the
declared purpose. We separate events into 3 retention tiers:

  - operational (90 days)   — high-volume signals, opens, clicks
  - business_record (3y)    — leads, deals, customer events
  - legal_hold (7y)         — compliance events (consent, opt-out, DSR)

`apply_retention()` is the function the cron runs daily. It NEVER deletes
legal_hold events. Operational events get tombstoned (replaced with a
minimal stub event) — preserving the audit trail without keeping raw payload.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from auto_client_acquisition.revenue_memory.events import RevenueEvent

OPERATIONAL_TYPES: tuple[str, ...] = (
    "message.opened",
    "message.clicked",
    "signal.detected",
    "signal.expired",
)
LEGAL_HOLD_TYPES: tuple[str, ...] = (
    "compliance.consent_recorded",
    "compliance.opt_out_received",
    "compliance.dsr_received",
    "compliance.dsr_completed",
    "compliance.blocked",
)
RETENTION_DAYS_OPERATIONAL = 90
RETENTION_DAYS_BUSINESS = 365 * 3
RETENTION_DAYS_LEGAL = 365 * 7


def classify_retention_tier(event_type: str) -> str:
    if event_type in LEGAL_HOLD_TYPES:
        return "legal_hold"
    if event_type in OPERATIONAL_TYPES:
        return "operational"
    return "business_record"


def is_expired(event: RevenueEvent, *, now: datetime) -> bool:
    """Whether the event has passed its retention window.

    Legal-hold events never expire — PDPL Article on lawful basis records
    requires indefinite retention for opt-outs / consents / DSR receipts.
    """
    tier = classify_retention_tier(event.event_type)
    if tier == "legal_hold":
        return False  # never expires — preserves the audit trail forever
    if tier == "operational":
        days = RETENTION_DAYS_OPERATIONAL
    else:
        days = RETENTION_DAYS_BUSINESS
    return (now - event.occurred_at).days > days


def tombstone_event(event: RevenueEvent) -> RevenueEvent:
    """Strip payload, keep envelope — preserves audit trail without PII."""
    return RevenueEvent(
        event_id=event.event_id,
        event_type=f"{event.event_type}.tombstoned",
        customer_id=event.customer_id,
        occurred_at=event.occurred_at,
        subject_type=event.subject_type,
        subject_id=event.subject_id,
        payload={"_tombstoned": True, "reason": "retention_policy"},
        causation_id=event.causation_id,
        correlation_id=event.correlation_id,
        actor=event.actor,
    )


def apply_retention(
    events: list[RevenueEvent], *, now: datetime | None = None
) -> tuple[list[RevenueEvent], list[str]]:
    """
    Apply retention policy. Returns (kept_or_tombstoned_events, removed_event_ids).

    - legal_hold events: kept as-is, no expiry
    - business_record events past 3y: removed
    - operational events past 90d: tombstoned (envelope kept, payload stripped)
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    kept: list[RevenueEvent] = []
    removed: list[str] = []
    for e in events:
        tier = classify_retention_tier(e.event_type)
        if tier == "legal_hold":
            kept.append(e)
            continue
        if not is_expired(e, now=n):
            kept.append(e)
            continue
        if tier == "operational":
            kept.append(tombstone_event(e))
        else:
            # business_record past retention → physical delete
            removed.append(e.event_id)
    return kept, removed


def retention_summary(events: list[RevenueEvent]) -> dict[str, int]:
    """For the Trust Center display — how many events in each tier."""
    out: dict[str, int] = {"operational": 0, "business_record": 0, "legal_hold": 0}
    for e in events:
        out[classify_retention_tier(e.event_type)] += 1
    return out
