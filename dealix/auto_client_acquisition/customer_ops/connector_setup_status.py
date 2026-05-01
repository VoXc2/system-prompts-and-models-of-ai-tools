"""Connector readiness matrix (demo / staging oriented)."""

from __future__ import annotations

from typing import Any


def build_connector_status() -> dict[str, Any]:
    return {
        "connectors": [
            {
                "id": "whatsapp",
                "name_ar": "واتساب",
                "status": "draft_only",
                "notes_ar": "الإرسال الحي يتطلب opt-in وسياسة وموافقة.",
            },
            {
                "id": "gmail",
                "name_ar": "Gmail",
                "status": "draft_ready",
                "notes_ar": "المسودات أولاً؛ الإرسال محظور افتراضياً.",
            },
            {
                "id": "google_calendar",
                "name_ar": "Google Calendar",
                "status": "draft_ready",
                "notes_ar": "إدراج الحدث يتطلب موافقة.",
            },
            {
                "id": "moyasar",
                "name_ar": "Moyasar",
                "status": "manual_or_sandbox",
                "notes_ar": "روابط دفع/فواتير يدوية أو sandbox؛ لا charge من المنصة افتراضياً.",
            },
            {
                "id": "linkedin_lead_forms",
                "name_ar": "LinkedIn Lead Gen",
                "status": "strategy_only",
                "notes_ar": "لا scraping؛ نماذج رسمية وإعلانات ومهام يدوية معتمدة.",
            },
        ],
        "summary_ar": "الوضع الافتراضي: مسودات وموافقات؛ لا توسيع live قبل staging واتفاق العميل.",
    }
