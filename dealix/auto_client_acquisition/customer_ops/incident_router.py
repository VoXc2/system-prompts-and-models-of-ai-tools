"""Incident routing stub (no paging, no secrets)."""

from __future__ import annotations

from typing import Any


def build_incident_playbook() -> dict[str, Any]:
    return {
        "steps_ar": [
            "تصنيف الخطورة (P0–P3) وفق وصف الحادث.",
            "إيقاف أي إجراء live إن وُجد حتى التحقق.",
            "توثيق الوقت، التأثير، والخطوات المتخذة (بدون أسرار أو PII خام).",
            "إشعار العميل بلغة واضحة وخطة تعافي.",
            "مراجعة لاحقة وتحديث السياسات/الاختبارات إن لزم.",
        ],
        "contacts_placeholder_ar": "يُحدَّد في العقد: بريد دعم + قناة طوارئ للـ P0.",
    }


def classify_incident(severity: str) -> dict[str, Any]:
    s = (severity or "P3").upper()
    if s not in {"P0", "P1", "P2", "P3"}:
        s = "P3"
    return {"severity": s, "escalate": s in {"P0", "P1"}}
