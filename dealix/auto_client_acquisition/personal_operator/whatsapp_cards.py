"""WhatsApp Cloud API–style interactive payloads (generation only — no send)."""

from __future__ import annotations

import re
from typing import Any


def _interactive_buttons(buttons: list[dict[str, str]]) -> dict[str, Any]:
    if len(buttons) > 3:
        msg = "WhatsApp interactive reply buttons allow at most 3 buttons"
        raise ValueError(msg)
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": ""},
            "action": {"buttons": [{"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}} for b in buttons]},
        },
    }


def build_opportunity_buttons(opportunity: dict[str, Any]) -> dict[str, Any]:
    """First-step message: قبول / تخطي / رسالة (maps to draft flow)."""
    oid = str(opportunity.get("id", "unknown"))
    return _interactive_buttons(
        [
            {"id": f"opp:{oid}:accept", "title": "قبول"},
            {"id": f"opp:{oid}:skip", "title": "تخطي"},
            {"id": f"opp:{oid}:draft", "title": "رسالة"},
        ]
    )


def build_second_step_message_buttons(draft_id: str) -> dict[str, Any]:
    """After user taps رسالة — اعتماد / تعديل / إلغاء."""
    return _interactive_buttons(
        [
            {"id": f"msg:{draft_id}:approve", "title": "اعتماد"},
            {"id": f"msg:{draft_id}:edit", "title": "تعديل"},
            {"id": f"msg:{draft_id}:cancel", "title": "إلغاء"},
        ]
    )


def build_daily_brief_message(brief: dict[str, Any]) -> dict[str, Any]:
    """Single card summarizing brief; buttons for next actions."""
    greeting = str(brief.get("greeting", "موجزك اليومي"))
    payload = _interactive_buttons(
        [
            {"id": "brief:show_opportunities", "title": "الفرص"},
            {"id": "brief:launch_report", "title": "الجاهزية"},
            {"id": "brief:dismiss", "title": "لاحقاً"},
        ]
    )
    payload["interactive"]["body"] = {"text": greeting[:1024]}
    return payload


def parse_button_reply(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse inbound webhook-style payload with reply id."""
    button_id = ""
    if "button" in payload and isinstance(payload["button"], dict):
        button_id = str(payload["button"].get("payload", "") or payload["button"].get("id", ""))
    elif "interactive" in payload:
        inter = payload.get("interactive") or {}
        btn = inter.get("button_reply") or inter.get("list_reply") or {}
        button_id = str(btn.get("id", ""))
    if not button_id:
        return {"ok": False, "error": "no_button_id"}

    if m := re.match(r"^opp:([^:]+):(accept|skip|draft|schedule|needs_research)$", button_id):
        return {"ok": True, "kind": "opportunity", "opportunity_id": m.group(1), "action": m.group(2)}
    if m := re.match(r"^msg:([^:]+):(approve|edit|cancel)$", button_id):
        return {"ok": True, "kind": "message_draft", "draft_id": m.group(1), "action": m.group(2)}
    if m := re.match(r"^brief:(show_opportunities|launch_report|dismiss)$", button_id):
        return {"ok": True, "kind": "brief", "action": m.group(1)}
    return {"ok": False, "error": "unknown_button_id", "raw": button_id}
