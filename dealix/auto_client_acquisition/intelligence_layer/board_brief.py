"""Executive board brief — Arabic headline + bullets."""

from __future__ import annotations

from typing import Any


def build_board_brief(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    sn = snapshot or {}
    title = str(sn.get("title_ar") or "موجز أسبوعي — Dealix")
    return {
        "title_ar": title,
        "bullets_ar": [
            "زخم الصفقات: مستقر مع حاجة لمتابعة ما بعد الاجتماع.",
            "الامتثال: لا إرسال جماعي حتى اكتمال opt-in.",
            "الفرص: ركّز على قطاعين بدل تشتيت ICP.",
        ],
        "demo": True,
    }
