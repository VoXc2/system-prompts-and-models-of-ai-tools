"""Deterministic intent classifier — Arabic + English keywords → 16 intents."""

from __future__ import annotations

import re
from typing import Any

# 16 supported intents that drive the operator.
SUPPORTED_INTENTS: tuple[str, ...] = (
    "want_more_customers",
    "has_contact_list",
    "want_partnerships",
    "want_daily_growth",
    "want_meetings",
    "want_email_rescue",
    "want_whatsapp_setup",
    "ask_pricing",
    "approve_action",
    "edit_action",
    "skip_action",
    "ask_demo",
    "ask_proof",
    "ask_services",
    "ask_partnership",
    "ask_revenue_today",
)

# Each intent → (Arabic keywords, English keywords).
_KEYWORDS: dict[str, tuple[list[str], list[str]]] = {
    "want_more_customers": (
        ["عملاء", "فرص", "leads", "ليدز", "عميل جديد", "مبيعات",
         "أبغى عملاء", "زيادة عملاء"],
        ["customers", "leads", "more sales", "new clients", "pipeline"],
    ),
    "has_contact_list": (
        ["قائمة", "أرقام", "إيميلات", "CSV", "قائمتي", "عملاء قدامى",
         "اللستة", "ملف"],
        ["list", "csv", "old customers", "spreadsheet", "contacts"],
    ),
    "want_partnerships": (
        ["شراكات", "شريك", "وكالة", "تعاون", "موزع", "شركاء"],
        ["partnership", "partner", "agency deal", "referral"],
    ),
    "want_daily_growth": (
        ["تشغيل يومي", "نمو شهري", "Growth OS", "اشتراك", "يومياً",
         "مدير نمو"],
        ["daily growth", "growth os", "subscription", "monthly"],
    ),
    "want_meetings": (
        ["اجتماعات", "ديمو", "meeting", "موعد", "احجز", "مكالمة",
         "demo"],
        ["meeting", "demo", "book", "schedule call"],
    ),
    "want_email_rescue": (
        ["إيميل", "Gmail", "Outlook", "إنباكس", "بريد", "ضائعة"],
        ["email rescue", "inbox", "gmail", "missed emails"],
    ),
    "want_whatsapp_setup": (
        ["واتساب", "WhatsApp", "opt-in", "حملة واتساب", "أرقامي"],
        ["whatsapp", "compliance", "opt-in"],
    ),
    "ask_pricing": (
        ["السعر", "كم", "بكم", "تكلفة", "اشتراك"],
        ["price", "cost", "how much", "pricing"],
    ),
    "approve_action": (
        ["اعتمد", "موافق", "وافق", "تمام", "نعم"],
        ["approve", "ok", "yes", "go ahead", "confirm"],
    ),
    "edit_action": (
        ["عدّل", "تعديل", "غير", "بدّل"],
        ["edit", "change", "modify", "tweak"],
    ),
    "skip_action": (
        ["تخطي", "تخطى", "تجاوز", "خطّي", "لا"],
        ["skip", "no", "pass", "later"],
    ),
    "ask_demo": (
        ["ديمو", "عرض", "أشوف", "جرب", "تجربة"],
        ["demo", "try", "show me", "trial"],
    ),
    "ask_proof": (
        ["proof", "نتائج", "case study", "إثبات", "تقرير"],
        ["proof", "results", "case study", "report"],
    ),
    "ask_services": (
        ["الخدمات", "وش عندكم", "ماذا تقدمون", "العروض", "bundles"],
        ["services", "what do you offer", "bundles", "packages"],
    ),
    "ask_partnership": (
        ["وكالة شريكة", "Agency Partner", "revenue share", "شراكة وكالة"],
        ["agency partner", "revenue share", "white label"],
    ),
    "ask_revenue_today": (
        ["دخل اليوم", "أبيع اليوم", "اول pilot", "ابدأ اليوم"],
        ["revenue today", "sell today", "first pilot", "private beta"],
    ),
}

# Map intent → recommended service ID (in service_tower.service_catalog).
INTENT_TO_SERVICE: dict[str, str] = {
    "want_more_customers": "first_10_opportunities_sprint",
    "has_contact_list": "list_intelligence",
    "want_partnerships": "partner_sprint",
    "want_daily_growth": "growth_os_monthly",
    "want_meetings": "meeting_booking_sprint",
    "want_email_rescue": "email_revenue_rescue",
    "want_whatsapp_setup": "whatsapp_compliance_setup",
    "ask_pricing": "free_growth_diagnostic",
    "ask_demo": "free_growth_diagnostic",
    "ask_proof": "free_growth_diagnostic",
    "ask_services": "free_growth_diagnostic",
    "ask_partnership": "agency_partner_program",
    "ask_revenue_today": "first_10_opportunities_sprint",
}


def classify_intent(message: str) -> dict[str, Any]:
    """
    Classify a free-text message → intent + confidence.

    Deterministic, keyword-based. No LLM. Returns:
        {
          "intent": str,
          "confidence": float (0..1),
          "matched_keywords": list[str],
          "all_scores": dict[intent, score],
        }
    """
    text = (message or "").strip()
    if not text:
        return {
            "intent": "ask_services",
            "confidence": 0.1,
            "matched_keywords": [],
            "all_scores": {},
        }

    text_lc = text.lower()
    scores: dict[str, int] = {}
    matched_by_intent: dict[str, list[str]] = {}

    for intent, (ar_kw, en_kw) in _KEYWORDS.items():
        matches: list[str] = []
        for kw in ar_kw:
            if kw in text:
                matches.append(kw)
        for kw in en_kw:
            if kw.lower() in text_lc:
                matches.append(kw)
        scores[intent] = len(matches)
        if matches:
            matched_by_intent[intent] = matches

    if not any(scores.values()):
        return {
            "intent": "ask_services",
            "confidence": 0.2,
            "matched_keywords": [],
            "all_scores": scores,
        }

    best_intent = max(scores, key=lambda k: scores[k])
    total_matches = sum(scores.values())
    confidence = (
        round(scores[best_intent] / max(1, total_matches), 3)
        if total_matches else 0.0
    )

    return {
        "intent": best_intent,
        "confidence": confidence,
        "matched_keywords": matched_by_intent.get(best_intent, []),
        "all_scores": scores,
    }


def intent_to_service(intent: str) -> str | None:
    """Return the service-tower service ID linked to an intent (or None)."""
    return INTENT_TO_SERVICE.get(intent)
