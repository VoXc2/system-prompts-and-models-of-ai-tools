"""Role-based Revenue Command Cards API — feeds + decisions (draft/approval-first)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from auto_client_acquisition.revenue_company_os.card_factory import (
    build_role_command_feed,
    build_whatsapp_daily_brief_lines,
)
from auto_client_acquisition.revenue_company_os.cards import (
    UserRole,
    is_known_role,
    normalize_role_param,
)

router = APIRouter(prefix="/api/v1/cards", tags=["revenue-command-cards"])

# Demo-only: in-process decision log (not durable storage).
_decision_log: dict[str, dict[str, Any]] = {}


class CardDecisionBody(BaseModel):
    """Human decision on a card — never triggers live channel send."""

    action: str | None = Field(None, description="approve | edit | skip")
    button_action: str | None = Field(None, description="machine key from pressed button")
    note: str | None = Field(None, max_length=2000)


def _find_card(card_id: str) -> dict[str, Any] | None:
    for role in UserRole:
        for c in build_role_command_feed(role.value)["cards"]:
            if str(c.get("card_id")) == card_id:
                return c
    return None


def _allowed_roles() -> list[str]:
    return [e.value for e in UserRole]


@router.get("/feed")
async def get_card_feed(role: str = Query("ceo", description="ceo | sales_manager | growth_manager | ...")) -> dict[str, Any]:
    nr = normalize_role_param(role)
    if not is_known_role(nr):
        raise HTTPException(
            status_code=400,
            detail={"error": "unknown_role", "allowed": _allowed_roles()},
        )
    return build_role_command_feed(nr)


@router.get("/whatsapp/daily-brief")
async def get_whatsapp_daily_brief(
    role: str = Query("ceo", description="Role for brief lines (still approval-first)"),
) -> dict[str, Any]:
    """Compact lines for WhatsApp-style surfaces — no auto-send."""
    nr = normalize_role_param(role)
    if not is_known_role(nr):
        raise HTTPException(
            status_code=400,
            detail={"error": "unknown_role", "allowed": _allowed_roles()},
        )
    return {
        "role": nr,
        "lines_ar": build_whatsapp_daily_brief_lines(nr),
        "demo": True,
        "no_auto_send": True,
    }


@router.post("/{card_id}/decision")
async def post_card_decision(card_id: str, body: CardDecisionBody) -> dict[str, Any]:
    card = _find_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail={"error": "unknown_card_id"})

    base_proof = list(card.get("proof_impact") or [])
    extra: list[str] = ["decision_recorded"]
    if body.button_action:
        extra.append(f"button:{body.button_action}")
    if body.action:
        extra.append(f"action:{body.action}")
    proof_events = base_proof + extra

    record = {
        "card_id": card_id,
        "role": card.get("role"),
        "action": body.action,
        "button_action": body.button_action,
        "note": body.note,
        "proof_events": proof_events,
        "execution_mode": "draft_only",
        "draft_export_ar": (
            "مسودة تنفيذية: راجع المحتوى ثم نفّذ يدوياً عبر قناتك المعتمدة. "
            "لا يُرسل Dealix نيابةً عنك في وضع Paid Beta الحالي."
        ),
    }
    _decision_log[card_id] = record

    return {
        "card_id": card_id,
        "status": "logged",
        "proof_events": proof_events,
        "execution_mode": record["execution_mode"],
        "draft_export_ar": record["draft_export_ar"],
        "demo": True,
    }
