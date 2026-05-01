"""Channel capabilities — registered-only social channels, no OAuth in MVP."""

from __future__ import annotations

from typing import Any

_CHANNEL_DEFS: list[dict[str, Any]] = [
    {
        "id": "whatsapp",
        "label_ar": "واتساب للأعمال",
        "beta_status": "pilot",
        "risk_level": "high",
        "allowed_actions": ["draft_message", "template_preview"],
        "blocked_actions": ["cold_outreach_auto", "bulk_send_without_approval"],
    },
    {
        "id": "email",
        "label_ar": "البريد",
        "beta_status": "ga_ready",
        "risk_level": "medium",
        "allowed_actions": ["draft_email", "schedule_internal"],
        "blocked_actions": ["smtp_live_without_approval"],
    },
    {
        "id": "linkedin_lead_form",
        "label_ar": "نماذج عملاء LinkedIn",
        "beta_status": "mvp",
        "risk_level": "low",
        "allowed_actions": ["ingest_webhook_simulation", "normalize_lead"],
        "blocked_actions": ["scrape_profile"],
    },
    {
        "id": "website_form",
        "label_ar": "نموذج موقع",
        "beta_status": "mvp",
        "risk_level": "low",
        "allowed_actions": ["ingest_webhook_simulation", "normalize_lead"],
        "blocked_actions": [],
    },
    # Wave 5 — registered-only (ingest / auto-reply deferred)
    {
        "id": "google_business",
        "label_ar": "ملف Google Business",
        "beta_status": "registered_only",
        "risk_level": "medium",
        "allowed_actions": [],
        "blocked_actions": ["auto_reply", "oauth_connect", "public_api_call"],
    },
    {
        "id": "x_twitter",
        "label_ar": "X (تويتر)",
        "beta_status": "registered_only",
        "risk_level": "medium",
        "allowed_actions": [],
        "blocked_actions": ["auto_reply", "oauth_connect", "public_api_call"],
    },
    {
        "id": "instagram",
        "label_ar": "إنستغرام",
        "beta_status": "registered_only",
        "risk_level": "medium",
        "allowed_actions": [],
        "blocked_actions": ["auto_reply", "oauth_connect", "public_api_call"],
    },
]


def list_channels() -> dict[str, Any]:
    return {"channels": list(_CHANNEL_DEFS), "demo": True}
