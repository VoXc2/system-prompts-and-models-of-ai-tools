"""Map normalized event types to Arabic command cards (max 3 buttons)."""

from __future__ import annotations

from typing import Any

_EVENT_HANDLERS: dict[str, dict[str, Any]] = {
    "email.received": {
        "type": "inbox",
        "title_ar": "بريد وارد — فرصة متابعة",
        "risk_score": 22,
        "recommended_action_ar": "صنّف الرد واقترح مسودة متابعة قصيرة.",
        "buttons_ar": ["مسودة متابعة", "تجاهل", "إلى الصفقة"],
        "proof_impact": "draft_created",
        "action_mode": "draft_only",
    },
    "whatsapp.reply_received": {
        "type": "reply",
        "title_ar": "رد واتساب — يحتاج قراراً",
        "risk_score": 35,
        "recommended_action_ar": "تحقق من opt-in ثم اقترح ردّاً مهنياً.",
        "buttons_ar": ["مسودة رد", "تأجيل", "تصعيد"],
        "proof_impact": "reply_handled",
        "action_mode": "approval_required",
    },
    "form.submitted": {
        "type": "lead",
        "title_ar": "نموذج جديد — جاهز للتأهيل",
        "risk_score": 15,
        "recommended_action_ar": "شغّل تشخيصاً قصيراً واربط بالخدمة المناسبة.",
        "buttons_ar": ["تشخيص", "تخطي", "إسناد"],
        "proof_impact": "opportunity_created",
        "action_mode": "suggest_only",
    },
    "payment.link_created": {
        "type": "revenue",
        "title_ar": "مسودة رابط دفع",
        "risk_score": 10,
        "recommended_action_ar": "راجع المبلغ والمرجع قبل الإرسال للعميل.",
        "buttons_ar": ["موافقة مراجعة", "تعديل", "إلغاء"],
        "proof_impact": "payment_link_drafted",
        "action_mode": "draft_only",
    },
    "risk.blocked": {
        "type": "compliance_risk",
        "title_ar": "إجراء مُحظور تلقائياً",
        "risk_score": 95,
        "recommended_action_ar": "سجّل السبب واقترح بديلاً آمناً.",
        "buttons_ar": ["عرض السياسة", "مسودة بديلة", "إغلاق"],
        "proof_impact": "risks_blocked",
        "action_mode": "blocked",
    },
    "proof.generated": {
        "type": "proof_update",
        "title_ar": "تحديث Proof Pack",
        "risk_score": 5,
        "recommended_action_ar": "أضف الحدث إلى تقرير الأسبوع.",
        "buttons_ar": ["عرض الملخص", "مشاركة", "تجاهل"],
        "proof_impact": "proof_generated",
        "action_mode": "suggest_only",
    },
}


def event_to_card(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    et = (event_type or "").strip().lower()
    base = dict(_EVENT_HANDLERS.get(et) or _EVENT_HANDLERS["form.submitted"])
    base["event_type"] = et
    base["payload_preview"] = {k: payload[k] for k in list((payload or {}).keys())[:5]} if payload else {}
    if len(base.get("buttons_ar") or []) > 3:
        base["buttons_ar"] = base["buttons_ar"][:3]
    return {**base, "demo": True}
