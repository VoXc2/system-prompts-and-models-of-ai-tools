"""
Saudi Message Engine — Arabic drafts that don't sound like spam.

Style rules (encoded in templates):
  - short (≤4 sentences for first message)
  - non-exaggerated (no "ضمان 100%", no "نتائج مضمونة")
  - explicit reason for outreach (not generic)
  - simple ask (one CTA, low-commitment)
  - sector-aware tone
  - approval_required = True ALWAYS
"""

from __future__ import annotations

import hashlib
from typing import Any


# ── Saudi B2B opening line bank — sector-aware ──────────────────
_OPENERS_BY_SECTOR_AR: dict[str, list[str]] = {
    "real_estate": [
        "السلام عليكم أستاذ {name}،\nلاحظت أنكم تتوسعون في {city}.",
        "مرحباً أستاذ {name}،\nمتابع نشاطكم في تطوير العقار في {city}.",
    ],
    "clinics": [
        "السلام عليكم دكتور {name}،\nشاهدت تطور خدمات العيادة في {city}.",
        "مرحباً دكتور {name}،\nأقدر اهتمامكم بتجربة المرضى في {city}.",
    ],
    "logistics": [
        "السلام عليكم أستاذ {name}،\nلاحظت توسعكم في خدمات الشحن في {city}.",
        "مرحباً أستاذ {name}،\nقطاع اللوجستيات في {city} يتحرك بسرعة.",
    ],
    "training": [
        "السلام عليكم أستاذ {name}،\nمتابع أثر برامجكم التدريبية في {city}.",
        "مرحباً أستاذ {name}،\nالطلب على التدريب الـ B2B يتزايد في {city}.",
    ],
    "default": [
        "السلام عليكم أستاذ {name}،\nمتابع نشاطكم في {city}.",
        "مرحباً أستاذ {name}،\nلاحظت تطوركم في {city}.",
    ],
}

# A single short reason + ask combo. Keep under 4 sentences total.
_REASON_TEMPLATES_AR: dict[str, str] = {
    "existing_customer": "باعتبار العلاقة القائمة معكم، عندي اقتراح سريع يخدم {goal}.",
    "inbound_lead": "بناءً على اهتمامكم الأخير، عندي خطوة واضحة لتسريع {goal}.",
    "referral": "وصلتني توصية مهنية للتواصل معكم بخصوص {goal}.",
    "event_lead": "بعد لقائنا الأخير، حضّرت اقتراح صغير يخدم {goal}.",
    "old_lead": "بمناسبة الموسم الجديد، عندي تحديث يهم {goal}.",
    "unknown": "بعد البحث في خدماتكم، عندي فرضية صغيرة تخدم {goal}.",
    "cold_list": "بعد البحث في خدماتكم، عندي فرضية صغيرة تخدم {goal}.",
}

_ASK_TEMPLATES_AR: list[str] = [
    "يناسبك أرسل لك مثال سريع؟",
    "هل ١٥ دقيقة الأسبوع الجاي مناسبة لمشاركة الفكرة؟",
    "تفضّل أرسل ملخص بصفحة واحدة أو نتفق على مكالمة قصيرة؟",
]


def _pick(seq: list[str], seed: str) -> str:
    """Deterministic choice — same seed → same pick."""
    if not seq:
        return ""
    h = hashlib.md5(seed.encode("utf-8")).digest()
    return seq[h[0] % len(seq)]


def _resolve_name(contact: dict[str, Any]) -> str:
    n = (contact.get("name") or "").strip()
    if not n:
        return "الفاضل"
    parts = n.split()
    return parts[0] if parts else n


def _resolve_city(contact: dict[str, Any], default: str = "السعودية") -> str:
    return (contact.get("city") or default).strip()


def _resolve_sector(contact: dict[str, Any], default: str = "default") -> str:
    s = (contact.get("sector") or default).lower().strip()
    return s if s in _OPENERS_BY_SECTOR_AR else "default"


# ── Public API ──────────────────────────────────────────────────
def draft_arabic_message(
    contact: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
    source: str | None = None,
    goal_ar: str = "تشغيل نمو B2B بلا إرسال عشوائي",
) -> dict[str, Any]:
    """
    Build a Saudi-tone Arabic outreach draft.

    - profile: optional ClientGrowthProfile.to_dict() for offer context
    - source: classify_contact_source override; auto-derived if None
    """
    from auto_client_acquisition.growth_operator.contact_importer import (
        classify_contact_source,
    )

    src = source or classify_contact_source(contact)
    name = _resolve_name(contact)
    city = _resolve_city(contact)
    sector = _resolve_sector(contact)
    seed = f"{contact.get('phone','')}{contact.get('name','')}{src}"
    opener = _pick(_OPENERS_BY_SECTOR_AR[sector], seed).format(name=name, city=city)
    reason = _REASON_TEMPLATES_AR.get(src, _REASON_TEMPLATES_AR["unknown"]).format(goal=goal_ar)
    ask = _pick(_ASK_TEMPLATES_AR, seed + "ask")

    offer_line = ""
    if profile and profile.get("offer_one_liner"):
        offer_line = f"\n\nنحن: {profile['offer_one_liner']}."

    body_ar = f"{opener}\n\n{reason}{offer_line}\n\n{ask}"
    return {
        "channel_recommendation": "whatsapp" if contact.get("phone") else "email",
        "subject_ar": None,
        "body_ar": body_ar,
        "source_classification": src,
        "approval_required": True,
        "approval_status": "pending_approval",
        "guardrails_ar": [
            "لا تُرسل قبل موافقة المشغّل.",
            "لا تستخدم في WhatsApp البارد بدون lawful basis.",
            "احذف أي مبالغة قبل الإرسال.",
        ],
        "estimated_length_chars": len(body_ar),
    }


def draft_followup(
    contact: dict[str, Any],
    *,
    days_since_last: int,
    last_outcome: str = "no_reply",
) -> dict[str, Any]:
    """Short follow-up draft based on last outcome."""
    name = _resolve_name(contact)
    seed = f"f{contact.get('phone','')}{last_outcome}{days_since_last}"

    if last_outcome == "no_reply" and days_since_last <= 3:
        body = (
            f"السلام عليكم أستاذ {name}،\n\n"
            "أعرف أن جدولكم مزدحم. لو الفكرة لا تناسب الآن، أقدر أرسل ملخص "
            "بصفحة واحدة تراجعونه على راحتكم. هل أرسل؟"
        )
    elif last_outcome == "no_reply":
        body = (
            f"السلام عليكم أستاذ {name}،\n\n"
            f"مر {days_since_last} يوم على رسالتي السابقة. لو لا يناسب الآن، "
            "أقدر أعود في التوقيت الأنسب لكم — متى يناسب؟"
        )
    elif last_outcome == "objection":
        body = (
            f"شكراً أستاذ {name} على وضوحكم. "
            "بناءً على ما ذكرتم، حضّرت توضيح مختصر يجاوب على نقطتكم تحديداً. "
            "هل أرسل؟"
        )
    elif last_outcome == "positive":
        body = (
            f"شكراً أستاذ {name}. "
            "أحجز ١٥ دقيقة هذا الأسبوع لمناقشة الخطوة التالية — متى يناسبك؟"
        )
    else:
        body = (
            f"السلام عليكم أستاذ {name}،\n\n"
            f"تابعت معكم سابقاً. لو فيه تحديث، يسعدني أعرف."
        )

    return {
        "body_ar": body,
        "purpose": f"followup_{last_outcome}_d{days_since_last}",
        "approval_required": True,
        "approval_status": "pending_approval",
    }


# ── Objection-to-Action library ─────────────────────────────────
_OBJECTION_RESPONSES_AR: dict[str, dict[str, Any]] = {
    "send_offer_whatsapp": {
        "interpretation_ar": "اهتمام متوسط — ليس إغلاق، لكن مفتوح للمعلومات.",
        "response_ar": (
            "تمام، أرسل خلال دقائق ملف صفحتين بالعربي + voice note قصير "
            "يشرح أهم ٣ نقاط. ثم نتفق على متابعة بعد يومين."
        ),
        "next_action": "send_pdf_then_followup_in_2d",
        "score_delta": +5,
    },
    "after_eid": {
        "interpretation_ar": "تأجيل ثقافي مفهوم — احترم التوقيت السعودي.",
        "response_ar": (
            "إن شاء الله. أسجل تذكير لـ بعد العيد بأسبوع، وأرسل لكم Pulse "
            "الشهري حتى ذلك الحين. كل عام وأنتم بخير."
        ),
        "next_action": "schedule_post_eid_followup",
        "score_delta": +1,
    },
    "talk_to_partner": {
        "interpretation_ar": "stakeholder جديد — يحتاج intro + ملف موجز.",
        "response_ar": (
            "محترم — أحضّر لكم ملف من صفحتين بالعربي مهيأ للعرض على الشريك. "
            "هل أرسله مباشرة لكم أو نعمل اجتماع ثلاثي قصير؟"
        ),
        "next_action": "arm_champion_with_2page_brief",
        "score_delta": +3,
    },
    "price_high": {
        "interpretation_ar": "اعتراض قيمة — يحتاج ROI breakdown، ليس خصم.",
        "response_ar": (
            "حقكم تركّزون على القيمة. أرسل ROI breakdown يوضح تكلفة الـ lead "
            "المؤهل لدينا مقارنة بالبدائل. توافقون؟"
        ),
        "next_action": "send_roi_breakdown",
        "score_delta": +5,
    },
    "have_vendor": {
        "interpretation_ar": "منافس قائم — اسأل عن الفجوة الفعلية.",
        "response_ar": (
            "ممتاز — مع مَن؟ والسؤال المهم: هل الـ leads مؤهلة فعلاً أم form fills؟ "
            "إن فيه فجوة، نقدر نكمل وليس نستبدل. مجاناً نعمل audit."
        ),
        "next_action": "offer_free_audit_position_as_complement",
        "score_delta": +2,
    },
    "no_need": {
        "interpretation_ar": "رفض/توقيت — الأنسب nurture بدون ضغط.",
        "response_ar": (
            "متفهم تماماً. نسجلكم في Pulse الشهري المجاني، ونعود حين تتغير "
            "الأولويات. شاكرين وقتكم."
        ),
        "next_action": "nurture_via_monthly_pulse",
        "score_delta": -2,
    },
}


def draft_objection_response(
    objection_id: str,
    *,
    contact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Look up an objection and return a Saudi-toned response draft."""
    obj = _OBJECTION_RESPONSES_AR.get(objection_id)
    if obj is None:
        return {
            "objection_id": objection_id,
            "interpretation_ar": "اعتراض غير مصنّف — يحتاج تشخيص يدوي.",
            "response_ar": (
                "شكراً على وضوحكم. ممكن تشاركوني السبب الرئيسي حتى أعطيكم "
                "إجابة مناسبة؟"
            ),
            "next_action": "diagnostic_question",
            "score_delta": 0,
            "approval_required": True,
            "approval_status": "pending_approval",
        }
    return {
        "objection_id": objection_id,
        **obj,
        "approval_required": True,
        "approval_status": "pending_approval",
    }
