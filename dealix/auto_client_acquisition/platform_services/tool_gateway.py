"""
Safe Tool Gateway — single chokepoint for every external action.

Returns one of: draft_created / approval_required / blocked /
ready_for_adapter / unsupported. Never executes a live action here;
the actual API call (Gmail/Calendar/WhatsApp/Moyasar/...) happens in
the dedicated adapter that's gated by an explicit env flag.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.platform_services.action_policy import evaluate_action
from auto_client_acquisition.platform_services.channel_registry import get_channel


SUPPORTED_TOOLS: tuple[str, ...] = (
    # Gmail / Email
    "gmail.create_draft",
    "gmail.read_thread",
    # Calendar
    "calendar.draft_event",
    "calendar.insert_event",
    # WhatsApp
    "whatsapp.send_message",
    "whatsapp.draft_message",
    # Moyasar
    "moyasar.create_payment_link",
    "moyasar.create_invoice",
    "moyasar.refund",
    # Social
    "social.post",
    "social.send_dm",
    # Sheets / CRM
    "sheets.append_row",
    "crm.update_deal_stage",
    # Reviews
    "gbp.reply_review",
    "gbp.publish_post",
)


@dataclass
class GatewayResult:
    """Outcome of a tool invocation through the gateway."""

    status: str                    # draft_created / approval_required / blocked
                                   # / ready_for_adapter / unsupported
    tool: str
    matched_policy_rule: str | None = None
    reasons_ar: list[str] = field(default_factory=list)
    next_action_ar: str = ""
    payload_passthrough: dict[str, Any] | None = None


# ── Live-execution flag — defaults to OFF ───────────────────────
def _live_send_allowed(channel: str) -> bool:
    """Each channel has its own env flag; OFF by default everywhere."""
    flag_map = {
        "whatsapp": "WHATSAPP_ALLOW_LIVE_SEND",
        "gmail": "GMAIL_ALLOW_LIVE_SEND",
        "google_calendar": "CALENDAR_ALLOW_LIVE_INSERT",
        "moyasar": "MOYASAR_ALLOW_LIVE_CHARGE",
        "social": "SOCIAL_ALLOW_LIVE_POST",
        "x_api": "SOCIAL_ALLOW_LIVE_POST",
        "instagram_graph": "SOCIAL_ALLOW_LIVE_POST",
        "google_business_profile": "GBP_ALLOW_LIVE_REPLY",
    }
    flag = flag_map.get(channel)
    if not flag:
        return False
    return os.environ.get(flag, "false").lower() in ("1", "true", "yes")


# ── Public API ──────────────────────────────────────────────────
def invoke_tool(
    *,
    tool: str,
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> GatewayResult:
    """
    Single entry point for every tool action.

    Flow: validate tool name → map to policy action → evaluate policy
    → check live-send flag → return GatewayResult (never throws on
    business-logic failures).
    """
    if tool not in SUPPORTED_TOOLS:
        return GatewayResult(
            status="unsupported",
            tool=tool,
            reasons_ar=[f"الأداة غير مدعومة: {tool}"],
        )

    channel_key = tool.split(".", 1)[0]
    channel = get_channel(_normalize_channel(channel_key))
    payload = payload or {}
    ctx = dict(context or {})
    if "payload" not in ctx:
        ctx["payload"] = payload

    # Map tool → policy action (the granular labels the policy understands)
    action_map: dict[str, str] = {
        "gmail.create_draft": "create_draft",
        "gmail.read_thread": "read_data",
        "calendar.draft_event": "create_draft",
        "calendar.insert_event": "calendar_insert_event",
        "whatsapp.send_message": "send_whatsapp",
        "whatsapp.draft_message": "create_draft",
        "moyasar.create_payment_link": "create_draft",
        "moyasar.create_invoice": "create_draft",
        "moyasar.refund": "charge_payment",
        "social.post": "post_social",
        "social.send_dm": "send_social_dm",
        "sheets.append_row": "create_draft",
        "crm.update_deal_stage": "create_draft",
        "gbp.reply_review": "post_social",
        "gbp.publish_post": "post_social",
    }
    policy_action = action_map.get(tool, "create_draft")

    decision = evaluate_action(action=policy_action, context=ctx)

    if decision.decision == "blocked":
        return GatewayResult(
            status="blocked",
            tool=tool,
            matched_policy_rule=decision.matched_rule_id,
            reasons_ar=decision.reasons_ar,
            next_action_ar=decision.suggested_next_action_ar,
        )
    if decision.decision == "approval_required":
        return GatewayResult(
            status="approval_required",
            tool=tool,
            matched_policy_rule=decision.matched_rule_id,
            reasons_ar=decision.reasons_ar,
            next_action_ar=decision.suggested_next_action_ar,
            payload_passthrough=payload,
        )

    # decision == "allow" → check live-send flag for the channel
    if _is_external_send(tool):
        if _live_send_allowed(_normalize_channel(channel_key)):
            return GatewayResult(
                status="ready_for_adapter",
                tool=tool,
                reasons_ar=["السياسة موافقة + LIVE flag مفعل — جاهز لـ adapter."],
                payload_passthrough=payload,
            )
        # Default: keep as draft
        return GatewayResult(
            status="draft_created",
            tool=tool,
            reasons_ar=["السياسة موافقة لكن LIVE flag غير مفعل — تم حفظه draft."],
            payload_passthrough=payload,
        )

    return GatewayResult(
        status="draft_created",
        tool=tool,
        reasons_ar=["إجراء داخلي / draft — لا تفاعل خارجي."],
        payload_passthrough=payload,
    )


# ── Helpers ──────────────────────────────────────────────────────
def _normalize_channel(prefix: str) -> str:
    """Channel registry uses dotted keys; tool prefixes use snake."""
    return {
        "calendar": "google_calendar",
        "gbp": "google_business_profile",
        "social": "x_api",  # used as an umbrella prefix
        "sheets": "google_sheets",
    }.get(prefix, prefix)


def _is_external_send(tool: str) -> bool:
    return tool in {
        "whatsapp.send_message",
        "calendar.insert_event",
        "moyasar.create_payment_link",
        "moyasar.create_invoice",
        "moyasar.refund",
        "social.post",
        "social.send_dm",
        "gbp.reply_review",
        "gbp.publish_post",
    }
