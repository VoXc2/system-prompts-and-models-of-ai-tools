"""Social strategy — official APIs + opt-in DMs only, public replies as drafts."""

from __future__ import annotations

from typing import Any


def social_do_not_do() -> list[str]:
    return [
        "scrape_public_profiles",
        "auto_dm_strangers",
        "fake_engagement",
        "buy_followers_or_engagement",
        "use_unauthorized_apis",
        "ignore_platform_terms",
    ]


def recommend_social_sources(
    sector: str, *, goal: str = "fill_pipeline",
) -> dict[str, Any]:
    """Recommend social sources by sector — only safe, official channels."""
    s = (sector or "").lower()
    by_sector = {
        "real_estate":  ["instagram_graph_api", "x_api_mentions", "google_business_reviews"],
        "retail":       ["instagram_graph_api", "google_business_reviews", "tiktok_business"],
        "healthcare":   ["google_business_reviews", "instagram_graph_api"],
        "saas":         ["x_api_mentions", "linkedin_lead_gen_forms"],
        "training":     ["linkedin_lead_gen_forms", "x_api_mentions"],
        "agency":       ["linkedin_lead_gen_forms", "x_api_mentions"],
    }
    return {
        "sector": s,
        "recommended_sources": by_sector.get(s, ["linkedin_lead_gen_forms",
                                                "google_business_reviews"]),
        "do_not_do": social_do_not_do(),
        "notes_ar": (
            "نلتزم بالـ official APIs والصلاحيات الرسمية فقط. "
            "DMs بدون تفاعل سابق محظورة."
        ),
    }


def build_social_listening_plan(
    sector: str, keywords: list[str] | None = None,
) -> dict[str, Any]:
    """Build a social listening plan — listening only, no auto-replies."""
    keywords = keywords or [
        "نمو", "B2B", "leads", "اجتماعات",
        "Pilot", "تدريب مبيعات", "أتمتة",
    ]
    return {
        "sector": sector,
        "keywords_ar_or_en": keywords,
        "listen_for": [
            "mentions_of_company",
            "competitor_mentions",
            "buying_signals",
            "complaints",
            "hiring_signals",
            "events_and_launches",
        ],
        "convert_to_cards_for": [
            "lead", "competitor_move", "review_response",
            "content_idea", "partner_suggestion",
        ],
        "no_auto_reply": True,
        "approval_required_for_reply": True,
    }


def draft_public_reply(
    comment: str,
    *,
    brand_voice: str = "professional_saudi",
) -> dict[str, Any]:
    """Build a public reply draft to a comment/review (Arabic)."""
    body_ar = (
        "شكراً على ملاحظتك. نأخذ تعليقك بجد وسنتواصل معك مباشرة لتفاصيل أكثر "
        "ومعالجة الموضوع. سعدنا بمشاركتك."
    )
    return {
        "draft": True,
        "body_ar": body_ar,
        "brand_voice": brand_voice,
        "approval_required": True,
        "live_publish_allowed": False,
        "guidelines_ar": [
            "لا تكشف بيانات شخصية في الرد العام.",
            "حول التفاصيل لقناة خاصة.",
            "لا تتجاهل العميل المنزعج.",
            "لا تحذف أو ترد بشكل دفاعي.",
        ],
    }
