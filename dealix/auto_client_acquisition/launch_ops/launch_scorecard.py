"""Launch scorecard — daily and weekly metrics for Private Beta ops."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# Valid event types the launch scorecard accepts.
VALID_LAUNCH_EVENTS: tuple[str, ...] = (
    "outreach_sent",
    "reply_received",
    "demo_booked",
    "demo_held",
    "diagnostic_delivered",
    "pilot_offered",
    "pilot_paid",
    "pilot_committed",
    "pilot_lost",
    "case_study_published",
    "blocked_action",
)

# Daily targets per the launch plan.
DAILY_TARGETS: dict[str, int] = {
    "outreach_sent": 20,
    "reply_received": 5,
    "demo_booked": 3,
    "pilot_paid": 1,
}

# Weekly targets (7-day plan).
WEEKLY_TARGETS: dict[str, int] = {
    "outreach_sent": 100,
    "reply_received": 20,
    "demo_booked": 10,
    "pilot_paid": 2,
}


def record_launch_event(
    *,
    event_type: str,
    customer_id: str | None = None,
    notes: str | None = None,
    event_log: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Record a launch event into an in-memory log.

    Returns the appended entry (validated). Raises ValueError on unknown type.
    """
    if event_type not in VALID_LAUNCH_EVENTS:
        raise ValueError(
            f"Unknown launch event: {event_type}. "
            f"Valid: {', '.join(VALID_LAUNCH_EVENTS)}"
        )
    entry: dict[str, Any] = {
        "event_type": event_type,
        "customer_id": customer_id,
        "notes": (notes or "")[:300],
    }
    if event_log is not None:
        event_log.append(entry)
    return entry


def _aggregate(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for e in events or []:
        et = str(e.get("event_type", ""))
        counts[et] += 1
    return dict(counts)


def build_daily_launch_scorecard(
    *, events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build today's Arabic launch scorecard from event log."""
    counts = _aggregate(events or [])
    metrics = {k: counts.get(k, 0) for k in VALID_LAUNCH_EVENTS}

    progress: dict[str, dict[str, int | float]] = {}
    for k, target in DAILY_TARGETS.items():
        actual = metrics.get(k, 0)
        pct = round(100 * actual / target, 1) if target else 0.0
        progress[k] = {"actual": actual, "target": target, "pct": pct}

    summary_lines = [
        f"تواصل اليوم: {metrics['outreach_sent']} / {DAILY_TARGETS['outreach_sent']}",
        f"ردود: {metrics['reply_received']} / {DAILY_TARGETS['reply_received']}",
        f"ديموهات: {metrics['demo_booked']} / {DAILY_TARGETS['demo_booked']}",
        f"Pilots مدفوعة: {metrics['pilot_paid']} / {DAILY_TARGETS['pilot_paid']}",
        f"مخاطر منعت: {metrics.get('blocked_action', 0)}",
    ]

    return {
        "metrics": metrics,
        "targets": DAILY_TARGETS,
        "progress": progress,
        "summary_ar": summary_lines,
    }


def build_weekly_launch_scorecard(
    *, events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the 7-day Arabic launch scorecard."""
    counts = _aggregate(events or [])
    metrics = {k: counts.get(k, 0) for k in VALID_LAUNCH_EVENTS}

    progress = {}
    for k, target in WEEKLY_TARGETS.items():
        actual = metrics.get(k, 0)
        pct = round(100 * actual / target, 1) if target else 0.0
        progress[k] = {"actual": actual, "target": target, "pct": pct}

    summary_lines = [
        f"تواصل الأسبوع: {metrics['outreach_sent']} / {WEEKLY_TARGETS['outreach_sent']}",
        f"ردود: {metrics['reply_received']} / {WEEKLY_TARGETS['reply_received']}",
        f"ديموهات منعقدة: {metrics.get('demo_held', 0)}",
        f"Pilots مدفوعة: {metrics['pilot_paid']} / {WEEKLY_TARGETS['pilot_paid']}",
        f"Pilots commitments: {metrics.get('pilot_committed', 0)}",
        f"Pilots خسرت: {metrics.get('pilot_lost', 0)}",
        f"مخاطر منعت: {metrics.get('blocked_action', 0)}",
    ]

    if metrics["pilot_paid"] >= WEEKLY_TARGETS["pilot_paid"]:
        verdict = "on_track"
    elif metrics["demo_booked"] >= 5:
        verdict = "promising"
    else:
        verdict = "needs_focus"

    return {
        "metrics": metrics,
        "targets": WEEKLY_TARGETS,
        "progress": progress,
        "summary_ar": summary_lines,
        "verdict": verdict,
    }
