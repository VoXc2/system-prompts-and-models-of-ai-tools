"""Deliverables and proof pack outlines per service."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def build_deliverables(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    if not svc:
        return {"service_id": service_id, "deliverables": [], "demo": True}
    items = list(svc.get("deliverables_ar") or [])
    return {"service_id": service_id, "deliverables_ar": items, "count": len(items), "demo": True}


def build_proof_pack_template(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    metrics = list((svc or {}).get("proof_metrics") or [])
    return {
        "service_id": service_id,
        "sections_ar": [
            "ملخص الأسبوع",
            "ما تم اعتماده",
            "المخاطر التي تم منعها",
            "الأثر المقدّر",
            "الخطوة التالية",
        ],
        "proof_metrics": metrics,
        "demo": True,
    }


def build_client_report_outline(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "outline_ar": [
            "الهدف والمدخلات",
            "ما نفّذناه (مسودات/موافقات)",
            "النتائج المقيسة",
            "المخاطر والامتثال",
            "التوصية للأسبوع القادم",
        ],
        "demo": True,
    }


def build_internal_operator_checklist(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "checklist_ar": [
            "تأكد من عدم وجود إرسال حي",
            "راجع contactability",
            "سجّل الموافقات في الدفتر",
            "حدّث Proof Pack",
        ],
        "demo": True,
    }
