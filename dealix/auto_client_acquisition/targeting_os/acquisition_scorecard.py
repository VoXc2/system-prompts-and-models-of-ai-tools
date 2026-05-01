"""Acquisition metrics snapshot — deterministic."""

from __future__ import annotations

from typing import Any


def calculate_pipeline_created(opportunities: list[dict[str, Any]]) -> int:
    total = 0
    for o in opportunities:
        total += int(o.get("expected_value_sar") or o.get("expected_impact_sar") or 5000)
    return total


def calculate_meetings_booked(events: list[dict[str, Any]]) -> int:
    return sum(1 for e in events if e.get("type") == "meeting_booked")


def calculate_risks_blocked(actions: list[dict[str, Any]]) -> int:
    return sum(1 for a in actions if a.get("outcome") == "blocked")


def calculate_productivity_score(metrics: dict[str, Any]) -> int:
    base = 50
    base += min(30, int(metrics.get("drafts_approved", 0)) * 3)
    base += min(20, int(metrics.get("meetings_booked", 0)) * 5)
    return max(0, min(100, base))


def build_acquisition_scorecard(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "leads_created": metrics.get("leads_created", 0),
        "meetings_booked": metrics.get("meetings_booked", 0),
        "drafts_approved": metrics.get("drafts_approved", 0),
        "risks_blocked": metrics.get("risks_blocked", 0),
        "pipeline_created_sar": metrics.get("pipeline_created_sar", 0),
        "productivity_score": calculate_productivity_score(metrics),
        "demo": True,
    }
