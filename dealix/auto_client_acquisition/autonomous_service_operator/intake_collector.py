"""Intake collector — builds intake questions per intent + validates payloads."""

from __future__ import annotations

from typing import Any

# Intake questions per intent (Arabic).
_INTAKE_QUESTIONS_BY_INTENT: dict[str, list[dict[str, Any]]] = {
    "want_more_customers": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "city", "label_ar": "المدينة", "required": True},
        {"key": "offer", "label_ar": "العرض الرئيسي", "required": True},
        {"key": "ideal_customer", "label_ar": "العميل المثالي",
         "required": True},
    ],
    "has_contact_list": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "list_size", "label_ar": "حجم القائمة (تقريباً)",
         "required": True},
        {"key": "list_source", "label_ar": "مصدر القائمة (CRM/event/upload)",
         "required": True},
        {"key": "channels_available", "label_ar": "القنوات المتاحة",
         "required": True},
    ],
    "want_partnerships": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "partner_goal",
         "label_ar": "هدف الشراكة (وكالات/موزعين/co-marketing)",
         "required": True},
        {"key": "current_partners", "label_ar": "شركاء حاليين (إن وجد)",
         "required": False},
    ],
    "want_daily_growth": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "team_size", "label_ar": "حجم فريق المبيعات/النمو",
         "required": True},
        {"key": "channels", "label_ar": "القنوات الحالية", "required": True},
        {"key": "approval_owner", "label_ar": "من يوافق على الرسائل؟",
         "required": True},
    ],
    "want_meetings": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "prospect_count", "label_ar": "عدد الـ prospects",
         "required": True},
        {"key": "calendar_link", "label_ar": "رابط Calendar (لو وُجد)",
         "required": False},
    ],
    "want_email_rescue": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "gmail_label",
         "label_ar": "اسم الـ label/الـ folder المستهدف",
         "required": True},
        {"key": "ICP", "label_ar": "العميل المثالي", "required": True},
    ],
    "want_whatsapp_setup": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "list_size",
         "label_ar": "حجم قاعدة الواتساب الحالية", "required": True},
        {"key": "current_practice",
         "label_ar": "الطريقة الحالية في إرسال الرسائل", "required": True},
    ],
    "ask_revenue_today": [
        {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
        {"key": "sector", "label_ar": "القطاع", "required": True},
        {"key": "city", "label_ar": "المدينة", "required": True},
        {"key": "offer", "label_ar": "العرض الرئيسي", "required": True},
    ],
    # Default minimal intake for any "ask_*" intent.
    "ask_services": [
        {"key": "goal", "label_ar": "ما هدفك الأساسي؟", "required": True},
    ],
}


def build_intake_questions_for_intent(intent: str) -> dict[str, Any]:
    """Return intake questions for an intent. Falls back to ask_services."""
    questions = _INTAKE_QUESTIONS_BY_INTENT.get(intent)
    if questions is None:
        questions = _INTAKE_QUESTIONS_BY_INTENT["ask_services"]
    return {
        "intent": intent,
        "questions": [dict(q) for q in questions],
        "estimated_minutes": max(2, len(questions) * 1),
        "approval_required": True,
    }


def parse_intake_payload(
    intent: str, raw_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Parse + sanitize an intake payload against the intent's question set."""
    raw_payload = raw_payload or {}
    questions = _INTAKE_QUESTIONS_BY_INTENT.get(
        intent, _INTAKE_QUESTIONS_BY_INTENT["ask_services"],
    )
    parsed: dict[str, Any] = {}
    for q in questions:
        key = q["key"]
        val = raw_payload.get(key)
        if val is None:
            continue
        # Strings get truncated to 500 chars.
        if isinstance(val, str):
            val = val.strip()[:500]
        parsed[key] = val
    return parsed


def validate_intake_completeness(
    intent: str, payload: dict[str, Any],
) -> dict[str, Any]:
    """Check that all required intake fields are present."""
    questions = _INTAKE_QUESTIONS_BY_INTENT.get(
        intent, _INTAKE_QUESTIONS_BY_INTENT["ask_services"],
    )
    missing: list[str] = []
    for q in questions:
        if q.get("required") and not payload.get(q["key"]):
            missing.append(str(q["key"]))
    return {
        "intent": intent,
        "complete": not missing,
        "missing_fields": missing,
        "missing_count": len(missing),
    }
