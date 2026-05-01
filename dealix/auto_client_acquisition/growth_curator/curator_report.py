"""Weekly curator narrative — Arabic, deterministic."""

from __future__ import annotations

from typing import Any


def build_weekly_curator_report(context: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = context or {}
    return {
        "week_label_ar": str(ctx.get("week_label_ar") or "أسبوع تجريبي"),
        "summary_ar": "تمت مراجعة رسائل المسودات: أرشفة ٣ نسخ ضعيفة، دمج تشابه في عنوانين، تحسين CTA في ٤ رسائل.",
        "actions_ar": [
            "حافظ على سؤال واحد لكل رسالة واتساب.",
            "قلل الوعود المطلقة في البريد.",
            "فعّل متابعة ٤٨ ساعة بعد الاجتماع فقط بعد الموافقة.",
        ],
        "demo": True,
    }
