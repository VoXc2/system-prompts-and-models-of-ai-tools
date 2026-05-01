"""Event → Card converter — every channel event becomes an Arabic decision card."""

from __future__ import annotations

from typing import Any

# Each event_type → card_type Dealix renders.
EVENT_TO_CARD_TYPES: dict[str, str] = {
    "email.received": "email_lead",
    "whatsapp.reply_received": "whatsapp_reply",
    "form.submitted": "opportunity",
    "lead.uploaded": "list_intake",
    "meeting.drafted": "meeting_prep",
    "meeting.completed": "meeting_outcome",
    "payment.link_created": "payment",
    "partner.suggested": "partner_suggestion",
    "review.created": "review_response",
    "social.comment_received": "social_signal",
    "proof.generated": "proof_pack",
    "risk.blocked": "risk_alert",
    "service.completed": "service_outcome",
}


def build_card_from_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a typed event into an Arabic decision card.

    Returns a dict with title_ar/summary_ar/why_now/recommended_action_ar/
    risk_level/buttons_ar (≤3)/approval_required/live_send_allowed=False.
    """
    event_type = str(event.get("event_type", ""))
    payload = dict(event.get("payload", {}) or {})
    customer_id = event.get("customer_id")

    card_type = EVENT_TO_CARD_TYPES.get(event_type, "action_required")

    base = {
        "type": card_type,
        "event_type": event_type,
        "customer_id": customer_id,
        "approval_required": True,
        "live_send_allowed": False,
        "buttons_ar": ["اعتمد", "عدّل", "تخطي"],
    }

    if event_type == "email.received":
        return {
            **base,
            "title_ar": "إيميل جديد يحتوي إشارة شراء",
            "summary_ar": (
                f"من: {payload.get('from', '?')}. "
                f"الموضوع: {payload.get('subject', '?')}."
            ),
            "why_now_ar": "ينتظر رداً منذ آخر تفاعل.",
            "recommended_action_ar": "جهّز رد عربي + احجز اجتماع",
            "risk_level": "low",
        }

    if event_type == "whatsapp.reply_received":
        return {
            **base,
            "title_ar": "رد واتساب من Lead",
            "summary_ar": (
                f"المحتوى: {str(payload.get('text', ''))[:120]}."
            ),
            "why_now_ar": "اهتمام نشط — احفظ الزخم.",
            "recommended_action_ar": "اعتمد رد قصير + لا ترسل عرض PDF كامل",
            "risk_level": "low",
        }

    if event_type == "form.submitted":
        return {
            **base,
            "title_ar": "Lead جديد من نموذج الموقع",
            "summary_ar": (
                f"الشركة: {payload.get('company', '?')}. "
                f"الدور: {payload.get('role', '?')}."
            ),
            "why_now_ar": "Inbound lead — أعلى أولوية اليوم.",
            "recommended_action_ar": "اعتمد رسالة شكر + احجز ديمو 12 دقيقة",
            "risk_level": "low",
        }

    if event_type == "review.created":
        rating = int(payload.get("rating", 5) or 5)
        return {
            **base,
            "title_ar": f"تقييم جديد — {rating} نجوم",
            "summary_ar": str(payload.get("text", ""))[:200],
            "why_now_ar": "السمعة المحلية حساسة — لا تتأخر.",
            "recommended_action_ar": (
                "رد علني قصير + تواصل خاص لتفاصيل."
                if rating < 3 else
                "شكر علني + سؤال ما الذي أعجبهم تحديداً."
            ),
            "risk_level": "high" if rating < 3 else "low",
        }

    if event_type == "payment.link_created":
        return {
            **base,
            "title_ar": "رابط دفع جاهز",
            "summary_ar": (
                f"المبلغ: {payload.get('amount_sar', '?')} ريال — "
                f"{payload.get('description', '')}."
            ),
            "why_now_ar": "العميل وافق — أرسل الرابط بعد المراجعة.",
            "recommended_action_ar": "راجع المبلغ ثم أرسل من Moyasar dashboard",
            "risk_level": "medium",
        }

    if event_type == "risk.blocked":
        return {
            **base,
            "title_ar": "تنبيه: تم منع فعل خطر تلقائياً",
            "summary_ar": str(payload.get("reason_ar", ""))[:200],
            "why_now_ar": "حماية القناة من الحظر/المخالفة.",
            "recommended_action_ar": "راجع السياسة + جهّز بديل آمن",
            "risk_level": "high",
            "buttons_ar": ["فهم", "اعرض البديل", "أرشف"],
        }

    if event_type == "partner.suggested":
        return {
            **base,
            "title_ar": "اقتراح شريك جديد",
            "summary_ar": (
                f"النوع: {payload.get('partner_type', '?')}. "
                f"السبب: {payload.get('reason_ar', '')[:120]}."
            ),
            "why_now_ar": "نقطة تكامل واضحة + قاعدة عملاء مشتركة.",
            "recommended_action_ar": "اكتب رسالة warm + احجز مكالمة 20 دقيقة",
            "risk_level": "low",
        }

    if event_type == "meeting.drafted":
        return {
            **base,
            "title_ar": "مسودة اجتماع جاهزة",
            "summary_ar": (
                f"مع: {payload.get('with_company', '?')} — "
                f"{payload.get('proposed_time', 'الوقت المقترح')}"
            ),
            "why_now_ar": "اعتمد المسودة لإرسال الدعوة.",
            "recommended_action_ar": "راجع الـ agenda + اعتمد",
            "risk_level": "low",
        }

    if event_type == "service.completed":
        return {
            **base,
            "title_ar": "خدمة اكتملت — Proof Pack جاهز",
            "summary_ar": (
                f"الخدمة: {payload.get('service_id', '?')}. "
                "Proof Pack + توصية بالخطوة التالية معدّة."
            ),
            "why_now_ar": "وقت الترقية بينما النتائج طازجة.",
            "recommended_action_ar": "اعتمد Proof Pack + ابدأ Upsell",
            "risk_level": "low",
            "buttons_ar": ["اعتمد Proof", "ابدأ Upsell", "لاحقاً"],
        }

    # Default fallback.
    return {
        **base,
        "title_ar": f"حدث: {event_type}",
        "summary_ar": str(payload)[:200],
        "why_now_ar": "حدث جديد يحتاج مراجعة.",
        "recommended_action_ar": "افتح للمراجعة",
        "risk_level": "low",
    }
