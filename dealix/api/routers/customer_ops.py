"""Customer ops API — onboarding, SLA, connectors (deterministic)."""

from __future__ import annotations

from fastapi import APIRouter, Body

from auto_client_acquisition.customer_ops.connector_setup_status import build_connector_status
from auto_client_acquisition.customer_ops.customer_success_cadence import build_weekly_cadence
from auto_client_acquisition.customer_ops.incident_router import build_incident_playbook, classify_incident
from auto_client_acquisition.customer_ops.onboarding_checklist import build_onboarding_checklist
from auto_client_acquisition.customer_ops.sla_tracker import build_sla_summary
from auto_client_acquisition.customer_ops.support_ticket_router import route_ticket

router = APIRouter(prefix="/api/v1/customer-ops", tags=["customer-ops"])


@router.get("/onboarding/checklist")
async def onboarding_checklist(service_id: str | None = None) -> dict[str, object]:
    return build_onboarding_checklist(service_id)


@router.get("/support/sla")
async def support_sla() -> dict[str, object]:
    return build_sla_summary()


@router.get("/connectors/status")
async def connectors_status() -> dict[str, object]:
    return build_connector_status()


@router.get("/success/cadence")
async def success_cadence() -> dict[str, object]:
    return build_weekly_cadence()


@router.get("/incidents/playbook")
async def incidents_playbook() -> dict[str, object]:
    return build_incident_playbook()


@router.post("/support/route")
async def support_route(payload: dict[str, object] = Body(default_factory=dict)) -> dict[str, object]:
    issue = str(payload.get("issue_ar") or "")
    return route_ticket(issue)


@router.get("/incidents/classify")
async def incidents_classify(severity: str = "P3") -> dict[str, object]:
    return classify_incident(severity)
