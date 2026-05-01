"""WhatsApp drafts — opt-in first, no cold outbound by default."""

from __future__ import annotations

from typing import Any


def whatsapp_do_not_do() -> list[str]:
    return ["cold_broadcast", "purchased_list_upload_send", "auto_reply_without_policy", "skip_opt_in"]


def requires_opt_in(contact: dict[str, Any]) -> bool:
    src = str(contact.get("source") or "").lower()
    if contact.get("opt_in_whatsapp") in (True, "true", "1", 1):
        return False
    return src not in ("inbound_lead", "prior_customer", "crm_customer", "explicit_consent")


def draft_whatsapp_message(contact: dict[str, Any], offer: str, why_now: str) -> dict[str, Any]:
    return {
        "message_ar": f"هلا، بخصوص {why_now}: نقدّم {offer} بمسار موافقة. تفضّلون ملخص سطرين؟",
        "approval_required": True,
        "demo": True,
    }


def score_whatsapp_risk(contact: dict[str, Any], message: str) -> dict[str, Any]:
    risk = 30 if requires_opt_in(contact) else 10
    if contact.get("cold_whatsapp"):
        risk = 100
    if "ضمان" in message:
        risk = min(100, risk + 25)
    return {"risk_score": risk, "blocked": risk >= 90, "demo": True}


def build_opt_in_request_template(company_name: str) -> dict[str, Any]:
    return {
        "template_ar": (
            f"مرحباً، نحن {company_name}. نرسل تحديثات قصيرة عبر واتساب حول [الموضوع]. "
            "الرد بـ «نعم» يعني موافقتك. «لا» توقف الرسائل."
        ),
        "approval_required": True,
        "demo": True,
    }
