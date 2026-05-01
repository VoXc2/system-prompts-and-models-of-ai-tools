"""Map issue text to priority bucket (deterministic heuristics)."""

from __future__ import annotations

from typing import Any


def route_ticket(issue_ar: str) -> dict[str, Any]:
    t = (issue_ar or "").lower()
    if any(k in t for k in ("أرسل", "إرسال", "send", "live", "خرق", "سر")):
        return {"priority": "P0", "queue_ar": "أمان وتشغيل", "sla_first_response_hours": 2}
    if any(k in t for k in ("تعطل", "502", "500", "error", "خطأ")):
        return {"priority": "P1", "queue_ar": "تشغيل", "sla_first_response_hours": 4}
    if any(k in t for k in ("connector", "ربط", "تكامل", "proof", "تقرير")):
        return {"priority": "P2", "queue_ar": "تكامل ونجاح عميل", "sla_first_response_hours": 24}
    return {"priority": "P3", "queue_ar": "عام", "sla_first_response_hours": 48}
