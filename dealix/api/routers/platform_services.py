"""Platform Services API — Growth Control Tower (no live external sends)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.platform_services import (
    build_proof_summary,
    evaluate_action,
    event_to_inbox_card,
    execute_tool,
    get_action_ledger,
    get_service_catalog,
    list_channels,
    validate_event,
)
from auto_client_acquisition.innovation.proof_ledger import build_demo_proof_ledger
from auto_client_acquisition.platform_services.contact_import_preview import build_import_preview
from auto_client_acquisition.platform_services.identity_resolution import resolve_identity_demo
from auto_client_acquisition.platform_services.inbox_feed import build_inbox_feed
from auto_client_acquisition.platform_services.lead_form_ingest import ingest_lead_form
from auto_client_acquisition.platform_services.proof_overview import build_proof_overview

router = APIRouter(prefix="/api/v1/platform", tags=["platform_services"])


@router.get("/service-catalog")
async def service_catalog() -> dict[str, Any]:
    return get_service_catalog()


@router.get("/services/catalog")
async def services_catalog_alias() -> dict[str, Any]:
    """Alias path for product docs compatibility."""
    return get_service_catalog()


@router.get("/channels")
async def channels() -> dict[str, Any]:
    return list_channels()


@router.post("/events/validate")
async def events_validate(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return validate_event(payload or {})


@router.post("/events/ingest")
async def events_ingest(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Validate normalized event and return inbox card — no persistence."""
    v = validate_event(payload or {})
    if not v["valid"]:
        return {"ok": False, "errors": v["errors"], "approval_required": True}
    ev = v.get("normalized") or {}
    return {"ok": True, "event": ev, "card": event_to_inbox_card(ev), "approval_required": True}


@router.post("/actions/approve")
async def actions_approve(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Record human approval/rejection in the in-memory action ledger — no live side effects."""
    ledger = get_action_ledger()
    action_id = str(payload.get("action_id") or payload.get("request_id") or "unspecified")
    actor = str(payload.get("actor") or "operator")
    approved = payload.get("approved")
    is_approved = True if approved is None else bool(approved)
    entry = ledger.append_decision(
        tool="human_approval",
        outcome="approved" if is_approved else "rejected",
        detail={
            "action_id": action_id,
            "actor": actor,
            "notes": payload.get("notes"),
        },
    )
    return {
        "ok": True,
        "ledger_entry": entry,
        "detail_ar": "سُجّل القرار في دفتر MVP — لا يُطلق إرسالاً أو دفعاً تلقائياً من هذا المسار.",
        "approval_required": False,
    }


@router.post("/actions/evaluate")
async def actions_evaluate_alias(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Alias of ``POST /policy/evaluate`` for docs that refer to ``actions/evaluate``."""
    return evaluate_action(
        action=str(payload.get("action") or ""),
        channel_id=str(payload.get("channel_id") or ""),
        context=payload.get("context") if isinstance(payload.get("context"), dict) else {},
    )


@router.post("/inbox/from-event")
async def inbox_from_event(
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    event = payload.get("event") if isinstance(payload.get("event"), dict) else payload
    merge = bool(payload.get("merge_demo_hint"))
    return {"card": event_to_inbox_card(event or {}, merge_demo_hint=merge)}


@router.post("/policy/evaluate")
async def policy_evaluate(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return evaluate_action(
        action=str(payload.get("action") or ""),
        channel_id=str(payload.get("channel_id") or ""),
        context=payload.get("context") if isinstance(payload.get("context"), dict) else {},
    )


@router.post("/tools/execute")
async def tools_execute(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return execute_tool(str(payload.get("tool_name") or ""), payload.get("payload") if isinstance(payload.get("payload"), dict) else {})


@router.get("/proof/summary")
async def proof_summary() -> dict[str, Any]:
    return build_proof_summary()


@router.get("/proof-ledger/demo")
async def proof_ledger_demo() -> dict[str, Any]:
    """Demo ledger events — same source as innovation demo."""
    return build_demo_proof_ledger()


@router.get("/identity/resolve-demo")
async def identity_resolve_demo(
    phone: str | None = None,
    email: str | None = None,
    company_hint: str | None = None,
) -> dict[str, Any]:
    return resolve_identity_demo(phone=phone, email=email, company_hint=company_hint)


@router.get("/proof/overview")
async def proof_overview() -> dict[str, Any]:
    return build_proof_overview()


@router.get("/inbox/feed")
async def inbox_feed() -> dict[str, Any]:
    return build_inbox_feed()


@router.post("/contacts/import-preview")
async def contacts_import_preview(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_import_preview(body or {})


@router.get("/action-ledger/recent")
async def action_ledger_recent(limit: int = 50) -> dict[str, Any]:
    lim = max(1, min(limit, 200))
    return {"entries": get_action_ledger().recent(lim)}


@router.post("/ingest/lead-form")
async def ingest_lead_form_route(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return ingest_lead_form(body or {})


# --- Wave 4: draft payloads only (re-export from aca.integrations) ---


@router.post("/integrations/gmail/draft")
async def gmail_draft(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    from auto_client_acquisition.integrations.gmail_operator import build_gmail_draft_payload

    return build_gmail_draft_payload(payload or {})


@router.post("/integrations/calendar/draft")
async def calendar_draft(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    from auto_client_acquisition.integrations.calendar_operator import build_calendar_draft_payload

    return build_calendar_draft_payload(payload or {})


@router.post("/integrations/moyasar/payment-draft")
async def moyasar_payment_draft(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    from auto_client_acquisition.integrations.moyasar_draft import build_moyasar_payment_draft

    return build_moyasar_payment_draft(payload or {})
