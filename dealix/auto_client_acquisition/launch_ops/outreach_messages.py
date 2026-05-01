"""First 20 outreach segments + per-segment Arabic messages + reply handlers."""

from __future__ import annotations

from typing import Any


def build_first_20_segments() -> dict[str, Any]:
    """The deterministic first-20 plan — 4 segments × 5 prospects each."""
    return {
        "total_targets": 20,
        "segments": [
            {
                "id": "agency_b2b",
                "label_ar": "وكالات تسويق B2B",
                "count": 5,
                "best_offer_id": "agency_partner_program",
                "fallback_offer_id": "partner_sprint",
                "primary_channel": "email",
            },
            {
                "id": "training_consulting",
                "label_ar": "شركات تدريب واستشارات",
                "count": 5,
                "best_offer_id": "first_10_opportunities_sprint",
                "fallback_offer_id": "free_growth_diagnostic",
                "primary_channel": "email",
            },
            {
                "id": "saas_tech_small",
                "label_ar": "SaaS / تقنية صغيرة",
                "count": 5,
                "best_offer_id": "first_10_opportunities_sprint",
                "fallback_offer_id": "growth_os_monthly",
                "primary_channel": "linkedin_lead_form",
            },
            {
                "id": "services_with_whatsapp",
                "label_ar": "شركات خدمات لديها واتساب نشط",
                "count": 5,
                "best_offer_id": "list_intelligence",
                "fallback_offer_id": "whatsapp_compliance_setup",
                "primary_channel": "email",
            },
        ],
        "rules_ar": [
            "لا scraping ولا قوائم مشتراة.",
            "استخدم علاقاتك المباشرة + جهات تعرفها.",
            "كل رسالة يدوية، لا automation.",
            "حد أقصى 3 follow-ups ثم أرشفة.",
        ],
    }


_BASE_INTRO = "هلا [الاسم]، أطلقنا Beta محدودة لـ Dealix."


def build_outreach_message(segment_id: str, *, name: str = "[الاسم]") -> dict[str, Any]:
    """Build the first-touch Arabic message for a segment."""
    intro = f"هلا {name}،"

    if segment_id == "agency_b2b":
        body = (
            f"{intro} عندي Beta خاص للوكالات.\n\n"
            "Dealix يساعد الوكالة تطلع فرص لعملائها، تجهز رسائل عربية، تدير "
            "موافقات، وتطلع Proof Pack باسم الوكالة والعميل.\n\n"
            "أبحث عن وكالة واحدة نجرب معها Pilot مشترك على عميل حقيقي. "
            "يناسبك ديمو 15 دقيقة؟"
        )
    elif segment_id == "training_consulting":
        body = (
            f"{intro} متابع توسع شركتكم في برامج الشركات.\n\n"
            "Dealix يطلع لكم 10 فرص B2B خلال 7 أيام، يكتب الرسائل بالعربي، "
            "ويخلي صاحب القرار يوافق قبل أي تواصل، وبعدها يعطي Proof Pack.\n\n"
            "Pilot بـ499 ريال أو مجاني مقابل case study. يناسبك ديمو 12 دقيقة؟"
        )
    elif segment_id == "saas_tech_small":
        body = (
            f"{intro} رأيت إصدار النسخة الجديدة من منتجكم — مبروك.\n\n"
            "نشتغل على مدير نمو عربي يطلع 10 فرص B2B، يستخدم LinkedIn Lead "
            "Forms (لا scraping)، ويكتب الرسائل بالعربي.\n\n"
            "أبغى أجربه مع شركة SaaS سعودية واحدة. يناسبك ديمو 12 دقيقة؟"
        )
    elif segment_id == "services_with_whatsapp":
        body = (
            f"{intro} عندكم قاعدة عملاء واتساب نشطة، صحيح؟\n\n"
            "Dealix ينظف القائمة، يصنف الـ opt-in، يحظر cold WhatsApp تلقائياً، "
            "ويكتب رسائل عربية للحملات الآمنة + Proof Pack شهري.\n\n"
            "List Intelligence بـ499–1,500 ريال. يناسبك أعطيك تشخيص مجاني أولاً؟"
        )
    else:
        body = (
            f"{intro} {_BASE_INTRO}\n\n"
            "Dealix يطلع لك 10 فرص B2B + رسائل عربية + Proof Pack — "
            "وأنت توافق قبل أي تواصل. Pilot 7 أيام بـ499 ريال. "
            "يناسبك ديمو 12 دقيقة؟"
        )

    return {
        "segment_id": segment_id,
        "channel": "email_or_dm",
        "body_ar": body,
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_followup_message(
    segment_id: str, *, step: int = 1, name: str = "[الاسم]",
) -> dict[str, Any]:
    """Build follow-up #1, #2, or #3 (final archive)."""
    if step <= 1:
        body = (
            f"هلا {name}، أرسل لك مثال سريع بدل شرح طويل؟\n"
            "أقدر أطلع لك عينة من 3 فرص مناسبة لشركتكم + رسالة واحدة جاهزة + "
            "ملاحظة عن أفضل قناة. إذا أعجبتك نكمل Pilot كامل."
        )
        kind = "followup_1"
    elif step == 2:
        body = (
            f"هلا {name}، أعرف أن وقتك مزدحم.\n"
            "سؤال أخير: لو طلعت لك 3 فرص B2B بالعربي مجاناً هذا الأسبوع، "
            "تعطيني 15 دقيقة feedback؟"
        )
        kind = "followup_2"
    else:
        body = (
            f"هلا {name}، أعتذر على الإلحاح.\n"
            "أرشّفها وأكون موجود لو احتجتني لاحقاً. شاكر لك."
        )
        kind = "followup_3_final"

    return {
        "segment_id": segment_id,
        "step": step,
        "kind": kind,
        "body_ar": body,
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_reply_handlers() -> dict[str, dict[str, str]]:
    """Standard reply-classifier → response mapping (Arabic)."""
    return {
        "interested": {
            "label_ar": "مهتم",
            "response_ar": (
                "ممتاز. أرسل لك intake form + موعد ديمو 12 دقيقة هذا الأسبوع. "
                "أي وقت يناسبك بين 10 ص و 5 م؟"
            ),
            "next_action": "send_intake_and_demo_link",
        },
        "needs_more_info": {
            "label_ar": "يحتاج معلومات أكثر",
            "response_ar": (
                "أرسل لك Free Growth Diagnostic — 3 فرص + رسالة + توصية، "
                "بدون التزام. أحتاج فقط: قطاعكم، مدينتكم، عرضكم الرئيسي."
            ),
            "next_action": "send_free_diagnostic_intake",
        },
        "price_objection": {
            "label_ar": "اعتراض سعر",
            "response_ar": (
                "تمام، نبدأ بـ Free Diagnostic مجاناً. "
                "تشوفون النتائج قبل أي دفع."
            ),
            "next_action": "send_free_diagnostic_intake",
        },
        "not_now": {
            "label_ar": "ليس الآن",
            "response_ar": (
                "تمام، شاكر لك. أتواصل معك بعد شهرين بدون إلحاح. "
                "إن احتجتنا قبل، أنا موجود."
            ),
            "next_action": "schedule_followup_60_days",
        },
        "no_thanks": {
            "label_ar": "غير مهتم",
            "response_ar": "تمام، شاكر لك. أرشّفها وأتمنى لكم التوفيق.",
            "next_action": "archive",
        },
        "unsubscribe": {
            "label_ar": "إلغاء",
            "response_ar": "تم. لن أتواصل معك مجدداً.",
            "next_action": "honor_opt_out_immediately",
        },
    }
