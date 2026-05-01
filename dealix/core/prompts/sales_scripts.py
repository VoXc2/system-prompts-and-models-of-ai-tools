"""
Bilingual sales scripts — opening, follow-up, demo, close.
سكربتات مبيعات ثنائية اللغة.
"""

from __future__ import annotations

SALES_SCRIPTS: dict[str, dict[str, str]] = {
    "opener": {
        "ar": (
            "السلام عليكم {name}،\n\n"
            "لاحظت أن شركتكم في {sector} عندها فرصة واضحة لتحسين سرعة "
            "المتابعة وتحويل الاستفسارات إلى اجتماعات وعروض أسرع.\n\n"
            "عندنا نظام AI منظم يلتقط العميل، يفهم احتياجه، ويجهز handoff "
            "واضح للمبيعات. إذا مناسب لك، أعرض لك demo مختصر جداً (10 دقائق).\n\n"
            "شاكر لك."
        ),
        "en": (
            "Hi {name},\n\n"
            "I noticed companies in {sector} often leave revenue on the table "
            "due to slow lead follow-up and unclear qualification.\n\n"
            "We've built an AI system that captures leads, understands their "
            "needs, and prepares clear handoffs for sales. If you're open, "
            "I'd love to walk you through a quick 10-minute demo.\n\n"
            "Best regards."
        ),
    },
    "follow_up_1": {
        "ar": (
            "{name}، مرحباً مرة أخرى.\n\n"
            "أرسلت لك قبل أيام حول نظام AI للمبيعات في {sector}. "
            "أكثر الشركات في قطاعك تخسر حوالي 30-40% من الاستفسارات "
            "بسبب التأخير أو عدم وجود qualification واضح.\n\n"
            "إذا مناسب، أرسل لك مثال مباشر على كيف يشتغل النظام عندكم."
        ),
        "en": (
            "Hi {name}, circling back.\n\n"
            "Sent a note earlier about our AI sales system for {sector}. "
            "Most companies in your sector lose 30-40% of inquiries to slow "
            "response or weak qualification.\n\n"
            "Happy to share a concrete example of how this would work for you."
        ),
    },
    "follow_up_2": {
        "ar": (
            "{name}، أحترم وقتك.\n\n"
            "إذا التوقيت مش مناسب الآن، أتفهم تماماً. سأكتفي بمتابعة واحدة "
            "بعد شهرين. إذا تغير الوضع قبل ذلك، المرحب."
        ),
        "en": (
            "{name}, respecting your time.\n\n"
            "If the timing isn't right, I fully understand. I'll circle back "
            "in ~2 months. If anything shifts before then, you know where to find me."
        ),
    },
    "demo_confirm": {
        "ar": (
            "ممتاز {name}! تم تأكيد الموعد:\n"
            "📅 التاريخ: {date}\n"
            "⏰ الوقت: {time} (توقيت الرياض)\n"
            "🔗 الرابط: {link}\n\n"
            "سأرسل تذكير قبل الموعد بساعة. إذا احتجت تغيير، فقط أرسل لي."
        ),
        "en": (
            "Great, {name}! Confirmed:\n"
            "📅 Date: {date}\n"
            "⏰ Time: {time} (Riyadh time)\n"
            "🔗 Link: {link}\n\n"
            "I'll send a reminder 1 hour before. Reply anytime to reschedule."
        ),
    },
    "proposal_cover": {
        "ar": (
            "الأستاذ/ة {name}،\n\n"
            "مرفق العرض المُعد خصيصاً لـ {company}. يغطي:\n"
            "• فهمنا لاحتياجاتكم\n"
            "• الحل المقترح والمراحل\n"
            "• الأسعار بالريال السعودي\n"
            "• الخطوات التالية\n\n"
            "سعيد بأي ملاحظات أو أسئلة."
        ),
        "en": (
            "Dear {name},\n\n"
            "Please find attached the proposal tailored for {company}, covering:\n"
            "• Our understanding of your needs\n"
            "• Proposed solution and phases\n"
            "• Pricing in SAR\n"
            "• Next steps\n\n"
            "Happy to discuss any questions."
        ),
    },
}


def get_sales_script(script_type: str, locale: str = "ar", **kwargs: object) -> str:
    """Get a formatted sales script | جلب سكربت مبيعات."""
    script = SALES_SCRIPTS.get(script_type, {}).get(locale)
    if script is None:
        raise KeyError(f"Unknown script '{script_type}' for locale '{locale}'")
    try:
        return script.format(**kwargs)
    except KeyError:
        return script  # return raw if missing keys
