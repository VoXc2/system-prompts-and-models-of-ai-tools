"""Service Delivery Mode — runs client services + tracks SLA + generates Proof.

Production wrapper around service_orchestrator + revenue_launch.pilot_delivery
+ customer_ops.sla_tracker.
"""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.customer_ops import (
    build_sla_health_report,
    classify_sla_breach,
)
from auto_client_acquisition.revenue_launch import (
    build_24h_delivery_plan,
    build_first_10_opportunities_delivery,
    build_growth_diagnostic_delivery,
    build_list_intelligence_delivery,
)
from auto_client_acquisition.service_tower import (
    build_service_workflow,
    get_service,
)


def build_service_delivery_brief(
    *,
    customer_id: str = "",
    service_id: str = "",
    intake: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the day-one delivery brief for a service."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    delivery_template_by_service: dict[str, Any] = {
        "first_10_opportunities_sprint":
            build_first_10_opportunities_delivery(intake or {}),
        "list_intelligence":
            build_list_intelligence_delivery(intake or {}),
        "free_growth_diagnostic":
            build_growth_diagnostic_delivery(intake or {}),
    }

    return {
        "mode": "service_delivery",
        "customer_id": customer_id,
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "intake_received": bool(intake),
        "workflow": build_service_workflow(service_id),
        "delivery_template": delivery_template_by_service.get(
            service_id, build_24h_delivery_plan(service_id),
        ),
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_sla_status_for_delivery(
    *,
    customer_id: str = "",
    open_tickets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute SLA health for a customer's open delivery tickets."""
    health = build_sla_health_report(tickets=open_tickets)
    breaches: list[dict[str, Any]] = []
    for t in (open_tickets or []):
        b = classify_sla_breach(
            priority=str(t.get("priority", "P3")),
            minutes_to_first_response=t.get("first_response_min"),
            hours_to_resolve=t.get("resolution_hours"),
        )
        if b["breached"]:
            breaches.append({**t, "breach": b})
    return {
        "customer_id": customer_id,
        "health": health,
        "breaches": breaches,
        "approval_required": True,
    }


def build_post_delivery_handoff(
    *,
    customer_id: str = "",
    service_id: str = "",
    delivered_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the post-delivery handoff (Arabic) → Customer Success cadence."""
    metrics = delivered_metrics or {}
    return {
        "mode": "service_delivery",
        "customer_id": customer_id,
        "service_id": service_id,
        "delivered_metrics": dict(metrics),
        "handoff_steps_ar": [
            "تسليم Proof Pack النهائي للعميل + اعتماده.",
            "حجز جلسة مراجعة 30 دقيقة.",
            "تفعيل Customer Success cadence (weekly check-ins).",
            "اقتراح الترقية المنطقية بناءً على النتائج.",
            "تحديث Action Graph + Revenue Work Units.",
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }
