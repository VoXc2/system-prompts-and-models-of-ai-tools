"""Platform Services router — channel registry + events + inbox + policy + proof."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Query

from auto_client_acquisition.platform_services import (
    ALL_CHANNELS,
    POLICY_RULES,
    SELLABLE_SERVICES,
    build_card_from_event,
    build_demo_feed,
    build_demo_platform_proof,
    evaluate_action,
    get_channel,
    invoke_tool,
    list_services,
    make_event,
    resolve_identity,
)
from auto_client_acquisition.platform_services.action_ledger import ActionLedger
from auto_client_acquisition.platform_services.channel_registry import channels_summary

router = APIRouter(prefix="/api/v1/platform", tags=["platform-services"])

_LEDGER = ActionLedger()


# ── Catalog ────────────────────────────────────────────────────
@router.get("/services/catalog")
async def services_catalog() -> dict[str, Any]:
    return list_services()


@router.get("/channels")
async def channels() -> dict[str, Any]:
    return {
        "summary": channels_summary(),
        "channels": [
            {
                "key": c.key, "label_ar": c.label_ar, "label_en": c.label_en,
                "capabilities": list(c.capabilities), "beta_status": c.beta_status,
                "required_permissions": list(c.required_permissions),
                "allowed_actions": list(c.allowed_actions),
                "blocked_actions": list(c.blocked_actions),
                "risk_level": c.risk_level, "notes_ar": c.notes_ar,
            }
            for c in ALL_CHANNELS
        ],
    }


@router.get("/channels/{channel_key}")
async def channel_detail(channel_key: str) -> dict[str, Any]:
    c = get_channel(channel_key)
    if c is None:
        return {"error": f"unknown channel: {channel_key}"}
    return {
        "key": c.key, "label_ar": c.label_ar, "label_en": c.label_en,
        "capabilities": list(c.capabilities), "beta_status": c.beta_status,
        "required_permissions": list(c.required_permissions),
        "allowed_actions": list(c.allowed_actions),
        "blocked_actions": list(c.blocked_actions),
        "risk_level": c.risk_level, "notes_ar": c.notes_ar,
    }


# ── Policy ─────────────────────────────────────────────────────
@router.get("/policy/rules")
async def policy_rules() -> dict[str, Any]:
    return {"count": len(POLICY_RULES), "rules": POLICY_RULES}


@router.post("/actions/evaluate")
async def actions_evaluate(
    action: str = Body(..., embed=True),
    context: dict[str, Any] = Body(default_factory=dict, embed=True),
) -> dict[str, Any]:
    d = evaluate_action(action=action, context=context)
    return {
        "decision": d.decision,
        "matched_rule_id": d.matched_rule_id,
        "reasons_ar": d.reasons_ar,
        "suggested_next_action_ar": d.suggested_next_action_ar,
    }


@router.post("/actions/approve")
async def actions_approve(
    customer_id: str = Body(..., embed=True),
    action_type: str = Body(..., embed=True),
    channel: str = Body(..., embed=True),
    actor: str = Body(default="user", embed=True),
    payload: dict[str, Any] = Body(default_factory=dict, embed=True),
    correlation_id: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    entry = _LEDGER.append(
        customer_id=customer_id,
        action_type=action_type,
        channel=channel,
        stage="approved",
        actor=actor,
        payload=payload,
        correlation_id=correlation_id,
    )
    return {"approved": True, "entry": entry.to_dict()}


@router.get("/ledger/summary")
async def ledger_summary(customer_id: str = Query(...)) -> dict[str, Any]:
    return _LEDGER.summary(customer_id=customer_id)


# ── Events + Inbox ─────────────────────────────────────────────
@router.post("/events/ingest")
async def events_ingest(
    event_type: str = Body(..., embed=True),
    channel: str = Body(..., embed=True),
    customer_id: str = Body(..., embed=True),
    payload: dict[str, Any] = Body(default_factory=dict, embed=True),
) -> dict[str, Any]:
    try:
        evt = make_event(
            event_type=event_type, channel=channel,
            customer_id=customer_id, payload=payload,
        )
    except ValueError as exc:
        return {"error": str(exc)}
    card = build_card_from_event(evt)
    return {
        "event": evt.to_dict(),
        "card": card.to_dict() if card else None,
        "actionable": card is not None,
    }


@router.get("/inbox/feed")
async def inbox_feed() -> dict[str, Any]:
    """Demo unified-inbox feed; production version reads from event store."""
    return build_demo_feed()


# ── Identity + Tool gateway ───────────────────────────────────
@router.post("/identity/resolve")
async def identity_resolve(
    signals: list[dict[str, Any]] = Body(..., embed=True),
) -> dict[str, Any]:
    out = resolve_identity(signals=signals)
    return {
        "identity_id": out.identity_id,
        "primary_phone": out.primary_phone,
        "primary_email": out.primary_email,
        "company": out.company,
        "crm_id": out.crm_id,
        "social_handles": out.social_handles,
        "confidence": out.confidence,
        "sources": out.sources,
    }


@router.get("/identity/resolve-demo")
async def identity_resolve_demo() -> dict[str, Any]:
    """Sample multi-source identity resolution."""
    out = resolve_identity(signals=[
        {"phone": "+966500000001", "company": "شركة العقار الذهبي", "source": "whatsapp"},
        {"email": "ali@example.sa", "company": "شركة العقار الذهبي", "source": "gmail"},
        {"crm_id": "crm_5421", "company": "شركة العقار الذهبي", "source": "crm"},
        {"social_handles": {"linkedin": "ali-realestate"}, "source": "linkedin_lead_forms"},
    ])
    return {
        "identity_id": out.identity_id,
        "primary_phone": out.primary_phone,
        "primary_email": out.primary_email,
        "company": out.company,
        "crm_id": out.crm_id,
        "social_handles": out.social_handles,
        "confidence": out.confidence,
        "sources": out.sources,
    }


@router.post("/tools/invoke")
async def tools_invoke(
    tool: str = Body(..., embed=True),
    payload: dict[str, Any] = Body(default_factory=dict, embed=True),
    context: dict[str, Any] = Body(default_factory=dict, embed=True),
) -> dict[str, Any]:
    r = invoke_tool(tool=tool, payload=payload, context=context)
    return {
        "status": r.status,
        "tool": r.tool,
        "matched_policy_rule": r.matched_policy_rule,
        "reasons_ar": r.reasons_ar,
        "next_action_ar": r.next_action_ar,
    }


# ── Proof ──────────────────────────────────────────────────────
@router.get("/proof-ledger/demo")
async def proof_ledger_demo() -> dict[str, Any]:
    return build_demo_platform_proof().to_dict()
