"""
Event Store — append-only log of RevenueEvents.

Two implementations:
  - InMemoryEventStore — for tests and offline replay
  - SqlAlchemyEventStore — production (lazy import to avoid hard dep here)

Storage contract:
  - APPEND ONLY. No updates, no deletes (except via retention.py policy).
  - Events ordered by (occurred_at, event_id).
  - Filterable by customer_id, subject (type+id), event_type, time window.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import asdict
from datetime import datetime
from typing import Any, Protocol

from auto_client_acquisition.revenue_memory.events import (
    RevenueEvent,
    event_from_dict,
    event_to_dict,
)


class EventStore(Protocol):
    """Interface every event-store implementation must satisfy."""

    def append(self, event: RevenueEvent) -> None: ...

    def append_many(self, events: list[RevenueEvent]) -> None: ...

    def read_for_customer(
        self,
        customer_id: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        event_types: tuple[str, ...] | None = None,
    ) -> Iterator[RevenueEvent]: ...

    def read_for_subject(
        self,
        subject_type: str,
        subject_id: str,
        *,
        customer_id: str | None = None,
    ) -> Iterator[RevenueEvent]: ...

    def count(self, customer_id: str | None = None) -> int: ...


class InMemoryEventStore:
    """In-memory implementation — fast, deterministic, used by tests."""

    def __init__(self) -> None:
        self._events: list[RevenueEvent] = []

    def append(self, event: RevenueEvent) -> None:
        self._events.append(event)

    def append_many(self, events: list[RevenueEvent]) -> None:
        self._events.extend(events)

    def read_for_customer(
        self,
        customer_id: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        event_types: tuple[str, ...] | None = None,
    ) -> Iterator[RevenueEvent]:
        for e in self._sorted_events():
            if e.customer_id != customer_id:
                continue
            if since is not None and e.occurred_at < since:
                continue
            if until is not None and e.occurred_at > until:
                continue
            if event_types is not None and e.event_type not in event_types:
                continue
            yield e

    def read_for_subject(
        self,
        subject_type: str,
        subject_id: str,
        *,
        customer_id: str | None = None,
    ) -> Iterator[RevenueEvent]:
        for e in self._sorted_events():
            if e.subject_type != subject_type or e.subject_id != subject_id:
                continue
            if customer_id is not None and e.customer_id != customer_id:
                continue
            yield e

    def count(self, customer_id: str | None = None) -> int:
        if customer_id is None:
            return len(self._events)
        return sum(1 for e in self._events if e.customer_id == customer_id)

    def _sorted_events(self) -> list[RevenueEvent]:
        return sorted(self._events, key=lambda e: (e.occurred_at, e.event_id))

    # Useful for tests + admin tooling
    def export_all(self) -> list[dict[str, Any]]:
        return [event_to_dict(e) for e in self._sorted_events()]

    def import_all(self, dicts: list[dict[str, Any]]) -> None:
        self._events = [event_from_dict(d) for d in dicts]


# ── Module-level convenience for tests / scripts ─────────────────
_DEFAULT_STORE: InMemoryEventStore | None = None


def get_default_store() -> InMemoryEventStore:
    """Lazy singleton — used by helpers when no store is injected."""
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = InMemoryEventStore()
    return _DEFAULT_STORE


def append_event(event: RevenueEvent, *, store: EventStore | None = None) -> None:
    """Module-level append helper — uses default in-memory store if none given."""
    s = store or get_default_store()
    s.append(event)


def reset_default_store() -> None:
    """Reset for tests."""
    global _DEFAULT_STORE
    _DEFAULT_STORE = InMemoryEventStore()
