"""
Audit Sink — append-only storage for AuditEntry.

Phase 0–1: InMemorySink + structured-log mirror.
Phase 2: PostgresSink with append-only table + monthly partition.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from dealix.contracts.audit_log import AuditEntry


class AuditSink(ABC):
    """Abstract append-only audit sink."""

    @abstractmethod
    def append(self, entry: AuditEntry) -> None: ...

    @abstractmethod
    def recent(self, limit: int = 100) -> list[AuditEntry]: ...


class InMemoryAuditSink(AuditSink):
    """In-memory circular buffer — dev/test only."""

    def __init__(self, max_entries: int = 10_000) -> None:
        self._entries: list[AuditEntry] = []
        self._max = max_entries

    def append(self, entry: AuditEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]

    def recent(self, limit: int = 100) -> list[AuditEntry]:
        return self._entries[-limit:]

    def filter(
        self,
        *,
        entity_id: str | None = None,
        decision_id: str | None = None,
        action_contains: str | None = None,
    ) -> list[AuditEntry]:
        result = []
        for e in self._entries:
            if entity_id and e.entity_id != entity_id:
                continue
            if decision_id and e.decision_id != decision_id:
                continue
            if action_contains and action_contains not in e.action.value:
                continue
            result.append(e)
        return result
