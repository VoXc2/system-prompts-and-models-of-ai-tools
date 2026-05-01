"""
Event taxonomy + envelope.

Every state-changing fact in Dealix flows through a typed event. Events are
immutable — once appended, they never change. Mutations to "current state"
are projections computed from the event stream.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── The canonical event taxonomy — versioned ─────────────────────
EVENT_TYPES: tuple[str, ...] = (
    # Lead lifecycle
    "lead.created",
    "lead.qualified",
    "lead.disqualified",
    "lead.enriched",
    "lead.merged",                   # dedup
    # Company state
    "company.created",
    "company.enriched",
    "company.scored",
    # Signals (market radar)
    "signal.detected",
    "signal.expired",
    "signal.confirmed",
    # Outreach
    "message.drafted",
    "message.approved",
    "message.rejected",
    "message.sent",
    "message.bounced",
    "message.opened",
    "message.clicked",
    "message.replied",
    # Reply classification
    "reply.received",
    "reply.classified",
    # Meetings & demos
    "meeting.requested",
    "meeting.booked",
    "meeting.held",
    "meeting.no_show",
    # Deal lifecycle
    "deal.created",
    "deal.stage_changed",
    "deal.proposal_sent",
    "deal.won",
    "deal.lost",
    "deal.stalled",
    # Customer lifecycle
    "customer.onboarded",
    "customer.health_changed",
    "customer.qbr_generated",
    "customer.expansion_detected",
    "customer.churn_predicted",
    "customer.churned",
    # Compliance
    "compliance.consent_recorded",
    "compliance.opt_out_received",
    "compliance.blocked",
    "compliance.dsr_received",
    "compliance.dsr_completed",
    # Agent lifecycle (orchestrator)
    "agent.action_requested",
    "agent.action_approved",
    "agent.action_rejected",
    "agent.action_executed",
    "agent.action_failed",
    # AI quality
    "ai.eval_run",
    "ai.regression_detected",
    # Pulse
    "pulse.published",
)


@dataclass(frozen=True)
class RevenueEvent:
    """
    Immutable event envelope.

    `subject_*` fields locate the event on the entity timeline (account,
    deal, customer, etc.). `payload` carries the type-specific data.
    `causation_id` lets you trace a chain of events triggered by one cause.
    """

    event_id: str
    event_type: str
    customer_id: str            # the Dealix customer this event belongs to
    occurred_at: datetime
    subject_type: str           # account|company|deal|customer|campaign|agent_task
    subject_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    causation_id: str | None = None  # event_id that caused this event
    correlation_id: str | None = None  # groups related events (e.g. one workflow run)
    actor: str = "system"       # who fired it: system / user_id / agent_id
    schema_version: int = 1


def make_event(
    *,
    event_type: str,
    customer_id: str,
    subject_type: str,
    subject_id: str,
    payload: dict[str, Any] | None = None,
    causation_id: str | None = None,
    correlation_id: str | None = None,
    actor: str = "system",
    occurred_at: datetime | None = None,
) -> RevenueEvent:
    """Build a new event with a UUID + UTC timestamp."""
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event_type: {event_type}")
    return RevenueEvent(
        event_id=f"evt_{uuid.uuid4().hex[:24]}",
        event_type=event_type,
        customer_id=customer_id,
        occurred_at=occurred_at or datetime.now(timezone.utc).replace(tzinfo=None),
        subject_type=subject_type,
        subject_id=subject_id,
        payload=payload or {},
        causation_id=causation_id,
        correlation_id=correlation_id,
        actor=actor,
    )


def event_to_dict(e: RevenueEvent) -> dict[str, Any]:
    """Stable serialization — used by event_store + audit exports."""
    return {
        "event_id": e.event_id,
        "event_type": e.event_type,
        "customer_id": e.customer_id,
        "occurred_at": e.occurred_at.isoformat(),
        "subject_type": e.subject_type,
        "subject_id": e.subject_id,
        "payload": e.payload,
        "causation_id": e.causation_id,
        "correlation_id": e.correlation_id,
        "actor": e.actor,
        "schema_version": e.schema_version,
    }


def event_from_dict(d: dict[str, Any]) -> RevenueEvent:
    """Reverse of event_to_dict — reconstitute from JSON."""
    return RevenueEvent(
        event_id=d["event_id"],
        event_type=d["event_type"],
        customer_id=d["customer_id"],
        occurred_at=datetime.fromisoformat(d["occurred_at"]),
        subject_type=d["subject_type"],
        subject_id=d["subject_id"],
        payload=d.get("payload", {}),
        causation_id=d.get("causation_id"),
        correlation_id=d.get("correlation_id"),
        actor=d.get("actor", "system"),
        schema_version=d.get("schema_version", 1),
    )
