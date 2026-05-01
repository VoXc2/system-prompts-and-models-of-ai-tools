"""
Intent Router — classifies the user's Arabic question into one of N intents.

Production: backed by LLM with examples. This module ships with a robust
keyword + phrase-pattern classifier so the system works without LLM and so
it's testable / deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Intent:
    """A classified intent with confidence + chosen route."""

    intent_id: str
    confidence: float
    matched_keywords: tuple[str, ...] = ()


# ── Intent catalog ───────────────────────────────────────────────
INTENTS: tuple[str, ...] = (
    "what_to_do_today",
    "explain_metric",
    "show_pipeline",
    "show_at_risk_deals",
    "show_revenue_leaks",
    "compare_sectors",
    "find_lookalikes",
    "draft_outreach",
    "generate_qbr",
    "generate_proof_pack",
    "explain_compliance_block",
    "show_market_radar",
    "forecast_revenue",
    "stop_or_disable",
    "general_help",
)


# Keyword patterns — Arabic + English. Order matters (first match wins).
_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("stop_or_disable", ("اوقف", "أوقف", "ايقاف", "stop", "disable", "تعطيل")),
    ("what_to_do_today", ("اليوم", "وش اسوي", "وش أسوي", "what should i do", "today")),
    ("show_at_risk_deals", ("at risk", "معرضة للخطر", "صفقات جامدة", "stalled")),
    ("show_revenue_leaks", ("تسريب", "leak", "ضايع", "ضايعه", "ضائع", "ضائعه")),
    ("show_revenue_leaks", ("اين المال", "أين المال")),
    ("forecast_revenue", ("توقع", "forecast", "30 يوم", "60 يوم", "90 يوم", "كم متوقع")),
    ("show_pipeline", ("pipeline", "بايبلاين", "صفقاتي", "قائمة الصفقات")),
    ("compare_sectors", ("قارن", "مقارنة", "compare sectors", "أي قطاع")),
    ("find_lookalikes", ("شركات مثل", "مشابه", "lookalike", "مماثل")),
    ("draft_outreach", ("اكتب رسالة", "اكتب لي", "draft", "صياغة")),
    ("generate_qbr", ("qbr", "تقرير ربعي", "تقرير شهري")),
    ("generate_proof_pack", ("proof pack", "اثبات", "إثبات", "ROI report")),
    ("explain_compliance_block", ("لماذا حُظر", "لماذا حظر", "compliance", "blocked", "PDPL")),
    ("show_market_radar", ("سوق", "market", "radar", "اشارات", "إشارات", "signals")),
    ("explain_metric", ("لماذا", "ليه", "explain", "اشرح", "what is")),
)


def classify_intent(question_ar: str) -> Intent:
    """Match the question to the most specific intent, with confidence."""
    q = (question_ar or "").lower().strip()
    if not q:
        return Intent(intent_id="general_help", confidence=0.0)

    best: tuple[str, int, list[str]] | None = None  # (intent, score, matched)
    for intent_id, keywords in _PATTERNS:
        matched = [k for k in keywords if k.lower() in q]
        if not matched:
            continue
        score = len(matched)
        if best is None or score > best[1]:
            best = (intent_id, score, matched)

    if best is None:
        return Intent(intent_id="general_help", confidence=0.2)

    intent_id, score, matched = best
    # Confidence: 0.5 base + 0.15 per matched keyword, capped at 0.95
    confidence = min(0.95, 0.5 + 0.15 * score)
    return Intent(intent_id=intent_id, confidence=confidence, matched_keywords=tuple(matched))


def list_intents() -> list[dict]:
    """Discoverable list — used by the help endpoint."""
    descriptions = {
        "what_to_do_today": "ماذا أفعل اليوم — الأولويات + القرارات",
        "explain_metric": "اشرح رقم/مقياس في اللوحة",
        "show_pipeline": "عرض pipeline الصفقات الحالية",
        "show_at_risk_deals": "صفقات معرضة للخطر — جامدة أو single-threaded",
        "show_revenue_leaks": "أين المال يتسرب — leaks المالية",
        "compare_sectors": "مقارنة بين قطاعات",
        "find_lookalikes": "شركات تشبه أفضل عملائنا",
        "draft_outreach": "كتابة رسالة مخصصة",
        "generate_qbr": "توليد QBR ربعي/شهري",
        "generate_proof_pack": "توليد Proof Pack شهري",
        "explain_compliance_block": "لماذا تم حظر هذا التواصل",
        "show_market_radar": "حالة السوق والإشارات الجديدة",
        "forecast_revenue": "توقعات الإيراد 30/60/90 يوم",
        "stop_or_disable": "إيقاف autopilot أو حملة",
        "general_help": "مساعدة عامة",
    }
    return [
        {"intent_id": i, "description_ar": descriptions.get(i, "")}
        for i in INTENTS
    ]
