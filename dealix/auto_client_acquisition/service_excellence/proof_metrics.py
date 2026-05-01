"""Proof metrics — كل خدمة لازم تثبت العائد بأرقام محددة."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service


def required_proof_metrics(service_id: str) -> list[str]:
    """Return the proof metrics every run of the service must produce."""
    s = get_service(service_id)
    if s is None:
        return []
    return list(s.proof_metrics)


def build_proof_pack_template_excellence(service_id: str) -> dict[str, Any]:
    """Build a polished Proof Pack template for an excellence-tier service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "executive_summary_ar": (
            "ملخص تنفيذي من 10 أسطر يعرض النتائج، الأثر المالي، "
            "والمخاطر التي تم منعها."
        ),
        "metrics": list(s.proof_metrics),
        "report_format": ["pdf", "json", "whatsapp_summary"],
        "signature_required": True,
        "approval_required": True,
    }


def calculate_service_roi_estimate(
    service_id: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    """Estimate ROI = pipeline_influenced / service_price."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    price = max(1, float(metrics.get("price_paid_sar", s.pricing_min_sar or 1)))
    pipeline = float(metrics.get("pipeline_sar", 0))
    closed_won = float(metrics.get("closed_won_sar", 0))

    roi_pipeline_x = round(pipeline / price, 2)
    roi_closed_x = round(closed_won / price, 2)

    return {
        "service_id": service_id,
        "price_paid_sar": price,
        "pipeline_sar": pipeline,
        "closed_won_sar": closed_won,
        "roi_pipeline_x": roi_pipeline_x,
        "roi_closed_x": roi_closed_x,
        "summary_ar": (
            f"كل ريال أنفقه العميل على {s.name_ar} أنتج "
            f"{roi_pipeline_x}× pipeline و {roi_closed_x}× closed-won."
        ),
    }


def summarize_proof_ar(service_id: str, metrics: dict[str, Any]) -> str:
    """Build a one-paragraph Arabic proof summary."""
    roi = calculate_service_roi_estimate(service_id, metrics)
    if "error" in roi:
        return roi["error"]
    return roi["summary_ar"]
