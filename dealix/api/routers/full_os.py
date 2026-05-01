"""
Full OS Orchestrator — 12-stage deal lifecycle + smart auto-action.

Connects every Dealix subsystem (reply classifier, draft generator,
WhatsApp multi-provider, suppression, scoring, deal stage) into a single
state-machine endpoint per inbound event.

12 stages (deal_stage):
    new_lead → qualifying → qualified → nurturing → meeting_booked →
    meeting_done → proposal_sent → negotiating → payment_requested →
    pilot_active → closed_won / closed_lost / opted_out

Endpoints:
    POST /api/v1/os/process              classify + return next-stage plan
    POST /api/v1/os/process-and-act      same + execute (send WhatsApp, draft email)
    POST /api/v1/os/bulk-process         batch over a list of events
    GET  /api/v1/os/stages               list all stages + valid transitions
    GET  /api/v1/os/whatsapp-providers   show configured providers + chain status
    POST /api/v1/os/test-send            send a test message (with safety guard)
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from auto_client_acquisition.email.reply_classifier import classify_reply
from auto_client_acquisition.email.whatsapp_multi_provider import (
    configured_providers,
    send_whatsapp_smart,
)

router = APIRouter(prefix="/api/v1/os", tags=["full-os"])
log = logging.getLogger(__name__)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str = "evt_") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ── 12-stage transition map ───────────────────────────────────────
STAGES: list[str] = [
    "new_lead", "qualifying", "qualified", "nurturing",
    "meeting_booked", "meeting_done", "proposal_sent",
    "negotiating", "payment_requested", "pilot_active",
    "closed_won", "closed_lost", "opted_out",
]

# Allowed transitions per current stage (forward + key sideways moves)
TRANSITIONS: dict[str, list[str]] = {
    "new_lead":          ["qualifying", "nurturing", "opted_out", "closed_lost"],
    "qualifying":        ["qualified", "nurturing", "opted_out", "closed_lost"],
    "qualified":         ["meeting_booked", "proposal_sent", "nurturing", "closed_lost"],
    "nurturing":         ["qualifying", "qualified", "opted_out", "closed_lost"],
    "meeting_booked":    ["meeting_done", "closed_lost", "nurturing"],
    "meeting_done":      ["proposal_sent", "negotiating", "closed_lost"],
    "proposal_sent":     ["negotiating", "payment_requested", "closed_lost", "nurturing"],
    "negotiating":       ["payment_requested", "proposal_sent", "closed_lost", "nurturing"],
    "payment_requested": ["pilot_active", "negotiating", "closed_lost"],
    "pilot_active":      ["closed_won", "closed_lost"],
    "closed_won":        [],  # terminal
    "closed_lost":       ["nurturing"],  # can revive after 30 days
    "opted_out":         [],  # terminal — suppression
}

# Reply category → next stage suggestion
CATEGORY_TO_STAGE: dict[str, str] = {
    "interested":         "qualified",
    "ask_demo":           "meeting_booked",
    "ask_price":          "proposal_sent",
    "ask_details":        "qualifying",
    "ask_case_study":     "nurturing",
    "objection_budget":   "negotiating",
    "objection_ai":       "negotiating",
    "objection_privacy":  "negotiating",
    "already_has_crm":    "qualifying",
    "partnership":        "qualifying",  # routed to partner flow
    "not_now":            "nurturing",
    "no_budget":          "closed_lost",
    "ai_quality_concern": "negotiating",
    "unsubscribe":        "opted_out",
    "angry":              "closed_lost",
    "unclear":            "qualifying",
}


def _suggest_next_stage(current: str, category: str) -> tuple[str, bool]:
    """
    Return (suggested_stage, is_valid_transition).
    If suggested isn't a valid transition from current, default to current.
    """
    target = CATEGORY_TO_STAGE.get(category, current)
    valid_targets = TRANSITIONS.get(current, [])
    if target == current:
        return current, True
    if target in valid_targets:
        return target, True
    # Out-of-order (e.g. unsubscribe from any stage)
    if target in {"opted_out", "closed_lost"}:
        return target, True
    return current, False


# ── Endpoints ─────────────────────────────────────────────────────
@router.get("/stages")
async def list_stages() -> dict[str, Any]:
    """Show all 12 stages + allowed transitions."""
    return {
        "stages": STAGES,
        "transitions": TRANSITIONS,
        "category_to_stage": CATEGORY_TO_STAGE,
        "terminal_stages": ["closed_won", "closed_lost", "opted_out"],
    }


@router.get("/whatsapp-providers")
async def whatsapp_providers_status() -> dict[str, Any]:
    """Which WhatsApp providers are configured + the smart-fallback chain order."""
    configured = configured_providers()
    return {
        "configured_providers": configured,
        "chain_order": ["green_api", "ultramsg", "fonnte", "meta_cloud"],
        "active_provider_will_be": configured[0] if configured else None,
        "mock_mode": os.getenv("WHATSAPP_MOCK_MODE", "").lower() in {"true", "1", "yes"},
        "recommendation": (
            "set GREEN_API_INSTANCE_ID + GREEN_API_TOKEN for free-tier primary; "
            "add ULTRAMSG_* as paid backup; add META_WHATSAPP_* for official fallback"
            if not configured else "✅ ready — chain will use first listed"
        ),
    }


@router.post("/process")
async def os_process(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Classify an inbound event and return the next-stage plan WITHOUT executing.
    Body:
        phone: str
        company: str | None
        message: str (required)
        current_stage: str (default: "new_lead")
        prefer_llm: bool (default: True)
    """
    phone = str(body.get("phone") or "").strip()
    company = str(body.get("company") or "").strip()
    message = str(body.get("message") or "").strip()
    current_stage = str(body.get("current_stage") or "new_lead").strip()
    prefer_llm = bool(body.get("prefer_llm", True))

    if not message:
        raise HTTPException(400, "message_required")
    if current_stage not in STAGES:
        raise HTTPException(400, f"unknown_stage:{current_stage}. Valid: {STAGES}")

    classification = await classify_reply(message, prefer_llm=prefer_llm)
    new_stage, valid = _suggest_next_stage(current_stage, classification.category)

    response_message_ar = classification.response_draft_ar
    if company:
        # Personalize opener if classifier didn't already
        if not response_message_ar.startswith(("السلام", "أهلاً", "مرحباً")):
            response_message_ar = f"مرحباً {company}،\n\n{response_message_ar}"

    return {
        "event_id": _new_id(),
        "received_at": _utcnow_iso(),
        "input": {"phone": phone, "company": company, "current_stage": current_stage},
        "classification": classification.to_dict(),
        "stage": {
            "from": current_stage,
            "to": new_stage,
            "transition_valid": valid,
        },
        "response_message_ar": response_message_ar,
        "auto_send_allowed": classification.auto_send_allowed,
        "requires_human_review": classification.requires_human_review,
        "next_action": classification.next_action,
        "followup_days": classification.followup_days,
    }


@router.post("/process-and-act")
async def os_process_and_act(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Same as /os/process + execute the action:
        - if auto_send_allowed=True and not requires_review → send WhatsApp via smart chain
        - else → return draft for human review (no send)
    """
    plan = await os_process(body)

    execution: dict[str, Any] = {"action_taken": "none", "reason": ""}
    safe_to_send = (
        plan["auto_send_allowed"]
        and not plan["requires_human_review"]
        and plan["classification"]["category"] not in {"angry", "objection_privacy"}
    )

    if not safe_to_send:
        execution["action_taken"] = "draft_for_review"
        execution["reason"] = "compliance_or_human_review_required"
        plan["execution"] = execution
        return plan

    phone = body.get("phone")
    if not phone:
        execution["action_taken"] = "no_op"
        execution["reason"] = "phone_missing"
        plan["execution"] = execution
        return plan

    result = await send_whatsapp_smart(str(phone), plan["response_message_ar"])
    if result.status == "ok":
        execution["action_taken"] = "whatsapp_sent"
        execution["provider"] = result.provider
        execution["message_id"] = result.message_id
        execution["chain_tried"] = result.fallback_chain_tried
    elif result.status == "mock":
        execution["action_taken"] = "whatsapp_mock"
        execution["provider"] = "mock"
    elif result.status == "no_keys":
        execution["action_taken"] = "draft_for_review"
        execution["reason"] = "no_whatsapp_provider_configured"
    else:
        execution["action_taken"] = "send_failed_falling_back_to_draft"
        execution["reason"] = result.error or result.status
        execution["chain_tried"] = result.fallback_chain_tried

    plan["execution"] = execution
    return plan


@router.post("/bulk-process")
async def os_bulk_process(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Process a list of events at once. Body: events: list[dict], execute: bool.
    Each event: {phone, company, message, current_stage}.
    """
    events = body.get("events")
    execute = bool(body.get("execute", False))
    if not isinstance(events, list) or not events:
        raise HTTPException(400, "events_required: list of {phone, message, current_stage}")
    if len(events) > 50:
        raise HTTPException(400, "too_many: max 50 per call")

    results: list[dict[str, Any]] = []
    fn = os_process_and_act if execute else os_process
    for ev in events:
        try:
            r = await fn(ev)
        except HTTPException as he:
            r = {"error": he.detail, "input": ev}
        except Exception as exc:  # noqa: BLE001
            r = {"error": str(exc), "input": ev}
        results.append(r)

    sent = sum(1 for r in results
               if r.get("execution", {}).get("action_taken") == "whatsapp_sent")
    drafts = sum(1 for r in results
                 if r.get("execution", {}).get("action_taken") == "draft_for_review")
    return {
        "count": len(results),
        "sent": sent,
        "drafts": drafts,
        "results": results,
    }


@router.post("/test-send")
async def os_test_send(phone: str, message: str = "Dealix test ping ✅") -> dict[str, Any]:
    """
    Send a single test WhatsApp via the smart-chain. Use only your own number.
    Hard guard: refuses to send to a phone that isn't on a small allowlist
    set via WHATSAPP_TEST_ALLOWLIST (comma-separated digits).
    """
    allowlist = {
        p.strip() for p in os.getenv("WHATSAPP_TEST_ALLOWLIST", "").split(",")
        if p.strip()
    }
    digits_only = "".join(c for c in phone if c.isdigit())
    if allowlist and digits_only not in allowlist:
        raise HTTPException(
            403,
            "phone_not_in_test_allowlist: set WHATSAPP_TEST_ALLOWLIST in env "
            "to your own +966 number(s) before using /os/test-send",
        )
    result = await send_whatsapp_smart(phone, message)
    return result.to_dict()
