"""Rule-based intent classification (AR/EN) — no LLM required for MVP."""

from __future__ import annotations

import re
from typing import Final

# Intent ids consumed by service_orchestrator and conversation_router.
INTENT_WANT_MORE_CUSTOMERS: Final = "want_more_customers"
INTENT_HAS_CONTACT_LIST: Final = "has_contact_list"
INTENT_WANT_PARTNERSHIPS: Final = "want_partnerships"
INTENT_WANT_DAILY_GROWTH: Final = "want_daily_growth"
INTENT_WANT_MEETINGS: Final = "want_meetings"
INTENT_WANT_EMAIL_RESCUE: Final = "want_email_rescue"
INTENT_WANT_WHATSAPP_SETUP: Final = "want_whatsapp_setup"
INTENT_ASK_PRICING: Final = "ask_pricing"
INTENT_APPROVE_ACTION: Final = "approve_action"
INTENT_EDIT_ACTION: Final = "edit_action"
INTENT_SKIP_ACTION: Final = "skip_action"
INTENT_ASK_DEMO: Final = "ask_demo"
INTENT_ASK_PROOF: Final = "ask_proof"
INTENT_ASK_SERVICES: Final = "ask_services"
INTENT_ASK_PARTNERSHIP: Final = "ask_partnership"
INTENT_ASK_REVENUE_TODAY: Final = "ask_revenue_today"
INTENT_COLD_WHATSAPP_REQUEST: Final = "cold_whatsapp_request"  # blocked path
INTENT_UNKNOWN: Final = "unknown"


def normalize_user_text(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def classify_intent(text: str) -> str:
    """Return intent id from free-form user message."""
    t = normalize_user_text(text)

    if not t:
        return INTENT_UNKNOWN

    # Dangerous / policy — before generic channel mentions
    cold_ar = ("واتساب بارد" in text) or ("رسائل باردة" in text) or ("بارد" in text and "واتساب" in text)
    cold_en = "cold whatsapp" in t or "whatsapp blast" in t or "bulk whatsapp" in t
    if cold_ar or cold_en:
        return INTENT_COLD_WHATSAPP_REQUEST

    if "موافق" in t or t == "approve" or "اعتمد" in t:
        return INTENT_APPROVE_ACTION
    if "عدّل" in t or "عدل" in t or "edit" in t:
        return INTENT_EDIT_ACTION
    if "تخطي" in t or "skip" in t:
        return INTENT_SKIP_ACTION

    if "سعر" in t or "تسعير" in t or "pricing" in t or "price" in t:
        return INTENT_ASK_PRICING
    if "ديمو" in t or "demo" in t:
        return INTENT_ASK_DEMO
    if "proof" in t or "إثبات" in text or "اثبات" in text:
        return INTENT_ASK_PROOF
    if (
        "خدمات" in t
        or "وش أفضل" in t
        or "ما أفضل" in t
        or "أفضل خدمة" in text
        or "افضل خدمة" in text
        or "ask_services" in t
    ):
        return INTENT_ASK_SERVICES
    if "شراكة" in t or "partnership" in t or "شراكات" in t:
        return INTENT_WANT_PARTNERSHIPS
    if "ايراد اليوم" in t or "إيراد اليوم" in text or "revenue today" in t:
        return INTENT_ASK_REVENUE_TODAY

    list_signals = (
        "قائمة أرقام" in text
        or "عندي قائمة" in text
        or "csv" in t
        or "قائمة ارقام" in text
        or "contacts" in t
        or "قائمة جهات" in text
    )
    if list_signals:
        return INTENT_HAS_CONTACT_LIST

    meeting_signals = "اجتماع" in text or "meetings" in t or "حجز" in t
    if meeting_signals and ("أبغى" in text or "ابغى" in text or "want" in t):
        return INTENT_WANT_MEETINGS

    email_signals = ("ايميل" in text or "إيميل" in text or "gmail" in t or "بريد" in text) and (
        "إنقاذ" in text or "rescue" in t or "فرص" in text
    )
    if email_signals:
        return INTENT_WANT_EMAIL_RESCUE

    wa_setup = ("واتساب" in text or "whatsapp" in t) and ("امتثال" in text or "إعداد" in text or "setup" in t)
    if wa_setup:
        return INTENT_WANT_WHATSAPP_SETUP

    daily = "يومي" in text or "daily" in t or "موجز" in text
    if daily:
        return INTENT_WANT_DAILY_GROWTH

    customer_signals = (
        "عملاء أكثر" in text
        or "أبغى عملاء" in text
        or "ابغى عملاء" in text
        or "more customers" in t
        or "leads" in t
        or "فرص" in text
    )
    if customer_signals:
        return INTENT_WANT_MORE_CUSTOMERS

    return INTENT_UNKNOWN
