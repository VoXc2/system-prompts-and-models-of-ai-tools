"""Private Beta offer — today's offer + safety notes + FAQ."""

from __future__ import annotations

from typing import Any

PRIVATE_BETA_OFFER: dict[str, Any] = {
    "offer_id": "private_beta_pilot_7d",
    "name_ar": "Private Beta Pilot — 7 أيام",
    "promise_ar": (
        "خلال 7 أيام نطلع لك 10 فرص B2B + رسائل عربية + خطة متابعة + Proof Pack، "
        "وأنت توافق قبل أي تواصل."
    ),
    "deliverables_ar": [
        "10 فرص B2B مع why-now + buying committee.",
        "10 رسائل عربية بنبرة سعودية طبيعية.",
        "تصنيف القنوات (safe / needs_review / blocked) لكل contact.",
        "خطة متابعة 7 أيام.",
        "Proof Pack مختصر (PDF + JSON).",
        "جلسة مراجعة 30 دقيقة في نهاية الأسبوع.",
    ],
    "price_sar": 499,
    "free_alternative_ar": "مجاني مقابل case study بعد انتهاء الـ Pilot.",
    "approval_required": True,
    "live_send_allowed": False,
    "duration_days": 7,
    "seats_available": 5,
}


def build_private_beta_offer(*, seats_remaining: int | None = None) -> dict[str, Any]:
    """Build today's Private Beta offer card. Seats are configurable."""
    out = dict(PRIVATE_BETA_OFFER)
    if seats_remaining is not None:
        out["seats_available"] = max(0, int(seats_remaining))
    out["upsell_path"] = [
        "growth_os_pilot_30d",
        "growth_os_monthly",
    ]
    return out


def build_private_beta_safety_notes() -> dict[str, Any]:
    """Return the explicit 'what we will NOT do today' list."""
    return {
        "title_ar": "ضمانات Dealix",
        "do_not_do_ar": [
            "لا live WhatsApp send بدون env flag + اعتماد بشري.",
            "لا live Gmail send.",
            "لا Calendar insert تلقائي.",
            "لا charge Moyasar تلقائي — invoice/payment link يدوي فقط.",
            "لا scraping LinkedIn ولا auto-DM.",
            "لا cold WhatsApp (PDPL).",
            "لا وعود بنتائج مضمونة.",
            "لا تخزين بيانات بطاقات.",
        ],
        "do_ar": [
            "Approval-first في كل قناة.",
            "Audit ledger لكل فعل.",
            "Saudi Tone + Safety eval قبل أي رسالة.",
            "Reputation Guard يوقف القناة عند تدهور السمعة.",
            "Free Diagnostic قبل أي التزام.",
        ],
    }


def private_beta_faq() -> list[dict[str, str]]:
    """Common Arabic FAQ entries for the Private Beta page."""
    return [
        {
            "q_ar": "كيف يعمل Pilot الـ7 أيام؟",
            "a_ar": (
                "نأخذ منك intake (قطاع/مدينة/عرض/هدف) خلال 30 دقيقة. "
                "خلال 24 ساعة عمل نسلّم 10 فرص + رسائل + تصنيف القنوات. "
                "خلال الأسبوع نتابع الردود ونحدّث Proof Pack."
            ),
        },
        {
            "q_ar": "هل ترسلون رسائل بدون موافقتي؟",
            "a_ar": "لا. كل رسالة تظل draft حتى توافق عليها صراحة.",
        },
        {
            "q_ar": "ماذا لو ما رد أحد؟",
            "a_ar": (
                "Proof Pack يوضح المخاطر التي منعناها + توصية بقطاع/زاوية مختلفة. "
                "Pilot يثبت طريقة التشغيل وليس عدداً مضموناً من الصفقات."
            ),
        },
        {
            "q_ar": "هل تعرفون شروط واتساب ولينكدإن؟",
            "a_ar": (
                "نعم. لا cold WhatsApp بدون opt-in. "
                "لا scraping ولا auto-DM في LinkedIn — نستخدم Lead Gen Forms والمهام اليدوية."
            ),
        },
        {
            "q_ar": "كيف أدفع 499 ريال؟",
            "a_ar": (
                "نرسل لك Moyasar invoice أو payment link من الـ dashboard. "
                "بعد الدفع نبدأ Pilot يوم الأحد التالي."
            ),
        },
        {
            "q_ar": "هل يصلح للوكالات؟",
            "a_ar": (
                "نعم — Agency Partner Program يعطي الوكالة co-branded Proof Pack + "
                "revenue share على عملائها. تواصل معنا مباشرة للترتيب."
            ),
        },
    ]
