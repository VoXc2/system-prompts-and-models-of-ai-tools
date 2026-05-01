"""Deliverables + Proof Pack templates per service."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service


def build_deliverables(service_id: str) -> dict[str, Any]:
    """Return the deliverables list for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "deliverables_ar": list(s.deliverables_ar),
        "approval_required": True,
    }


def build_proof_pack_template(service_id: str) -> dict[str, Any]:
    """Build a proof-pack template for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "metrics_to_track": list(s.proof_metrics),
        "report_sections_ar": [
            "ملخص الفترة",
            "ما تم إنجازه (ledger entries)",
            "النتائج بالأرقام (الـ proof_metrics)",
            "المخاطر التي تم منعها",
            "تجربة الأسبوع/الشهر القادم",
            "التوصية بالخطوة التالية",
        ],
        "delivery_format": ["pdf", "json", "whatsapp_summary"],
        "approval_required": True,
    }


def build_client_report_outline(service_id: str) -> dict[str, Any]:
    """Outline of the client-facing report for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "title_ar": f"تقرير {s.name_ar}",
        "sections_ar": [
            "ملخص تنفيذي (10 أسطر)",
            "السياق والأهداف",
            "ما عمله Dealix",
            "النتائج (الأرقام مقابل الأهداف)",
            "أبرز الاعتراضات والـsignals",
            "المخاطر التي تم منعها",
            "Proof — ledger events",
            "التوصية بالخطوة التالية",
        ],
        "approval_required": True,
    }


def build_internal_operator_checklist(service_id: str) -> dict[str, Any]:
    """Internal operator checklist (for the team running the service)."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "checklist_ar": [
            "مراجعة الـ intake واكتمال الحقول.",
            "تشغيل targeting + contactability.",
            "صياغة الـ drafts الأولى.",
            "إرسال للـ approval center.",
            "تنفيذ بعد الاعتماد فقط.",
            "تتبع النتائج في الـ Action Ledger.",
            "بناء Proof Pack.",
            "اقتراح الترقية للعميل.",
        ],
        "do_not_do_ar": [
            "لا live send بدون env flag + اعتماد.",
            "لا إرسال على cold list.",
            "لا charge بدون تأكيد.",
            "لا تخزين أسرار في الـ payload.",
        ],
    }
