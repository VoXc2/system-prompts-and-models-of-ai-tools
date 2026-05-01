"""Classify lead/contact sources and allowed channels — policy only, no I/O."""

from __future__ import annotations

from typing import Any

_SOURCE_ORDER = (
    "crm_customer",
    "inbound_lead",
    "website_form",
    "linkedin_lead_form",
    "event_lead",
    "referral",
    "partner_intro",
    "manual_research",
    "uploaded_list",
    "unknown_source",
    "cold_list",
    "opt_out",
)


def classify_source(source: str | None) -> str:
    s = (source or "").strip().lower().replace(" ", "_")
    if s in ("opt_out", "optout"):
        return "opt_out"
    if s in _SOURCE_ORDER:
        return s
    if s in ("unknown", "", "none"):
        return "unknown_source"
    return "unknown_source"


def source_risk_score(source: str) -> int:
    """0 = low risk, 100 = high risk (for sorting)."""
    s = classify_source(source)
    return {
        "opt_out": 100,
        "cold_list": 85,
        "unknown_source": 70,
        "uploaded_list": 55,
        "manual_research": 40,
        "referral": 35,
        "partner_intro": 30,
        "event_lead": 25,
        "linkedin_lead_form": 20,
        "website_form": 15,
        "inbound_lead": 10,
        "crm_customer": 10,
    }.get(s, 65)


def allowed_channels_for_source(source: str, opt_in_status: str | None) -> list[str]:
    s = classify_source(source)
    opt = (opt_in_status or "").lower()
    if s == "opt_out":
        return []
    if s == "cold_list":
        return ["email_draft_review"] if opt != "explicit" else ["email_draft_review", "linkedin_manual_task"]
    if s == "unknown_source":
        return ["email_draft_review", "internal_task"]
    if s == "uploaded_list":
        return ["email_draft_review", "internal_task"]
    if s == "manual_research":
        return ["email_draft_review", "linkedin_manual_task", "internal_task"]
    if s in ("referral", "partner_intro"):
        return ["email_draft_review", "whatsapp_draft_if_opt_in", "calendar_draft", "internal_task"]
    if s in ("linkedin_lead_form", "website_form", "inbound_lead", "event_lead"):
        return ["email_draft_review", "whatsapp_draft_if_opt_in", "calendar_draft", "internal_task"]
    if s == "crm_customer":
        return ["email_draft_review", "whatsapp_draft_if_opt_in", "calendar_draft", "payment_draft", "internal_task"]
    return ["internal_task"]


def required_review_level(source: str) -> str:
    s = classify_source(source)
    if s in ("opt_out", "cold_list"):
        return "blocked"
    if s in ("unknown_source", "uploaded_list", "manual_research"):
        return "human_review"
    if s in ("referral", "partner_intro"):
        return "light_review"
    return "auto_ok_with_approval"


def retention_recommendation(source: str) -> dict[str, Any]:
    s = classify_source(source)
    days = {"opt_out": 0, "cold_list": 30, "unknown_source": 90}.get(s, 365)
    return {
        "source": s,
        "suggested_retention_days": days,
        "note_ar": "توصية MVP — راجع سياسة الاحتفاظ مع DPO قبل الإنتاج.",
    }


def list_sources_reference() -> dict[str, Any]:
    return {"sources": list(_SOURCE_ORDER), "demo": True}
