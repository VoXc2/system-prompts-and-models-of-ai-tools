"""Static competitor gap framing — do_not_copy list."""

from __future__ import annotations

from typing import Any


def compare_against_categories(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "competitor_strengths_ar": [
            "أدوات CRM: بيانات غنية لكن بدون قرار يومي.",
            "أدوات واتساب: إرسال سريع لكن بدون سياسة.",
        ],
        "dealix_advantages_ar": [
            "كروت قرار عربية + موافقة + Proof.",
            "تعدد قنوات مع بوابة أمان.",
        ],
        "gaps_to_close_ar": ["تكاملات OAuth حقيقية", "تتبع تكلفة LLM"],
        "do_not_copy": ["spam_automation", "scraping_linkedin", "cold_whatsapp_blast"],
        "demo": True,
    }
