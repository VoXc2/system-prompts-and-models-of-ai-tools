"""Safe competitive move suggestions (display-only)."""

from __future__ import annotations

from typing import Any


def build_competitive_moves(sector: str | None = None) -> dict[str, Any]:
    sec = sector or "عام"
    return {
        "sector": sec,
        "moves_ar": [
            "تضييق رسالة القيمة على نتيجة واحدة قابلة للقياس لكل عميل.",
            "عرض تجربة ٧ أيام مع حدود واضحة للنطاق وتقرير إثبات أسبوعي.",
            "تفعيل غرفة صفقة مشتركة مع SLA داخلي ٢٤ ساعة للرد.",
        ],
        "demo": True,
    }
