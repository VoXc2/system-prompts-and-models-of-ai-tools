"""WhatsApp strategy — opt-in only, never cold, draft-first."""

from __future__ import annotations

from typing import Any


def whatsapp_do_not_do() -> list[str]:
    return [
        "cold_send_without_consent",
        "scrape_groups",
        "buy_phone_lists",
        "auto_send_without_approval",
        "send_outside_business_hours_without_consent",
        "ignore_opt_out",
    ]


def requires_opt_in(contact: dict[str, Any]) -> dict[str, Any]:
    """
    Check whether reaching this contact via WhatsApp requires opt-in.

    Returns the opt-in requirement + how to obtain it if missing.
    """
    source = contact.get("source", "unknown_source")
    opt_in = (contact.get("opt_in_status") or "unknown").lower()
    has_relationship = bool(contact.get("has_relationship", False))

    needs = True
    if has_relationship and source == "crm_customer" and opt_in == "yes":
        needs = False
    if source == "inbound_lead" and opt_in in ("yes", "double"):
        needs = False

    return {
        "needs_opt_in": needs,
        "current_status": opt_in,
        "source": source,
        "obtain_via_ar": (
            "نموذج موقع + تأكيد بالـemail (double opt-in) أو "
            "Lead Gen Form + شرح صريح بنوع الرسائل."
        ),
    }


def draft_whatsapp_message(
    contact: dict[str, Any], *, offer: str = "", why_now: str = "",
) -> dict[str, Any]:
    """Build a WhatsApp message draft. Never sends; always approval-required."""
    name = contact.get("name", "")
    sal = f"هلا {name}" if name else "هلا"
    why_now_part = f" {why_now}" if why_now else ""
    body_ar = (
        f"{sal}.{why_now_part} نشتغل على Dealix كمدير نمو عربي. "
        "خلال 7 أيام نطلع 10 فرص B2B + رسائل + خطة متابعة. "
        f"{offer or 'Pilot بـ 499 ريال أو مجاني مقابل case study.'} "
        "يناسبك ديمو 12 دقيقة هذا الأسبوع؟"
        "\n\nلو ما تفضل هذه الرسائل، اكتب \"إلغاء\" وأوقفها."
    )
    risk = score_whatsapp_risk(contact, body_ar)
    return {
        "channel": "whatsapp",
        "body_ar": body_ar,
        "approval_required": True,
        "live_send_allowed": False,
        "opt_in_check": requires_opt_in(contact),
        "risk": risk,
        "do_not_do": whatsapp_do_not_do(),
    }


def score_whatsapp_risk(contact: dict[str, Any], message: str = "") -> dict[str, Any]:
    """Score WhatsApp risk 0..100; very strict."""
    source = contact.get("source", "unknown_source")
    opt_in = (contact.get("opt_in_status") or "unknown").lower()
    risk = 0
    reasons: list[str] = []

    if source == "cold_list":
        risk += 100
        reasons.append("قائمة باردة — واتساب محظور تلقائياً.")
    if opt_in not in ("yes", "double"):
        risk += 40
        reasons.append("لا يوجد opt-in واضح.")
    if source == "unknown_source":
        risk += 30
        reasons.append("مصدر غير معروف.")

    risky_phrases = ["ضمان 100%", "آخر فرصة", "اضغط الآن", "نتائج مضمونة"]
    for p in risky_phrases:
        if p in message:
            risk += 25
            reasons.append(f"عبارة محظورة: {p}")

    risk = max(0, min(100, risk))
    if risk >= 50:
        verdict = "blocked"
    elif risk >= 25:
        verdict = "needs_review"
    else:
        verdict = "safe"
    return {"risk": risk, "verdict": verdict, "reasons_ar": reasons}


def build_opt_in_request_template(
    company_name: str = "Dealix",
) -> dict[str, Any]:
    """Build an opt-in request template the customer can send via website/forms."""
    return {
        "channel": "website_or_form",
        "body_ar": (
            f"بالاشتراك في تنبيهات {company_name} عبر واتساب، أوافق على استقبال "
            "رسائل تتعلق بالعروض والمحتوى الخاص بالشركة. أعرف أنه يمكنني الانسحاب "
            "في أي وقت بكتابة \"إلغاء\"."
        ),
        "explicit_purpose_required": True,
        "explicit_company_name_required": True,
        "explicit_unsubscribe_required": True,
        "double_opt_in_recommended": True,
        "notes_ar": (
            "WhatsApp Business يتطلب شرحاً صريحاً لما سيستقبله المستخدم. "
            "ظهور رقم واتساب في موقع لا يكفي كموافقة."
        ),
    }
