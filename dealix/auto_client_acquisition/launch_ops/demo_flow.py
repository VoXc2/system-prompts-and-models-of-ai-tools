"""Demo flow — 12-min Arabic demo + discovery + objection handling + close."""

from __future__ import annotations

from typing import Any


def build_12_min_demo_flow() -> dict[str, Any]:
    """The canonical 12-minute Arabic demo plan."""
    return {
        "duration_minutes": 12,
        "minute_by_minute_ar": [
            "0–2: الفكرة الكبرى — Dealix ليس CRM ولا أداة واتساب.",
            "2–4: Daily Brief / Command Feed — 3 قرارات + 3 فرص + 3 مخاطر.",
            "4–6: 10 فرص في 10 دقائق — مثال حي.",
            "6–8: Trust Score + Simulator + Approval Card.",
            "8–10: الأمان والتكاملات — security_curator + connector_catalog.",
            "10–12: العرض والـ CTA — Pilot 7 أيام / 499 ريال.",
        ],
        "demo_endpoints": [
            "/api/v1/personal-operator/daily-brief",
            "/api/v1/intelligence/command-feed/demo",
            "/api/v1/intelligence/missions",
            "/api/v1/targeting/free-diagnostic",
            "/api/v1/services/catalog",
            "/api/v1/launch/private-beta/offer",
        ],
        "do_not_do_in_demo_ar": [
            "لا تكشف API keys على الشاشة.",
            "لا تشغّل live WhatsApp أو Gmail send.",
            "لا تعد بأرقام لم تُحقَّق.",
        ],
    }


def build_discovery_questions() -> list[dict[str, str]]:
    """5 discovery questions to ask in the demo's first 4 minutes."""
    return [
        {"key": "challenge",
         "q_ar": "وش أكبر تحدي نمو لديكم اليوم؟"},
        {"key": "current_targeting",
         "q_ar": "كيف تستهدفون اليوم؟ ما الذي يعمل؟ ما الذي لا يعمل؟"},
        {"key": "time_drain",
         "q_ar": "ما الذي يأخذ وقتاً يومياً ولا يثبت قيمة؟"},
        {"key": "old_list",
         "q_ar": "هل عندكم قائمة عملاء قدامى لم تتم متابعتهم؟"},
        {"key": "approval_owner",
         "q_ar": "من يوافق على الرسائل قبل الإرسال؟"},
    ]


def build_objection_responses() -> dict[str, str]:
    """Standard Arabic objection-handling responses."""
    return {
        "price": (
            "نقدم Free Diagnostic أولاً — تشوفون عينة قبل الدفع. "
            "Pilot 499 ريال أرخص من ساعة عمل في وكالة."
        ),
        "timing": (
            "Pilot 7 أيام لا يحتاج التزام طويل. "
            "نسلّم خلال أسبوع، تقررون بعدها."
        ),
        "trust": (
            "Approval-first: لا نرسل أي شيء بدون موافقتكم. "
            "Audit ledger يسجل كل فعل."
        ),
        "complexity": (
            "Pilot لا يحتاج تكاملات. "
            "نستلم intake في 30 دقيقة ونسلم خلال 24 ساعة."
        ),
        "data_privacy": (
            "PDPL-aware من اليوم الأول. "
            "DPA draft جاهز للتوقيع. "
            "بياناتكم تُخزّن في Supabase KSA-region حسب الإمكان."
        ),
        "results_uncertainty": (
            "لا نضمن أرقاماً، نضمن طريقة تشغيل + Proof Pack مفصّل. "
            "إذا ما اقتنعتم بعد 7 أيام، تأخذون Proof Pack مجاناً وتمشون."
        ),
    }


def build_close_script() -> dict[str, Any]:
    """The closing script — used in minute 11-12 of the demo."""
    return {
        "close_sequence_ar": [
            "هل الفكرة منطقية؟",
            "هل عندك أسئلة محددة قبل ما نبدأ؟",
            "أحدد لكم Pilot يبدأ يوم الأحد القادم — موافق؟",
            "أرسل لكم intake form + invoice خلال ساعة من نهاية المكالمة.",
        ],
        "close_template_ar": (
            "تمام، نبدأ Pilot 7 أيام بـ499 ريال. "
            "أرسل لك خلال ساعة:\n"
            "1. نموذج intake.\n"
            "2. Moyasar invoice.\n"
            "3. تأكيد موعد الكيك-أوف.\n\n"
            "بعد الدفع، Pilot يبدأ يوم الأحد."
        ),
        "if_hesitant_ar": (
            "إذا تحبون عينة قبل الالتزام، أرسل لكم Free Growth Diagnostic "
            "خلال 24 ساعة — 3 فرص + رسالة + توصية، بدون التزام."
        ),
    }
