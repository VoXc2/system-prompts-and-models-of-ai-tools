"""Lightweight counters — replace with Prometheus / OTel in production."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BrainMetrics:
    events_ingested: int = 0
    events_rate_limited: int = 0
    agent_sessions_started: int = 0
    skills_executed: int = 0
    skills_failed: int = 0
    last_event_monotonic: float = field(default_factory=time.monotonic)


_metrics = BrainMetrics()


def record_event_ingested() -> None:
    _metrics.events_ingested += 1
    _metrics.last_event_monotonic = time.monotonic()


def record_rate_limited() -> None:
    _metrics.events_rate_limited += 1


def record_session_started() -> None:
    _metrics.agent_sessions_started += 1


def record_skill(ok: bool) -> None:
    _metrics.skills_executed += 1
    if not ok:
        _metrics.skills_failed += 1


def snapshot() -> Dict[str, int | float]:
    return {
        "events_ingested": _metrics.events_ingested,
        "events_rate_limited": _metrics.events_rate_limited,
        "agent_sessions_started": _metrics.agent_sessions_started,
        "skills_executed": _metrics.skills_executed,
        "skills_failed": _metrics.skills_failed,
        "last_event_monotonic": _metrics.last_event_monotonic,
    }
