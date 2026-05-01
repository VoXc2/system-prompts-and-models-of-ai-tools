"""Weekly cadence for pilots (deterministic)."""

from __future__ import annotations

from typing import Any


def build_weekly_cadence() -> dict[str, Any]:
    return {
        "weekly_touchpoints_ar": [
            "مراجعة كروت الموافقة المعلقة.",
            "تحديث Proof Pack (مسودات، موافقات، مخاطر ممنوعة).",
            "مكالمة قصيرة أو تحديث كتابي مع صاحب القرار.",
            "قراءة مؤشرات القنوات (ردود، شكاوى، opt-out = صفر مطلوب).",
        ],
        "metrics_to_track": [
            "demos_booked",
            "pilots_active",
            "drafts_approved",
            "risks_blocked",
            "proof_events",
        ],
    }
