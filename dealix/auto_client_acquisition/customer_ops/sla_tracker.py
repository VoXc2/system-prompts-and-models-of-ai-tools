"""SLA tracker — measure first-response, MTTR, weekly support health."""

from __future__ import annotations

import time
from typing import Any

# Default SLA targets per priority (minutes for first_response, hours for resolution).
SLA_TARGETS: dict[str, dict[str, float]] = {
    "P0": {"first_response_min": 30, "resolution_hours": 4},
    "P1": {"first_response_min": 120, "resolution_hours": 24},
    "P2": {"first_response_min": 480, "resolution_hours": 72},
    "P3": {"first_response_min": 1440, "resolution_hours": 168},
}


def record_sla_event(
    *,
    ticket_id: str,
    priority: str,
    event: str,
    log: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Record an SLA event.

    `event` = "opened" | "first_response" | "resolved" | "escalated".
    """
    if event not in {"opened", "first_response", "resolved", "escalated"}:
        raise ValueError(f"Unknown SLA event: {event}")
    entry: dict[str, Any] = {
        "ticket_id": ticket_id,
        "priority": priority,
        "event": event,
        "ts": time.time(),
    }
    if log is not None:
        log.append(entry)
    return entry


def classify_sla_breach(
    *,
    priority: str,
    minutes_to_first_response: float | None = None,
    hours_to_resolve: float | None = None,
) -> dict[str, Any]:
    """Classify whether SLA was breached for a single ticket."""
    target = SLA_TARGETS.get(priority, SLA_TARGETS["P3"])
    breaches: list[str] = []

    if (minutes_to_first_response is not None
            and minutes_to_first_response > target["first_response_min"]):
        breaches.append(
            f"first_response: {minutes_to_first_response:.0f} > "
            f"{target['first_response_min']} min"
        )

    if (hours_to_resolve is not None
            and hours_to_resolve > target["resolution_hours"]):
        breaches.append(
            f"resolution: {hours_to_resolve:.1f}h > "
            f"{target['resolution_hours']}h"
        )

    return {
        "priority": priority,
        "breached": bool(breaches),
        "breaches": breaches,
    }


def build_sla_health_report(
    *,
    tickets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a weekly SLA health report from a list of tickets."""
    tickets = tickets or []
    by_priority: dict[str, dict[str, Any]] = {}
    total_tickets = len(tickets)
    total_breached = 0

    for t in tickets:
        priority = str(t.get("priority", "P3"))
        bucket = by_priority.setdefault(priority, {
            "count": 0, "breaches": 0,
            "total_first_response_min": 0.0,
            "total_resolution_hours": 0.0,
            "responded_count": 0, "resolved_count": 0,
        })
        bucket["count"] += 1
        ftr = t.get("first_response_min")
        ttr = t.get("resolution_hours")
        b = classify_sla_breach(
            priority=priority,
            minutes_to_first_response=ftr,
            hours_to_resolve=ttr,
        )
        if b["breached"]:
            bucket["breaches"] += 1
            total_breached += 1
        if ftr is not None:
            bucket["total_first_response_min"] += float(ftr)
            bucket["responded_count"] += 1
        if ttr is not None:
            bucket["total_resolution_hours"] += float(ttr)
            bucket["resolved_count"] += 1

    # Compute averages.
    for p, b in by_priority.items():
        if b["responded_count"]:
            b["avg_first_response_min"] = round(
                b["total_first_response_min"] / b["responded_count"], 1,
            )
        if b["resolved_count"]:
            b["avg_resolution_hours"] = round(
                b["total_resolution_hours"] / b["resolved_count"], 2,
            )

    breach_rate = round(total_breached / total_tickets, 3) if total_tickets else 0.0

    return {
        "total_tickets": total_tickets,
        "total_breached": total_breached,
        "breach_rate": breach_rate,
        "by_priority": by_priority,
        "verdict": (
            "healthy" if breach_rate < 0.10
            else "watch" if breach_rate < 0.25
            else "critical"
        ),
    }
