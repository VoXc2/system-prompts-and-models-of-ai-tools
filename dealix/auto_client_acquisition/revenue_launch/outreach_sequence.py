"""First-20 segments and message templates — manual copy only."""

from __future__ import annotations

from typing import Any


def build_first_20_segments() -> dict[str, Any]:
    return {
        "segments": [
            {"id": "agency_b2b", "label_ar": "وكالات B2B", "count": 5},
            {"id": "training", "label_ar": "تدريب واستشارات", "count": 5},
            {"id": "saas", "label_ar": "SaaS / تقنية صغيرة", "count": 5},
            {"id": "services_whatsapp", "label_ar": "خدمات بواتساب نشط", "count": 5},
        ],
        "total": 20,
        "disclaimer_ar": "نسخ يدوي فقط — لا إرسال تلقائي من Dealix.",
        "demo": True,
    }


def build_outreach_message(segment: str) -> dict[str, Any]:
    seg = (segment or "default").lower()
    if seg == "agency_b2b":
        body = (
            "هلا [الاسم]، عندنا Beta للوكالات: Dealix يساعدكم تطلعون فرص لعملائكم، "
            "رسائل عربية، موافقات، وProof Pack. يناسبكم ديمو ١٥ دقيقة؟"
        )
    elif seg == "training":
        body = (
            "هلا [الاسم]، Dealix يطلع فرص B2B لقطاع التدريب مع سبب «لماذا الآن» ورسائل عربية — "
            "أنت توافق قبل أي تواصل. نقدر نعطيكم تشخيصاً مجانياً مختصراً؟"
        )
    else:
        body = (
            "هلا [الاسم]، أطلقنا Beta محدودة لـ Dealix: ١٠ فرص، رسائل عربية، موافقة قبل التواصل، وProof Pack. "
            "أفتح ٥ مقاعد Pilot هذا الأسبوع — يناسبكم؟"
        )
    return {"segment": segment, "body_ar": body, "manual_only": True, "demo": True}


def build_followup_1(_segment: str) -> dict[str, Any]:
    return {
        "body_ar": "متابعة خفيفة: أقدر أرسل عينة ٣ فرص + رسالة واحدة خلال ٢٤ ساعة إذا أعطيتني رابط الموقع والقطاع والمدينة.",
        "manual_only": True,
        "demo": True,
    }


def build_followup_2(_segment: str) -> dict[str, Any]:
    return {
        "body_ar": "إذا التوقيت مو مناسب، أقدر أرجع بعد أسبوعين — أو أغلق الملف برسالة «لا شكراً».",
        "manual_only": True,
        "demo": True,
    }


def build_reply_handlers() -> dict[str, Any]:
    return {
        "handlers_ar": [
            {"trigger": "مهتم", "action_ar": "أرسل رابط التشخيص أو جدول ديمو ١٥ دقيقة."},
            {"trigger": "كم السعر؟", "action_ar": "عرض ٤٩٩ لسبعة أيام أو ١٥٠٠–٣٠٠٠ لـ Growth OS Pilot ٣٠ يوم."},
            {"trigger": "لا شكراً", "action_ar": "شكراً — أغلق السجل بدون متابعة."},
        ],
        "demo": True,
    }
