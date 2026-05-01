"""Channel health snapshot (deterministic demo)."""

from __future__ import annotations

from typing import Any


def demo_channel_health() -> dict[str, Any]:
    return {
        "channels": [
            {"channel": "email", "health_score": 78, "notes_ar": "مسودات فقط — جيد"},
            {"channel": "whatsapp", "health_score": 62, "notes_ar": "يحتاج opt-in واضح"},
            {"channel": "linkedin", "health_score": 70, "notes_ar": "Lead Forms أولاً — لا auto-DM"},
        ],
        "demo": True,
    }
