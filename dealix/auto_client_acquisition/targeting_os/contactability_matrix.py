"""Contactability: safe / needs_review / blocked + action modes — no send."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.contact_source_policy import (
    allowed_channels_for_source,
    classify_source,
    required_review_level,
)


def block_reason_codes() -> dict[str, str]:
    return {
        "opted_out": "المتلقي طلب عدم التواصل.",
        "cold_whatsapp": "واتساب بارد غير مسموح افتراضياً.",
        "unknown_source": "مصدر غير موثّق — يحتاج مراجعة.",
        "purchased_list": "قائمة مشتراة/مكشوفة — محظورة.",
        "no_identifier": "لا هاتف ولا إيميل صالح.",
    }


def evaluate_contactability(contact: dict[str, Any], desired_channel: str | None = None) -> dict[str, Any]:
    """
    Returns status, allowed_action_modes, channels, Arabic explanation.
    ``contact`` may include: source, opted_out, cold_whatsapp, phone, email, opt_in_status.
    """
    if contact.get("opted_out") in (True, "true", "1", 1):
        return _result(
            "blocked",
            "opted_out",
            ["blocked"],
            [],
            "محظور: opt-out ساري.",
        )

    if contact.get("cold_whatsapp") in (True, "true", "1", 1):
        return _result(
            "blocked",
            "cold_whatsapp",
            ["blocked"],
            [],
            "محظور: واتساب بارد — استخدم إيميل أو opt-in صريح.",
        )

    raw_src = str(contact.get("source") or "").lower()
    if raw_src in ("scraped", "purchased_list"):
        return _result(
            "blocked",
            "purchased_list",
            ["blocked"],
            [],
            "محظور: مصدر قائمة غير موثوق أو scraping.",
        )

    src = classify_source(str(contact.get("source") or "unknown_source"))
    if src in ("opt_out",):
        return _result("blocked", "opted_out", ["blocked"], [], "محظور: مصدر opt-out.")

    if src == "cold_list":
        return _result(
            "needs_review",
            "cold_list",
            ["suggest_only", "draft_only", "approval_required"],
            allowed_channels_for_source(src, contact.get("opt_in_status")),
            "قائمة باردة — مسودات بريد فقط تحت مراجعة.",
        )

    opt_in = str(contact.get("opt_in_status") or "")
    phone = str(contact.get("phone") or contact.get("mobile") or "").strip()
    email = str(contact.get("email") or "").strip()
    if not phone and not email:
        return _result(
            "needs_review",
            "no_identifier",
            ["suggest_only", "blocked"],
            [],
            "يحتاج مراجعة: لا معرّف تواصل واضح.",
        )

    if src == "unknown_source":
        return _result(
            "needs_review",
            "unknown_source",
            ["suggest_only", "draft_only", "approval_required"],
            allowed_channels_for_source(src, opt_in),
            "مراجعة بشرية: المصدر غير موثّق.",
        )

    chans = allowed_channels_for_source(src, opt_in)
    review = required_review_level(src)
    if review == "human_review":
        status = "needs_review"
        modes = ["suggest_only", "draft_only", "approval_required"]
    elif review == "light_review":
        status = "safe" if desired_channel != "whatsapp" else "needs_review"
        modes = ["draft_only", "approval_required", "suggest_only"]
    else:
        status = "safe"
        modes = ["draft_only", "approval_required", "suggest_only"]

    if desired_channel == "whatsapp" and "whatsapp_draft_if_opt_in" not in chans and "opt_in" not in opt_in.lower():
        if status == "safe":
            status = "needs_review"
        modes = ["draft_only", "approval_required", "blocked"]

    ar = {
        "safe": "مسموح بمسودات وموافقة قبل أي إرسال خارجي.",
        "needs_review": "يحتاج مراجعة قبل التواصل.",
        "blocked": "غير مسموح بالتواصل بهذه القناة/المصدر.",
    }[status]

    return _result(status, review, modes, chans, ar)


def explain_contactability_ar(result: dict[str, Any]) -> str:
    return str(result.get("summary_ar") or "")


def allowed_action_modes(result: dict[str, Any]) -> list[str]:
    return list(result.get("action_modes") or [])


def _result(
    status: str,
    reason: str,
    modes: list[str],
    channels: list[str],
    summary_ar: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason_code": reason,
        "action_modes": modes,
        "allowed_channel_hints": channels,
        "summary_ar": summary_ar,
        "approval_required": status != "blocked",
        "demo": True,
    }
