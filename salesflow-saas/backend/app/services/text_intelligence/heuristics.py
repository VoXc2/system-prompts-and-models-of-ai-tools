"""Rule-based Arabic/English keyword signals for B2B text intelligence (no fabricated persons)."""

from __future__ import annotations

import re
from typing import Iterable

# Intent buckets (stable string ids for CRM / routing)
INTENT_INQUIRY = "inquiry"
INTENT_PURCHASE = "purchase_intent"
INTENT_PRICING = "pricing"
INTENT_SUPPORT = "support"
INTENT_COMPLAINT = "complaint"
INTENT_PARTNERSHIP = "partnership"
INTENT_SCHEDULING = "scheduling"
INTENT_UNKNOWN = "unknown"

_URGENCY_HIGH = (
    "عاجل",
    "فوري",
    "اليوم",
    "الآن",
    "urgent",
    "asap",
    "immediately",
    "today",
    "now",
)
_URGENCY_MED = ("هذا الأسبوع", "قريباً", "soon", "this week", "week")

_PAIN = (
    "مشكلة",
    "تأخير",
    "بطيء",
    "غالي",
    "خطأ",
    "issue",
    "problem",
    "delay",
    "expensive",
    "slow",
    "bug",
    "error",
)

_PRODUCT = (
    "نظام",
    "برنامج",
    "crm",
    "تكامل",
    "api",
    "اشتراك",
    "license",
    "software",
    "integration",
    "platform",
    "saas",
)

_POS = ("شكرا", "ممتاز", "رائع", "thanks", "great", "good", "happy", "مبسوط")
_NEG = ("سيء", "زعلان", "disappointed", "bad", "terrible", "angry", "unhappy", "فشل")

_DECISION = ("عقد", "شراء", "توقيع", "po", "invoice", "contract", "purchase order", "payment")
_CONSIDERATION = ("عرض سعر", "quote", "proposal", "demo", "تجربة", "مقارنة")
_AWARENESS = ("ما هو", "what is", "tell me about", "معلومات", "information")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def _hits(text: str, needles: Iterable[str]) -> int:
    t = _norm(text)
    return sum(1 for n in needles if n.lower() in t)


def classify_intent(text: str) -> str:
    t = _norm(text)
    if any(x in t for x in ("شكوى", "complaint", "unhappy", "زعلان")):
        return INTENT_COMPLAINT
    if any(x in t for x in ("دعم", "support", "ticket", "مساعدة تقنية")):
        return INTENT_SUPPORT
    if any(x in t for x in ("سعر", "تسعير", "عرض سعر", "pricing", "quote", "cost")):
        return INTENT_PRICING
    if any(x in t for x in ("شراكة", "partnership", "reseller")):
        return INTENT_PARTNERSHIP
    if any(x in t for x in ("موعد", "اجتماع", "demo", "call", "مكالمة")):
        return INTENT_SCHEDULING
    if any(x in t for x in ("أريد الشراء", "شراء", "اشترك", "buy", "purchase", "order")):
        return INTENT_PURCHASE
    if len(t) > 12:
        return INTENT_INQUIRY
    return INTENT_UNKNOWN


def urgency_level(text: str) -> str:
    t = _norm(text)
    if _hits(t, _URGENCY_HIGH) >= 1:
        return "high"
    if _hits(t, _URGENCY_MED) >= 1:
        return "medium"
    return "low"


def extract_pain_points(text: str, limit: int = 5) -> list[str]:
    t = _norm(text)
    found: list[str] = []
    for p in _PAIN:
        if p.lower() in t and p not in found:
            found.append(p)
        if len(found) >= limit:
            break
    return found


def product_interest_keywords(text: str, limit: int = 6) -> list[str]:
    t = _norm(text)
    found: list[str] = []
    for p in _PRODUCT:
        if p.lower() in t and p not in found:
            found.append(p)
        if len(found) >= limit:
            break
    return found


def sentiment_label(text: str) -> str:
    t = _norm(text)
    pos, neg = _hits(t, _POS), _hits(t, _NEG)
    if pos > neg + 1:
        return "positive"
    if neg > pos + 1:
        return "negative"
    return "neutral"


def buying_stage(text: str) -> str:
    t = _norm(text)
    if any(x in t for x in _DECISION):
        return "decision"
    if any(x in t for x in _CONSIDERATION):
        return "consideration"
    if any(x in t for x in _AWARENESS):
        return "awareness"
    return "unknown"


def confidence_from_signals(text: str, intent: str) -> float:
    """Heuristic 0..1 based on length and keyword coverage."""
    if not text or len(text.strip()) < 8:
        return 0.25
    base = min(1.0, len(text.strip()) / 800.0) * 0.35 + 0.3
    if intent != INTENT_UNKNOWN:
        base += 0.15
    base += min(0.2, (_hits(text, _PAIN) + _hits(text, _PRODUCT) + _hits(text, _URGENCY_HIGH)) * 0.03)
    return round(min(1.0, base), 3)


def suggest_sales_actions(intent: str, urgency: str, stage: str) -> dict[str, str]:
    """Non-LLM templates — safe defaults; can be replaced by LLM layer behind a flag."""
    reply = "شكراً لتواصلكم. يمكننا مساعدتكم في الخطوة التالية وفق احتياجكم."
    if intent == INTENT_PRICING:
        reply = "شكراً لاهتمامكم. هل يمكن مشاركة حجم الفريق أو الاستخدام المتوقع لنرسل عرضاً مناسباً؟"
    elif intent == INTENT_PURCHASE:
        reply = "نقدّر جاهزيتكم. هل يمكن تحديد موعد قصير لمناقشة التفعيل والتسعير؟"
    elif intent == INTENT_COMPLAINT:
        reply = "نعتذر عن الإزعاج. نريد تفاصيل إضافية لحل المشكلة بأسرع وقت."

    nxt = "تسجيل ملاحظة ومتابعة خلال 24 ساعة"
    if urgency == "high":
        nxt = "متابعة فورية عبر القناة المناسبة (واتساب/هاتف)"
    if stage == "decision":
        nxt = "إرسال عرض نهائي وجدول تفعيل"

    follow = "رسالة متابعة بعد 48 ساعة مع تلخيص الاتفاق"
    if urgency == "high":
        follow = "متابعة خلال 4 ساعات"

    offer = "جلسة تعريفية قصيرة + عرض تجربة"
    if intent == INTENT_PRICING:
        offer = "عرض سعر مبني على عدد المستخدمين"

    return {
        "suggested_reply": reply,
        "follow_up_suggestion": follow,
        "offer_suggestion": offer,
        "next_action": nxt,
    }


def market_aggregate_signals(texts: list[str]) -> dict:
    """Roll up themes across multiple public/marketing texts (no raw storage required)."""
    joined = "\n".join(texts)[:50_000]
    complaints: list[str] = []
    desires: list[str] = []
    objections: list[str] = []
    triggers: list[str] = []

    t = _norm(joined)
    for kw in ("غالي", "بطيء", "مشكلة", "expensive", "slow", "issue"):
        if kw in t and kw not in complaints:
            complaints.append(kw)
    for kw in ("أريد", "نحتاج", "need", "want", "تحسين"):
        if kw in t and kw not in desires:
            desires.append(kw)
    for kw in ("ليس الآن", "later", "ميزانية", "budget", "منافس"):
        if kw in t and kw not in objections:
            objections.append(kw)
    for kw in ("عرض", "تخفيض", "promo", "launch", "إطلاق"):
        if kw in t and kw not in triggers:
            triggers.append(kw)

    return {
        "common_complaints": complaints[:12],
        "common_desires": desires[:12],
        "common_objections": objections[:12],
        "common_triggers": triggers[:12],
    }
