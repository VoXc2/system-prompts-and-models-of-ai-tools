"""SLA summary for support tiers (static policy text + JSON for API)."""

from __future__ import annotations

from typing import Any


def build_sla_summary() -> dict[str, Any]:
    return {
        "tiers": [
            {
                "id": "P0",
                "name_ar": "أمان / إرسال خاطئ / توقف كامل",
                "first_response_hours": 2,
                "resolution_target_hours": 8,
            },
            {
                "id": "P1",
                "name_ar": "تعطل خدمة أساسية",
                "first_response_hours": 4,
                "resolution_target_hours": 24,
            },
            {
                "id": "P2",
                "name_ar": "تكامل أو Proof متأخر",
                "first_response_hours": 24,
                "resolution_target_hours": 72,
            },
            {
                "id": "P3",
                "name_ar": "سؤال أو تحسين",
                "first_response_hours": 48,
                "resolution_target_hours": 120,
            },
        ],
        "notes_ar": "الأرقام أهداف تشغيلية للـ Pilot؛ تُحدّث في العقد/Appendix عند التوسع.",
    }
