"""Curated list of playbook/message skills — deterministic inventory."""

from __future__ import annotations

from typing import Any


def list_skill_inventory() -> dict[str, Any]:
    skills: list[dict[str, Any]] = [
        {"id": "saudi_short_pitch", "score": 88, "usage_count_demo": 42, "status": "active"},
        {"id": "objection_timing", "score": 72, "usage_count_demo": 18, "status": "active"},
        {"id": "cold_whatsapp_template", "score": 12, "usage_count_demo": 3, "status": "archived", "reason_ar": "مخالف سياسة القناة"},
    ]
    return {"skills": skills, "recommendation_ar": "أرشف القوالب منخفضة الدرجة وادمج المتشابه.", "demo": True}


def score_skill(skill_id: str) -> dict[str, Any]:
    inv = list_skill_inventory()
    for s in inv["skills"]:
        if s["id"] == skill_id:
            return {"skill": s, "demo": True}
    return {"error": "not_found", "demo": True}
