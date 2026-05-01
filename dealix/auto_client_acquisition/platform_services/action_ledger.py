"""In-memory decision log for platform tools (MVP)."""

from __future__ import annotations

import itertools
import threading
import time
from typing import Any

_counter = itertools.count(1)
_lock = threading.Lock()
_entries: list[dict[str, Any]] = []


class ActionLedger:
    """Thread-safe append-only ledger."""

    def append_decision(self, *, tool: str, outcome: str, detail: dict[str, Any]) -> dict[str, Any]:
        with _lock:
            entry = {
                "id": next(_counter),
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tool": tool,
                "outcome": outcome,
                "detail": detail,
            }
            _entries.append(entry)
            if len(_entries) > 500:
                del _entries[:-500]
        return entry

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with _lock:
            return list(_entries[-limit:])


_ledger = ActionLedger()


def get_action_ledger() -> ActionLedger:
    return _ledger
