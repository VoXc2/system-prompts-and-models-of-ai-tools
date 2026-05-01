"""Mission / playbook curation suggestions — no automatic deletion."""

from __future__ import annotations

from typing import Any


def curate_missions_weekly() -> dict[str, Any]:
    return {
        "merged_pairs_ar": ["book_three_meetings + followup_sequence → دمج عنوان الخطوات"],
        "archived_ids": ["deprecated_template_v1"],
        "next_week_focus_ar": "زيادة Pilot 7 أيام في قطاع التدريب",
        "demo": True,
    }


def score_mission_popularity(mission_id: str) -> dict[str, Any]:
    return {"mission_id": mission_id, "popularity_score": 81 if "10" in mission_id else 55, "demo": True}
