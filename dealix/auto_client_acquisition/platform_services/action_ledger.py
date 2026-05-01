"""
Action Ledger — auditable record of every action lifecycle.

Stage transitions per action: requested → (approved | rejected | blocked)
→ executed → outcome.

Used for SDAIA / DPO inspections + customer's own audit trail.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


VALID_STAGES: tuple[str, ...] = (
    "requested", "approved", "rejected", "blocked",
    "executed", "outcome_recorded",
)


@dataclass
class LedgerEntry:
    """One entry in the action ledger."""

    entry_id: str
    customer_id: str
    action_type: str
    channel: str
    stage: str
    actor: str = "system"
    payload: dict[str, Any] = field(default_factory=dict)
    reason_ar: str = ""
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "customer_id": self.customer_id,
            "action_type": self.action_type,
            "channel": self.channel,
            "stage": self.stage,
            "actor": self.actor,
            "payload": self.payload,
            "reason_ar": self.reason_ar,
            "created_at": self.created_at.isoformat(),
            "correlation_id": self.correlation_id,
        }


@dataclass
class ActionLedger:
    """Append-only ledger keyed by customer_id."""

    entries: list[LedgerEntry] = field(default_factory=list)

    def append(
        self,
        *,
        customer_id: str,
        action_type: str,
        channel: str,
        stage: str,
        actor: str = "system",
        payload: dict[str, Any] | None = None,
        reason_ar: str = "",
        correlation_id: str | None = None,
    ) -> LedgerEntry:
        if stage not in VALID_STAGES:
            raise ValueError(f"unknown stage: {stage}")
        entry = LedgerEntry(
            entry_id=f"led_{uuid.uuid4().hex[:20]}",
            customer_id=customer_id,
            action_type=action_type,
            channel=channel,
            stage=stage,
            actor=actor,
            payload=payload or {},
            reason_ar=reason_ar,
            correlation_id=correlation_id,
        )
        self.entries.append(entry)
        return entry

    def for_customer(self, customer_id: str) -> list[LedgerEntry]:
        return [e for e in self.entries if e.customer_id == customer_id]

    def summary(self, customer_id: str | None = None) -> dict[str, Any]:
        pool = self.entries if customer_id is None else self.for_customer(customer_id)
        by_stage: dict[str, int] = {}
        by_channel: dict[str, int] = {}
        by_action: dict[str, int] = {}
        for e in pool:
            by_stage[e.stage] = by_stage.get(e.stage, 0) + 1
            by_channel[e.channel] = by_channel.get(e.channel, 0) + 1
            by_action[e.action_type] = by_action.get(e.action_type, 0) + 1
        return {
            "total": len(pool),
            "by_stage": by_stage,
            "by_channel": by_channel,
            "by_action_type": by_action,
        }
