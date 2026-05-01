"""Customer Ops router — onboarding + connectors + support + SLA + incidents."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.customer_ops import (
    SUPPORT_PRIORITIES,
    SUPPORTED_CONNECTORS,
    build_at_risk_alert,
    build_connector_setup_summary,
    build_customer_success_plan,
    build_first_response_template,
    build_incident_response_plan,
    build_onboarding_checklist,
    build_sla_health_report,
    build_weekly_check_in,
    classify_sla_breach,
    classify_ticket_priority,
    record_sla_event,
    route_ticket,
    triage_incident,
    update_connector_status,
    update_onboarding_step,
)

router = APIRouter(prefix="/api/v1/customer-ops", tags=["customer-ops"])


# ── Onboarding ───────────────────────────────────────────────
@router.post("/onboarding/checklist")
async def onboarding_checklist(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_onboarding_checklist(
        customer_id=payload.get("customer_id", ""),
        company_name=payload.get("company_name", ""),
        bundle_id=payload.get("bundle_id"),
    )


@router.post("/onboarding/update-step")
async def onboarding_update_step(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return update_onboarding_step(
        payload.get("checklist") or {},
        step_id=payload.get("step_id", ""),
        completed=bool(payload.get("completed", True)),
        notes=payload.get("notes", ""),
    )


@router.get("/onboarding/checklist/demo")
async def onboarding_checklist_demo() -> dict[str, Any]:
    return build_onboarding_checklist(
        customer_id="demo", company_name="شركة نمو للتدريب",
        bundle_id="growth_starter",
    )


# ── Connectors ───────────────────────────────────────────────
@router.get("/connectors/catalog")
async def connectors_catalog() -> dict[str, Any]:
    return {
        "total": len(SUPPORTED_CONNECTORS),
        "connectors": [dict(c) for c in SUPPORTED_CONNECTORS],
    }


@router.post("/connectors/summary")
async def connectors_summary(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_connector_setup_summary(
        customer_id=payload.get("customer_id", ""),
        statuses=payload.get("statuses"),
    )


@router.post("/connectors/update")
async def connectors_update(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    statuses = payload.get("statuses") or {}
    try:
        return {"statuses": update_connector_status(
            statuses,
            connector_key=payload.get("connector_key", ""),
            state=payload.get("state", "not_started"),
            notes=payload.get("notes", ""),
        )}
    except ValueError as exc:
        return {"error": str(exc)}


@router.get("/connectors/demo")
async def connectors_demo() -> dict[str, Any]:
    return build_connector_setup_summary(
        customer_id="demo",
        statuses={
            "gmail": {"state": "connected_draft_only"},
            "google_calendar": {"state": "connected_draft_only"},
            "moyasar": {"state": "configuring"},
            "whatsapp_cloud": {"state": "not_started"},
        },
    )


# ── Support ──────────────────────────────────────────────────
@router.get("/support/priorities")
async def support_priorities() -> dict[str, Any]:
    return {"priorities": [dict(p) for p in SUPPORT_PRIORITIES]}


@router.post("/support/classify")
async def support_classify(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return classify_ticket_priority(payload.get("text", ""))


@router.post("/support/route")
async def support_route(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return route_ticket(
        text=payload.get("text", ""),
        customer_id=payload.get("customer_id", ""),
        contact_email=payload.get("contact_email", ""),
    )


@router.get("/support/first-response/{priority}")
async def support_first_response(priority: str) -> dict[str, Any]:
    return build_first_response_template(priority)


# ── SLA ──────────────────────────────────────────────────────
@router.post("/sla/event")
async def sla_event(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return record_sla_event(
            ticket_id=payload.get("ticket_id", ""),
            priority=payload.get("priority", "P3"),
            event=payload.get("event", "opened"),
        )
    except ValueError as exc:
        return {"error": str(exc)}


@router.post("/sla/classify-breach")
async def sla_classify_breach(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return classify_sla_breach(
        priority=payload.get("priority", "P3"),
        minutes_to_first_response=payload.get("minutes_to_first_response"),
        hours_to_resolve=payload.get("hours_to_resolve"),
    )


@router.post("/sla/health-report")
async def sla_health_report(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_sla_health_report(tickets=payload.get("tickets") or [])


@router.get("/sla/health-report/demo")
async def sla_health_report_demo() -> dict[str, Any]:
    return build_sla_health_report(tickets=[
        {"priority": "P0", "first_response_min": 12, "resolution_hours": 2.5},
        {"priority": "P1", "first_response_min": 90, "resolution_hours": 18},
        {"priority": "P2", "first_response_min": 600, "resolution_hours": 70},
        {"priority": "P3", "first_response_min": 1200, "resolution_hours": 100},
    ])


# ── Incidents ────────────────────────────────────────────────
@router.post("/incidents/triage")
async def incidents_triage(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return triage_incident(
        title=payload.get("title", ""),
        description=payload.get("description", ""),
        affected_customers=int(payload.get("affected_customers", 1)),
        has_data_leak=bool(payload.get("has_data_leak", False)),
        has_unauthorized_send=bool(payload.get("has_unauthorized_send", False)),
    )


@router.get("/incidents/response-plan/{severity}")
async def incidents_response_plan(severity: str) -> dict[str, Any]:
    return build_incident_response_plan(severity=severity)


# ── Customer Success ─────────────────────────────────────────
@router.post("/cs/weekly-check-in")
async def cs_weekly_check_in(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_weekly_check_in(
        customer_id=payload.get("customer_id", ""),
        company_name=payload.get("company_name", ""),
        metrics=payload.get("metrics"),
    )


@router.post("/cs/at-risk-alert")
async def cs_at_risk_alert(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_at_risk_alert(
        customer_id=payload.get("customer_id", ""),
        days_inactive=int(payload.get("days_inactive", 0)),
        drafts_pending=int(payload.get("drafts_pending", 0)),
        last_proof_pack_days_ago=int(payload.get("last_proof_pack_days_ago", 0)),
    )


@router.post("/cs/success-plan")
async def cs_success_plan(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_customer_success_plan(
        customer_id=payload.get("customer_id", ""),
        bundle_id=payload.get("bundle_id", "growth_starter"),
    )
