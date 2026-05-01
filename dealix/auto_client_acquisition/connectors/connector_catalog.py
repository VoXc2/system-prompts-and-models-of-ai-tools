"""12+ connectors with capabilities and risk — no live OAuth in MVP."""

from __future__ import annotations

from typing import Any


def _row(
    cid: str,
    label_ar: str,
    beta: str,
    allowed: list[str],
    blocked: list[str],
    risk: str,
) -> dict[str, Any]:
    return {
        "id": cid,
        "label_ar": label_ar,
        "beta_status": beta,
        "required_permissions_ar": "OAuth أو مفاتيح رسمية حسب المزود — لا تخزين أسرار في الريبو.",
        "allowed_actions": allowed,
        "blocked_actions": blocked,
        "risk_level": risk,
        "launch_phase": 1 if beta == "mvp" else 2 if beta == "pilot" else 3,
    }


_CONNECTORS: list[dict[str, Any]] = [
    _row("whatsapp", "واتساب للأعمال", "pilot", ["draft", "template_preview"], ["cold_bulk", "live_send"], "high"),
    _row("gmail", "Gmail", "pilot", ["draft_create", "read_limited"], ["send_live"], "medium"),
    _row("google_calendar", "Google Calendar", "pilot", ["draft_event"], ["insert_live"], "medium"),
    _row("google_meet", "Google Meet", "planned", ["transcript_read"], ["record_without_consent"], "high"),
    _row("linkedin_lead_forms", "LinkedIn Lead Gen", "mvp", ["lead_ingest"], ["auto_dm"], "medium"),
    _row("x_api", "X API", "registered_only", [], ["firehose", "auto_reply"], "high"),
    _row("instagram_graph", "Instagram Graph", "registered_only", [], ["auto_dm"], "high"),
    _row("google_business_profile", "Google Business Profile", "registered_only", ["review_draft"], ["auto_reply"], "medium"),
    _row("google_sheets", "Google Sheets", "planned", ["read_range_draft"], ["write_live"], "low"),
    _row("crm", "CRM عام", "planned", ["sync_draft"], ["delete_records"], "medium"),
    _row("moyasar", "Moyasar", "mvp", ["payment_link_draft"], ["charge_live"], "high"),
    _row("website_forms", "نماذج موقع", "mvp", ["webhook_ingest"], ["scraping"], "low"),
]


def build_connector_catalog() -> dict[str, Any]:
    return {"connectors": list(_CONNECTORS), "count": len(_CONNECTORS), "demo": True}
