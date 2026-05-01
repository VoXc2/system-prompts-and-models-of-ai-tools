"""
Reply classifier + negotiation agent.

Two-tier:
1. Rule-based fast path (regex on Khaliji + English) — no API cost.
2. Optional LLM upgrade via core.llm.router when GROQ_API_KEY is set —
   handles ambiguous replies + generates the response draft.

Classifications:
    interested            — books demo / ready to start
    ask_price             — wants pricing
    ask_details           — wants more info
    ask_demo              — wants a demo
    not_now               — defer 30 days
    objection_budget      — too expensive
    objection_ai          — distrusts AI / wants human
    objection_privacy     — PDPL / data residency concerns
    already_has_crm       — has HubSpot/Salesforce
    partnership           — wants to be partner not customer
    unsubscribe           — STOP / OPT OUT / إيقاف
    angry                 — hostile reply
    unclear               — needs human review

Returns: ReplyClassification with:
    category, confidence, response_draft_ar, auto_send_allowed,
    next_action, deal_stage, followup_days
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, asdict
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class ReplyClassification:
    category: str
    confidence: float  # 0.0..1.0
    response_draft_ar: str
    response_draft_en: str | None
    auto_send_allowed: bool
    next_action: str
    deal_stage: str
    followup_days: int | None  # None means stop
    notes: list[str]
    requires_human_review: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Regex patterns (Khaliji + English) ────────────────────────────
PATTERNS: list[tuple[str, list[re.Pattern]]] = [
    ("unsubscribe", [
        re.compile(r"\b(STOP|UNSUBSCRIBE|opt[\s-]?out|إيقاف|إلغاء|أوقف|توقف|لا تتواصل)\b", re.IGNORECASE),
    ]),
    ("interested", [
        re.compile(r"(نعم تجربة|ابدأ|نبدأ|نشتغل|قبلت|ودي|أبي اشترك|sign me up|let'?s start|i'?m in)", re.IGNORECASE),
    ]),
    ("ask_demo", [
        re.compile(r"(demo|عرض توضيحي|ديمو|مكالمة|اجتماع|نتقابل|meeting|اتصال)", re.IGNORECASE),
    ]),
    ("ask_price", [
        re.compile(r"(كم\s*السعر|التكلفة|السعر|كم|how much|pricing|cost|price)", re.IGNORECASE),
    ]),
    ("ask_details", [
        re.compile(r"(تفاصيل|كيف يعمل|اشرح|توضيح|how does it work|tell me more|details)", re.IGNORECASE),
    ]),
    ("objection_budget", [
        re.compile(r"(غالي|ميزانية|باهظ|too expensive|out of budget|cant afford)", re.IGNORECASE),
    ]),
    ("objection_ai", [
        re.compile(r"(ai|روبوت|إنسان حقيقي|real person|automated|ما أبي ذكاء|robotic)", re.IGNORECASE),
    ]),
    ("objection_privacy", [
        re.compile(r"(خصوصية|بيانات|PDPL|GDPR|privacy|data residency|سرية)", re.IGNORECASE),
    ]),
    ("already_has_crm", [
        re.compile(r"(عندنا|نستخدم|HubSpot|Salesforce|Zoho|Bitrix|CRM موجود|already have)", re.IGNORECASE),
    ]),
    ("partnership", [
        re.compile(r"(شراكة|شركاء|توزيع|reseller|partner|agency)", re.IGNORECASE),
    ]),
    ("not_now", [
        re.compile(r"(ليس الآن|لاحقاً|بعد رمضان|بعد العيد|next quarter|not now|later|maybe later)", re.IGNORECASE),
    ]),
    ("angry", [
        re.compile(r"(stop emailing|سبام|spam|ازعاج|إزعاج|اشتكي|complaint)", re.IGNORECASE),
    ]),
]

RESPONSE_TEMPLATES: dict[str, dict[str, Any]] = {
    "interested": {
        "ar": "ممتاز! هذا رابط Calendly نختار وقت يناسبكم: https://calendly.com/sami-assiri11/dealix-demo. "
              "خلال المكالمة نحدد leadsكم الحالية ونبدأ Pilot يوم الإثنين.",
        "auto_send_allowed": False,  # Sami confirms first
        "next_action": "send_calendly_link", "deal_stage": "demo_scheduled",
        "followup_days": None,
    },
    "ask_demo": {
        "ar": "ممتاز. تفضلوا اختاروا وقت يناسبكم من Calendly: "
              "https://calendly.com/sami-assiri11/dealix-demo — 20 دقيقة.",
        "auto_send_allowed": False,
        "next_action": "send_calendly_link", "deal_stage": "demo_offered",
        "followup_days": 2,
    },
    "ask_price": {
        "ar": "Pilot 7 أيام بـ 499 ريال — استرجاع كامل لو لم نرد على lead واحد بالعربي. "
              "بعد البايلوت Starter 999/شهر، Growth 2,499/شهر، Pro 5,000/شهر. "
              "تبغوا نوضح بمكالمة 20 دقيقة؟",
        "auto_send_allowed": False,
        "next_action": "send_pricing_then_offer_call", "deal_stage": "pricing_sent",
        "followup_days": 2,
    },
    "ask_details": {
        "ar": "Dealix يستقبل leads من website / WhatsApp / inbound email، "
              "يرد بالعربي خلال 45 ثانية، يأخذ التفاصيل (الميزانية + الموقع + الموعد)، "
              "ويسلم العميل المؤهل لمندوبكم. تبغوا أرسل لكم demo جاهز أم نتقابل 20 دقيقة؟",
        "auto_send_allowed": False,
        "next_action": "send_explainer_then_demo_ask", "deal_stage": "info_sent",
        "followup_days": 3,
    },
    "objection_budget": {
        "ar": "أفهم. Pilot 499 ريال هو أرخص طريقة تختبروا فعلاً قبل أي اشتراك. "
              "لو ما اقتنعتم خلال 3 أيام، استرجاع كامل. تجربة بدون مخاطرة فعلياً.",
        "auto_send_allowed": False,
        "next_action": "reframe_pilot_as_low_risk", "deal_stage": "objection_handling",
        "followup_days": 5,
    },
    "objection_ai": {
        "ar": "صحيح، AI لوحده لا يكفي. Dealix يرد بالعربي الخليجي + يحدد الـ leads "
              "الجادة، ثم يحول للمندوب البشري للإغلاق. النظام يكمل عمل فريقكم، ما يستبدله. "
              "تبون نريكم مثال على نشاطكم؟",
        "auto_send_allowed": False,
        "next_action": "explain_human_in_loop_model", "deal_stage": "objection_handling",
        "followup_days": 5,
    },
    "objection_privacy": {
        "ar": "Dealix متوافق مع PDPL من اليوم الأول — كل بيانات leads تُحفظ في Postgres "
              "مع opt-out + suppression list مفروضة قبل أي رد. نقدر نرسلكم data flow diagram "
              "+ الجزء المتعلق بـ PDPL في docs/ops/ — تبغوا؟",
        "auto_send_allowed": False,
        "next_action": "send_pdpl_compliance_doc", "deal_stage": "compliance_review",
        "followup_days": 3,
    },
    "already_has_crm": {
        "ar": "ممتاز. Dealix يتكامل مع HubSpot/Salesforce/Zoho/Bitrix كـ AI sales rep "
              "يجلس فوق CRM الحالي ويسلم العميل المؤهل لـ pipelineكم. لا نستبدل، "
              "نضيف طبقة الرد السريع بالعربي. تبغوا 20 دقيقة نشرح كيف؟",
        "auto_send_allowed": False,
        "next_action": "explain_layered_integration", "deal_stage": "qualified",
        "followup_days": 3,
    },
    "partnership": {
        "ar": "ممتاز — لكم مسارين: (1) تستخدمون Dealix لعملائكم وتحصلون 25% MRR شهرياً، "
              "أو (2) تشترون لوكالتكم. كلاهما revenue share. رابط نظرة عامة: "
              "https://dealix.me/partners.html — تبغوا 20 دقيقة نوضح؟",
        "auto_send_allowed": False,
        "next_action": "route_to_partner_flow", "deal_stage": "partner_qualified",
        "followup_days": 2,
    },
    "not_now": {
        "ar": "متفهم. سأتابع معكم بعد 30 يوماً. لو احتجتم شيء قبل ذلك، أنا هنا. "
              "(لإلغاء الاستلام: ردّ بـ STOP)",
        "auto_send_allowed": True,  # safe deferral
        "next_action": "schedule_30day_followup", "deal_stage": "nurture",
        "followup_days": 30,
    },
    "unsubscribe": {
        "ar": "تم إيقاف التواصل. لن أتواصل مرة ثانية. شكراً لوقتكم.",
        "auto_send_allowed": True,  # mandatory ack
        "next_action": "add_to_suppression_immediately", "deal_stage": "opted_out",
        "followup_days": None,
    },
    "angry": {
        "ar": "أعتذر بشدة على الإزعاج. تم حذف عنوانكم من قائمتنا الآن.",
        "auto_send_allowed": False,  # human must read first
        "next_action": "human_review_immediate_then_suppress", "deal_stage": "complaint",
        "followup_days": None,
    },
    "unclear": {
        "ar": "شكراً للرد — هل ممكن توضيح الجانب الذي يهمكم في Dealix أكثر؟",
        "auto_send_allowed": False,
        "next_action": "human_review", "deal_stage": "needs_clarification",
        "followup_days": 3,
    },
}


def classify_rule_based(text: str) -> tuple[str, float]:
    """Fast regex-only classification. Returns (category, confidence)."""
    text = (text or "").strip()
    if not text:
        return "unclear", 0.1

    # Multiple matches = check priority order (unsubscribe always wins, angry second)
    matches: list[tuple[str, int]] = []
    for category, patterns in PATTERNS:
        hits = 0
        for p in patterns:
            if p.search(text):
                hits += 1
        if hits:
            matches.append((category, hits))

    if not matches:
        return "unclear", 0.2

    # Priority order overrides hit count for safety-critical
    priority = {
        "unsubscribe": 100, "angry": 90, "interested": 80,
        "objection_budget": 70, "objection_ai": 70, "objection_privacy": 70,
        "ask_demo": 60, "ask_price": 55, "partnership": 55,
        "already_has_crm": 50, "ask_details": 45, "not_now": 40,
    }
    matches.sort(key=lambda x: (-priority.get(x[0], 0), -x[1]))
    best_cat, hit_count = matches[0]
    confidence = min(0.9, 0.5 + 0.1 * hit_count)
    return best_cat, confidence


def build_classification(category: str, confidence: float, original_text: str) -> ReplyClassification:
    tpl = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["unclear"])
    requires_review = (
        category in {"angry", "objection_privacy", "unclear"}
        or confidence < 0.5
        or len(original_text) > 1000  # long replies always need human eyes
    )
    return ReplyClassification(
        category=category,
        confidence=confidence,
        response_draft_ar=tpl["ar"],
        response_draft_en=None,  # generated lazily by /reply/translate if needed
        auto_send_allowed=bool(tpl["auto_send_allowed"]) and not requires_review,
        next_action=tpl["next_action"],
        deal_stage=tpl["deal_stage"],
        followup_days=tpl["followup_days"],
        notes=[],
        requires_human_review=requires_review,
    )


async def classify_with_llm(text: str) -> ReplyClassification | None:
    """
    Optional LLM upgrade. Returns None if no LLM key — caller falls back to rules.
    """
    import os
    if not (os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        return None
    try:
        from core.llm.router import get_router
        from core.llm.base import Message
    except Exception:
        return None

    prompt = (
        "أنت classifier لردود الإيميل التجارية باللغة العربية الخليجية + الإنجليزية.\n"
        "صنّف هذا الرد إلى واحدة من: interested, ask_price, ask_details, ask_demo, "
        "not_now, objection_budget, objection_ai, objection_privacy, already_has_crm, "
        "partnership, unsubscribe, angry, unclear.\n\n"
        f"الرد:\n{text[:1500]}\n\n"
        "أرجع JSON فقط بهذا الشكل:\n"
        '{"category": "...", "confidence": 0.0-1.0, "reasoning": "...", "suggested_response_ar": "..."}'
    )
    try:
        router = get_router()
        msg = Message(role="user", content=prompt)
        resp = await router.complete([msg], max_tokens=400, temperature=0.2)
    except Exception as exc:  # noqa: BLE001
        log.warning("llm_classify_failed err=%s", exc)
        return None

    import json
    text_out = (resp.content or "").strip()
    # Extract JSON if wrapped
    m = re.search(r"\{[^{}]*\"category\"[^{}]*\}", text_out, re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except Exception:
        return None
    cat = str(data.get("category") or "unclear")
    conf = float(data.get("confidence") or 0.6)
    base = build_classification(cat, conf, text)
    # Override response with LLM-suggested if present
    if data.get("suggested_response_ar"):
        base.response_draft_ar = str(data["suggested_response_ar"])[:2000]
    base.notes.append(f"llm_reasoning: {str(data.get('reasoning',''))[:200]}")
    return base


async def classify_reply(text: str, *, prefer_llm: bool = True) -> ReplyClassification:
    """
    Main entry point. Tries LLM first if available + prefer_llm; falls back to rules.
    """
    if prefer_llm:
        llm_result = await classify_with_llm(text)
        if llm_result is not None:
            return llm_result
    cat, conf = classify_rule_based(text)
    return build_classification(cat, conf, text)
