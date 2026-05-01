"""Grade Arabic outreach messages — heuristic MVP."""

from __future__ import annotations

from typing import Any


def grade_message(message_ar: str, *, sector: str = "", channel: str = "whatsapp") -> dict[str, Any]:
    text = (message_ar or "").strip()
    score = 70
    notes: list[str] = []
    if len(text) < 40:
        score -= 15
        notes.append("قصير جداً — أضف سياقاً ولماذا الآن.")
    if len(text) > 900:
        score -= 10
        notes.append("طويل — قصّر للواتساب/المتابعة السريعة.")
    if "ضمان" in text or "مضمون" in text or "100%" in text:
        score -= 20
        notes.append("تجنب وعود مطلقة — خطر امتثال.")
    if "؟" not in text and "?" not in text:
        score -= 5
        notes.append("أضف سؤالاً واحداً واضحاً لزيادة الرد.")
    if channel == "email" and "السلام" not in text and "عليكم" not in text:
        notes.append("افتتح بتحية مهنية للبريد.")
    score = max(0, min(100, score))
    band = "strong" if score >= 80 else "ok" if score >= 60 else "weak"
    return {"score": score, "band": band, "notes_ar": notes, "sector": sector, "channel": channel, "demo": True}
