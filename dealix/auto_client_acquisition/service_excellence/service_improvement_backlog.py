"""Prioritized improvement backlog per service."""

from __future__ import annotations

from typing import Any


def build_backlog(service_id: str) -> list[dict[str, Any]]:
    return [
        {"id": f"{service_id}_tone_eval", "title_ar": "تقييم نبرة سعودية", "priority": 1},
        {"id": f"{service_id}_latency", "title_ar": "تقليل زمن توليد المسودات", "priority": 2},
        {"id": f"{service_id}_integrations", "title_ar": "OAuth محدود النطاق", "priority": 3},
    ]


def prioritize_backlog_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items or [], key=lambda x: int(x.get("priority", 99)))


def convert_feedback_to_backlog(feedback: str) -> dict[str, Any]:
    return {
        "feedback": feedback,
        "backlog_item": {
            "id": "user_feedback_1",
            "title_ar": "معالجة ملاحظة مستخدم",
            "priority": 2,
        },
        "demo": True,
    }


def recommend_weekly_improvements(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "items_ar": [
            "راجع آخر ١٠ موافقات واختصر المسودات.",
            "قارن proof metrics أسبوع بأسبوع.",
        ],
        "demo": True,
    }
