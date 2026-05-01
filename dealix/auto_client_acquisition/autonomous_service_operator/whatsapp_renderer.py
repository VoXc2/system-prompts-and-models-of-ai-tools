"""WhatsApp payload shapes (text templates only — no live send)."""

from __future__ import annotations

from typing import Any


def render_daily_brief_stub() -> dict[str, Any]:
    return {
        "channel": "whatsapp",
        "format": "text_stub",
        "body_ar": (
            "موجز Dealix (مسودة): ٣ قرارات مقترحة — راجع لوحة الموافقات. "
            "لا يُرسل هذا النص تلقائياً من المنصة في MVP."
        ),
        "demo": True,
    }
