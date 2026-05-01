"""Tool execution facade — never performs live external I/O."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.platform_services.action_ledger import get_action_ledger
from auto_client_acquisition.platform_services.action_policy import evaluate_action

_SUPPORTED = frozenset(
    {
        "send_message",
        "create_payment_draft",
        "moyasar_charge",
        "moyasar_payment_link",
        "ingest_lead",
        "render_whatsapp_template_preview",
        "gmail_draft",
        "gmail_send",
        "calendar_draft",
        "calendar_insert",
        "google_meet_transcript_read",
        "social_reply",
    }
)


def execute_tool(tool_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Returns one of: ``draft_created``, ``blocked``, ``approval_required``, ``unsupported``.
    Never calls HTTP, SMTP, or WhatsApp APIs.
    """
    body = payload or {}
    ledger = get_action_ledger()

    if tool_name not in _SUPPORTED:
        ledger.append_decision(tool=tool_name, outcome="unsupported", detail=body)
        return {"status": "unsupported", "tool": tool_name, "approval_required": False}

    if tool_name == "send_message":
        channel = str(body.get("channel_id") or "email")
        action = str(body.get("action") or "external_send")
        pol = evaluate_action(
            action=action,
            channel_id=channel,
            context=body.get("context") if isinstance(body.get("context"), dict) else {},
        )
        if pol["state"] == "blocked":
            ledger.append_decision(tool=tool_name, outcome="blocked", detail={"policy": pol})
            return {"status": "blocked", "tool": tool_name, "policy": pol, "approval_required": False}
        if pol["state"] in ("approval_required", "review"):
            ledger.append_decision(tool=tool_name, outcome="approval_required", detail={"policy": pol})
            return {
                "status": "approval_required",
                "tool": tool_name,
                "policy": pol,
                "approval_required": True,
            }
        ledger.append_decision(tool=tool_name, outcome="draft_created", detail={"policy": pol})
        return {
            "status": "draft_created",
            "tool": tool_name,
            "draft": {"channel_id": channel, "preview_ar": "مسودة داخلية — لا إرسال."},
            "approval_required": False,
        }

    if tool_name in ("create_payment_draft", "moyasar_charge"):
        pol = evaluate_action(
            action="moyasar_charge",
            channel_id="moyasar",
            context={"user_confirmed": body.get("user_confirmed"), "amount_halalas": body.get("amount_halalas")},
        )
        ledger.append_decision(tool=tool_name, outcome=pol["state"], detail={"policy": pol})
        return {
            "status": "approval_required" if pol["state"] != "blocked" else "blocked",
            "tool": tool_name,
            "policy": pol,
            "approval_required": pol["state"] != "blocked",
        }

    if tool_name == "moyasar_payment_link":
        ledger.append_decision(tool=tool_name, outcome="draft_created", detail=body)
        return {
            "status": "draft_created",
            "tool": tool_name,
            "draft": {"type": "payment_link_placeholder", "approval_required": True},
            "approval_required": False,
        }

    if tool_name == "gmail_draft":
        ledger.append_decision(tool=tool_name, outcome="draft_created", detail=body)
        return {"status": "draft_created", "tool": tool_name, "approval_required": False}

    if tool_name == "gmail_send":
        ledger.append_decision(tool=tool_name, outcome="blocked", detail={"reason": "gmail_send_blocked_by_default"})
        return {
            "status": "blocked",
            "tool": tool_name,
            "policy": {"state": "blocked", "reason_ar": "إرسال Gmail معطّل افتراضياً — استخدم مسودة + موافقة لاحقاً."},
            "approval_required": False,
        }

    if tool_name == "calendar_draft":
        ledger.append_decision(tool=tool_name, outcome="draft_created", detail=body)
        return {"status": "draft_created", "tool": tool_name, "approval_required": False}

    if tool_name == "calendar_insert":
        ledger.append_decision(tool=tool_name, outcome="approval_required", detail=body)
        return {
            "status": "approval_required",
            "tool": tool_name,
            "policy": {"state": "approval_required", "reason_ar": "إدراج حدث تقويم يحتاج موافقة صريحة."},
            "approval_required": True,
        }

    if tool_name == "google_meet_transcript_read":
        ledger.append_decision(tool=tool_name, outcome="approval_required", detail=body)
        return {
            "status": "approval_required",
            "tool": tool_name,
            "policy": {"state": "approval_required", "reason_ar": "قراءة transcript تتطلب OAuth ونطاقات صريحة."},
            "approval_required": True,
        }

    if tool_name == "social_reply":
        ledger.append_decision(tool=tool_name, outcome="approval_required", detail=body)
        return {
            "status": "approval_required",
            "tool": tool_name,
            "policy": {"state": "approval_required", "reason_ar": "رد السوشيال يتطلب صلاحية قناة وموافقة."},
            "approval_required": True,
        }

    if tool_name in ("ingest_lead", "render_whatsapp_template_preview"):
        ledger.append_decision(tool=tool_name, outcome="draft_created", detail=body)
        return {"status": "draft_created", "tool": tool_name, "approval_required": False}

    return {"status": "unsupported", "tool": tool_name, "approval_required": False}
