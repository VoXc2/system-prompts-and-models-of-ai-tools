"""Intelligence Command Feed — Arabic decision cards with ≤3 buttons."""

from __future__ import annotations

from typing import Any

INTEL_CARD_TYPES: tuple[str, ...] = (
    "opportunity",
    "revenue_leak",
    "approval_needed",
    "meeting_prep",
    "payment_followup",
    "partner_suggestion",
    "social_signal",
    "review_response",
    "competitive_move",
)


def build_command_feed_demo() -> dict[str, Any]:
    """Deterministic Arabic command feed for demo + tests."""
    cards = [
        {
            "type": "opportunity",
            "title_ar": "فرصة نمو — شركة تدريب في الرياض",
            "summary_ar": "نشروا 3 وظائف مبيعات جديدة → توسع واضح في فريق المبيعات.",
            "why_it_matters_ar": "التوسع = ميزانية = نافذة شراء ≤30 يوم.",
            "recommended_action_ar": "رسالة قصيرة تعرض تجربة 7 أيام.",
            "expected_impact_sar": 18_000,
            "risk_level": "low",
            "buttons_ar": ("قبول", "تخطّي", "اكتب رسالة"),
        },
        {
            "type": "revenue_leak",
            "title_ar": "تسريب إيراد — 7 leads بلا متابعة",
            "summary_ar": "آخر تواصل قبل 72+ ساعة. الردود تتراجع 14%/ساعة.",
            "why_it_matters_ar": "الإهمال خسارة pipeline متراكمة.",
            "recommended_action_ar": "اعتمد 7 follow-ups جاهزة.",
            "expected_impact_sar": 42_000,
            "risk_level": "medium",
            "buttons_ar": ("اعتمد", "عدّل", "تخطّي"),
        },
        {
            "type": "partner_suggestion",
            "title_ar": "فرصة شراكة — وكالة B2B في جدة",
            "summary_ar": "عملاؤها يحتاجون lead-gen → Dealix يكمل خدماتها.",
            "why_it_matters_ar": "الشراكة الواحدة تفتح 3-5 leads warmer.",
            "recommended_action_ar": "رسالة partnership warm + اقتراح pilot.",
            "expected_impact_sar": 60_000,
            "risk_level": "low",
            "buttons_ar": ("اكتب رسالة", "احجز اجتماع", "تخطّي"),
        },
        {
            "type": "meeting_prep",
            "title_ar": "اجتماع غداً مع شركة العقار الذهبي",
            "summary_ar": "جاهز: ملف الشركة + 5 أسئلة + 3 اعتراضات + عرض مناسب.",
            "why_it_matters_ar": "الاجتماع المُحضَّر يرفع الإغلاق 40%+.",
            "recommended_action_ar": "افتح التحضير + راجع الأجندة.",
            "expected_impact_sar": 250_000,
            "risk_level": "low",
            "buttons_ar": ("افتح التحضير", "اكتب أجندة", "أرسل تأكيد"),
        },
        {
            "type": "review_response",
            "title_ar": "تقييم Google جديد — 2 نجوم",
            "summary_ar": "العميل اشتكى من التأخر في الرد.",
            "why_it_matters_ar": "تقييم سلبي بدون رد ≤24 ساعة يضرّ السمعة المحلية.",
            "recommended_action_ar": "اعتذار قصير + طلب تواصل + حل.",
            "expected_impact_sar": 1_000,
            "risk_level": "high",
            "buttons_ar": ("اعتمد الرد", "صعّد للمدير", "تخطّي"),
        },
        {
            "type": "competitive_move",
            "title_ar": "منافس أطلق pricing جديد",
            "summary_ar": "خفّضوا 15% على باقة Growth — يستهدفون نفس عملاءك.",
            "why_it_matters_ar": "الردود السريعة تحفظ الـ pipeline.",
            "recommended_action_ar": "حملة مضادة + ROI breakdown مقارن.",
            "expected_impact_sar": 80_000,
            "risk_level": "medium",
            "buttons_ar": ("جهّز رد", "نبّه المبيعات", "تخطّي"),
        },
    ]
    # Validate constraints
    for c in cards:
        assert c["type"] in INTEL_CARD_TYPES
        assert len(c["buttons_ar"]) <= 3
    return {
        "feed_size": len(cards),
        "cards": cards,
        "policy_note_ar": "كل كرت عربي + ≤3 buttons + approval-aware.",
    }
