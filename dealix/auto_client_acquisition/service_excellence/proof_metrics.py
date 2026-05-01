"""Required proof metrics and ROI estimate stubs."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def required_proof_metrics(service_id: str) -> list[str]:
    svc = get_service_by_id(service_id) or {}
    return list(svc.get("proof_metrics") or ["drafts_created", "approvals"])


def build_proof_pack_template(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "metrics": required_proof_metrics(service_id),
        "template_ar": "ملخص + قرارات + مخاطر منعت + أثر مقدّر",
        "demo": True,
    }


def calculate_service_roi_estimate(service_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
    influenced = int(metrics.get("revenue_influenced_sar", 0))
    if influenced <= 0:
        influenced = int(metrics.get("pipeline_sar", 12000))
    return {
        "service_id": service_id,
        "revenue_influenced_sar_estimate": influenced,
        "note_ar": "تقدير عرضي — ليس وعداً.",
        "demo": True,
    }


def summarize_proof_ar(service_id: str, metrics: dict[str, Any]) -> str:
    r = calculate_service_roi_estimate(service_id, metrics)
    return f"خدمة {service_id}: أثر مقدّر {r.get('revenue_influenced_sar_estimate')} ريال (عرضي)."
