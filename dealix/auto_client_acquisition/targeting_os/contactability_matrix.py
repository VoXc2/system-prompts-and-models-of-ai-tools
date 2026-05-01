"""Contactability matrix — هل التواصل مع هذا الـcontact مسموح؟"""

from __future__ import annotations

from typing import Any

from .contact_source_policy import (
    allowed_channels_for_source,
    classify_source,
    source_risk_score,
)

ACTION_MODES: tuple[str, ...] = (
    "suggest_only",
    "draft_only",
    "approval_required",
    "approved_execute",
    "blocked",
)

BLOCK_REASONS: dict[str, str] = {
    "opt_out": "العميل سحب موافقته.",
    "cold_whatsapp": "واتساب بارد محظور (PDPL).",
    "no_lawful_basis": "لا يوجد أساس نظامي للتواصل.",
    "missing_consent": "موافقة opt-in مفقودة.",
    "secret_in_payload": "الـ payload يحوي قيمة حساسة.",
    "high_value_no_approval": "صفقة عالية القيمة بدون اعتماد.",
    "channel_paused": "القناة موقوفة لتدهور السمعة.",
    "frequency_cap_hit": "تجاوز سقف التواصل الأسبوعي.",
    "unknown_source": "مصدر الـ contact غير معروف — تحتاج مراجعة.",
}


def block_reason_codes() -> dict[str, str]:
    """Expose all block reason codes (Arabic)."""
    return dict(BLOCK_REASONS)


def evaluate_contactability(
    contact: dict[str, Any],
    *,
    desired_channel: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate whether contacting `contact` via `desired_channel` is permitted.

    Returns a structured verdict with status and Arabic reasons.
    """
    source = contact.get("source", "unknown_source")
    opt_in = contact.get("opt_in_status", "unknown")
    opt_out = bool(contact.get("opt_out", False))
    has_relationship = bool(contact.get("has_relationship", False))

    risk = source_risk_score(source)
    classified = classify_source(source)["source"]

    if opt_out or classified == "opt_out":
        return {
            "status": "blocked",
            "reason_codes": ["opt_out"],
            "reasons_ar": [BLOCK_REASONS["opt_out"]],
            "allowed_action_mode": "blocked",
            "allowed_channels": [],
        }

    channel_map = allowed_channels_for_source(source, opt_in_status=str(opt_in))["channels"]

    if desired_channel:
        ch = desired_channel.lower()
        ch_status = channel_map.get(ch, "blocked")
        if ch_status == "blocked":
            reason = "cold_whatsapp" if ch == "whatsapp" else "no_lawful_basis"
            return {
                "status": "blocked",
                "reason_codes": [reason],
                "reasons_ar": [BLOCK_REASONS[reason]],
                "allowed_action_mode": "blocked",
                "allowed_channels": [k for k, v in channel_map.items() if v != "blocked"],
            }
        if ch_status == "needs_review":
            return {
                "status": "needs_review",
                "reason_codes": ["unknown_source"] if classified == "unknown_source" else [],
                "reasons_ar": (
                    [BLOCK_REASONS["unknown_source"]] if classified == "unknown_source"
                    else ["تحتاج مراجعة بشرية قبل الإرسال."]
                ),
                "allowed_action_mode": "approval_required",
                "allowed_channels": [k for k, v in channel_map.items() if v != "blocked"],
            }
        # safe
        return {
            "status": "safe",
            "reason_codes": [],
            "reasons_ar": [],
            "allowed_action_mode": "draft_only" if not has_relationship else "approval_required",
            "allowed_channels": [k for k, v in channel_map.items() if v != "blocked"],
        }

    # No desired_channel → return per-channel verdict
    return {
        "status": "safe" if any(v == "safe" for v in channel_map.values()) else "needs_review",
        "reason_codes": [],
        "reasons_ar": [],
        "allowed_action_mode": "draft_only",
        "allowed_channels": [k for k, v in channel_map.items() if v != "blocked"],
        "channel_status": channel_map,
        "risk_score": risk,
    }


def explain_contactability_ar(result: dict[str, Any]) -> str:
    """Build a human Arabic explanation from a contactability result."""
    status = result.get("status", "unknown")
    reasons = result.get("reasons_ar", [])
    channels = result.get("allowed_channels", [])
    if status == "blocked":
        return f"محظور: {' / '.join(reasons) or 'سياسة عامة'}."
    if status == "needs_review":
        return (
            f"يحتاج مراجعة: {' / '.join(reasons) or 'بدون مصدر واضح'}. "
            f"القنوات المتاحة بعد المراجعة: {', '.join(channels) or 'لا شيء'}."
        )
    return f"آمن. القنوات المسموحة: {', '.join(channels)}."


def allowed_action_modes(result: dict[str, Any]) -> list[str]:
    """Return the action modes available given a contactability verdict."""
    status = result.get("status", "blocked")
    if status == "blocked":
        return ["blocked"]
    if status == "needs_review":
        return ["suggest_only", "draft_only", "approval_required"]
    return ["draft_only", "approval_required", "approved_execute"]
