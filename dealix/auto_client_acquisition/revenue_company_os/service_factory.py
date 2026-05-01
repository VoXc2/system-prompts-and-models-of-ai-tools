"""Service factory — instantiate a service for a customer."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import (
    build_intake_questions,
    build_service_workflow,
    get_service,
    quote_service,
)


def instantiate_service(
    *,
    service_id: str,
    customer_id: str = "",
    company_size: str = "small",
    urgency: str = "normal",
) -> dict[str, Any]:
    """Instantiate a service for a customer + return ready-to-run state."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "customer_id": customer_id,
        "intake": build_intake_questions(service_id),
        "workflow": build_service_workflow(service_id),
        "quote": quote_service(
            service_id, company_size=company_size, urgency=urgency,
        ),
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_service_factory_demo() -> dict[str, Any]:
    """Demo: instantiate the 4 launch-day services for a sample customer."""
    services = [
        "free_growth_diagnostic",
        "list_intelligence",
        "first_10_opportunities_sprint",
        "growth_os_monthly",
    ]
    return {
        "instantiations": [
            instantiate_service(service_id=sid, customer_id="demo")
            for sid in services
        ],
    }
