"""Social — official APIs and drafts only."""

from __future__ import annotations

from typing import Any


def social_do_not_do() -> list[str]:
    return ["unauthorized_scraping", "auto_dm_without_permission", "firehose_access", "fake_engagement"]


def recommend_social_sources(sector: str, goal: str) -> dict[str, Any]:
    return {
        "sector": sector,
        "goal": goal,
        "recommended_sources": ["linkedin_lead_form", "meta_business_inbox_registered", "x_api_registered_webhook"],
        "do_not_do": social_do_not_do(),
        "summary_ar": "اربط القنوات التي تملك صلاحية رسمية لها فقط.",
        "demo": True,
    }


def build_social_listening_plan(sector: str, keywords: list[str]) -> dict[str, Any]:
    return {
        "sector": sector,
        "keywords": keywords[:20],
        "plan_ar": "راقب الكلمات عبر webhooks/APIs المسجّلة؛ حوّل الإشارات إلى كروت مسودة داخل المنصة.",
        "approval_required": True,
        "demo": True,
    }


def draft_public_reply(comment: str, brand_voice: str) -> dict[str, Any]:
    return {
        "draft_reply_ar": f"شكراً لتعليقكم. نتواصل بالخاص لخدمتكم — [{brand_voice}]",
        "original_snippet": comment[:200],
        "approval_required": True,
        "demo": True,
    }
