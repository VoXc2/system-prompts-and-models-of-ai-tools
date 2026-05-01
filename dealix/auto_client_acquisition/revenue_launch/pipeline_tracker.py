"""Simple pipeline schema for founder-led beta — in-memory demo only."""

from __future__ import annotations

from typing import Any

STAGES = [
    "identified",
    "contacted",
    "replied",
    "demo_booked",
    "diagnostic_sent",
    "pilot_offered",
    "paid",
    "lost",
]


def build_pipeline_schema() -> dict[str, Any]:
    return {
        "stages": STAGES,
        "fields_ar": ["company", "person", "segment", "channel", "stage", "next_step_ar", "notes"],
        "demo": True,
    }


def add_prospect(company: str, person: str, segment: str, channel: str) -> dict[str, Any]:
    return {
        "id": f"prospect_{hash(company + person) % 10_000_000}",
        "company": company,
        "person": person,
        "segment": segment,
        "channel": channel,
        "stage": "identified",
        "demo": True,
    }


def update_stage(prospect_id: str, new_stage: str) -> dict[str, Any]:
    st = new_stage if new_stage in STAGES else "identified"
    return {"id": prospect_id, "stage": st, "ok": True, "demo": True}


def summarize_pipeline(prospects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = prospects or []
    counts: dict[str, int] = {s: 0 for s in STAGES}
    for r in rows:
        counts[r.get("stage", "identified")] = counts.get(r.get("stage", "identified"), 0) + 1
    return {"counts_by_stage": counts, "total": len(rows), "demo": True}
