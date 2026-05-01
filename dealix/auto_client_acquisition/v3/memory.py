"""Event-sourced Revenue Memory for Dealix v3."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Any
from uuid import uuid4


class EventType(StrEnum):
    LEAD_CREATED = "lead.created"
    SIGNAL_DETECTED = "signal.detected"
    MESSAGE_SENT = "message.sent"
    REPLY_RECEIVED = "reply.received"
    MEETING_BOOKED = "meeting.booked"
    DEAL_WON = "deal.won"
    DEAL_LOST = "deal.lost"
    COMPLIANCE_BLOCKED = "compliance.blocked"
    AGENT_ACTION_EXECUTED = "agent.action_executed"


@dataclass(frozen=True)
class RevenueEvent:
    event_type: EventType
    customer_id: str
    aggregate_id: str
    payload: dict[str, Any]
    actor: str = "system"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def integrity_hash(self) -> str:
        raw = f"{self.event_id}|{self.event_type.value}|{self.customer_id}|{self.aggregate_id}|{self.occurred_at.isoformat()}|{self.payload}"
        return sha256(raw.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "customer_id": self.customer_id,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "actor": self.actor,
            "occurred_at": self.occurred_at.isoformat(),
            "integrity_hash": self.integrity_hash(),
        }


class RevenueMemory:
    def __init__(self) -> None:
        self._events: list[RevenueEvent] = []

    def append(self, event: RevenueEvent) -> RevenueEvent:
        self._events.append(event)
        self._events.sort(key=lambda item: item.occurred_at)
        return event

    def timeline(self, aggregate_id: str) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self._events if event.aggregate_id == aggregate_id]

    def projection(self, aggregate_id: str) -> dict[str, Any]:
        events = [event for event in self._events if event.aggregate_id == aggregate_id]
        result: dict[str, Any] = {
            "aggregate_id": aggregate_id,
            "events": len(events),
            "signals": 0,
            "messages": 0,
            "replies": 0,
            "meetings": 0,
            "revenue_sar": 0.0,
            "blocked": False,
            "stage": "unknown",
        }
        for event in events:
            if event.event_type == EventType.SIGNAL_DETECTED:
                result["signals"] += 1
            elif event.event_type == EventType.MESSAGE_SENT:
                result["messages"] += 1
            elif event.event_type == EventType.REPLY_RECEIVED:
                result["replies"] += 1
            elif event.event_type == EventType.MEETING_BOOKED:
                result["meetings"] += 1
                result["stage"] = "meeting_booked"
            elif event.event_type == EventType.DEAL_WON:
                result["stage"] = "won"
                result["revenue_sar"] += float(event.payload.get("amount", 0) or 0)
            elif event.event_type == EventType.DEAL_LOST:
                result["stage"] = "lost"
            elif event.event_type == EventType.COMPLIANCE_BLOCKED:
                result["blocked"] = True
                result["stage"] = "blocked"
        return result


def demo_memory() -> RevenueMemory:
    memory = RevenueMemory()
    memory.append(RevenueEvent(EventType.SIGNAL_DETECTED, "demo", "clinic_riyadh_01", {"signal": "hiring_sales"}))
    memory.append(RevenueEvent(EventType.MESSAGE_SENT, "demo", "clinic_riyadh_01", {"channel": "whatsapp"}))
    memory.append(RevenueEvent(EventType.REPLY_RECEIVED, "demo", "clinic_riyadh_01", {"intent": "positive"}))
    memory.append(RevenueEvent(EventType.MEETING_BOOKED, "demo", "clinic_riyadh_01", {"date": "next_week"}))
    return memory
