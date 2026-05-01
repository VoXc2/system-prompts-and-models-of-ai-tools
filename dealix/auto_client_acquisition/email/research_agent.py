"""
Company Research Agent — produces a per-account brief used by the email generator.

Output (CompanyBrief):
    company_brief        — 2-line summary
    pain_hypothesis      — what likely hurts this company
    dealix_fit           — why Dealix specifically helps
    expected_gain        — conservative qualitative hint (no guarantees)
    best_offer           — one of: pilot_499 / pilot_999 / pilot_1500 / partnership
    best_channel         — email / phone_task / linkedin_manual
    best_first_sentence  — Khaliji opener tailored to sector
    objection_risks      — likely 1-2 objections to prep for
    risk_note            — compliance flags
    confidence           — 0..1
    sources_used         — list of strings (e.g. "tech_signal:WhatsApp", "directory:saudi_business_directory")

Two-tier:
1. Deterministic per-sector rules (always runs).
2. Optional LLM polish via Groq (one short call) — produces a single sharper paragraph.
"""

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class CompanyBrief:
    company_name: str
    company_brief: str
    pain_hypothesis: str
    dealix_fit: str
    expected_gain: str
    best_offer: str
    best_channel: str
    best_first_sentence: str
    objection_risks: list[str]
    risk_note: str
    confidence: float
    sources_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SECTOR_BRIEFS: dict[str, dict[str, Any]] = {
    "real_estate_developer": {
        "brief": "مطور عقاري سعودي يستقبل leads من الإعلانات + الموقع + WhatsApp.",
        "pain": "leads متعددة في وقت قصير — تأخر الرد دقيقة واحدة قد يخسر العميل لمنافس.",
        "fit": "Dealix يرد بالعربي خلال 45 ثانية، يأخذ الميزانية + الموقع + موعد المعاينة، ويحجز للمندوب الجاهز.",
        "gain": "غالباً 5-15 lead دافئ إضافي شهرياً عند تحسين زمن الرد بـ 80%.",
        "objections": ["budget_for_pilot", "concern_about_arabic_quality", "already_uses_simple_chat_widget"],
        "first_sentence": "كل lead عقاري متأخر دقيقة = احتمال خسارة العميل لمنافس.",
        "best_offer": "pilot_499", "best_channel": "phone_task",
    },
    "real_estate": {
        "brief": "مكتب عقار سعودي للوساطة العقارية.",
        "pain": "الردود متناثرة بين موظفين مختلفين على واتساب — لا يوجد فرز أولوية.",
        "fit": "Dealix يستقبل الاستفسار، يأخذ التفاصيل، ويحوّل العميل الجاهز للوسيط الصح.",
        "gain": "غالباً تحسين conversion ratio على inbound من 5% إلى 12%.",
        "objections": ["small_team_concern", "trust_in_AI"],
        "first_sentence": "العمولة الواحدة في العقار = ربح أسبوع. لا تخسرونها بسبب وقت الرد.",
        "best_offer": "pilot_499", "best_channel": "phone_task",
    },
    "construction": {
        "brief": "شركة مقاولات سعودية تستقبل طلبات تسعير من شركات وأفراد.",
        "pain": "RFQ تتوزع بين واتساب + اتصالات + إيميلات بدون فرز موحّد.",
        "fit": "Dealix يستقبل كل RFQ، يجمع المواصفات + الميزانية + المهلة، ويفرز الجاهز للتسعير.",
        "gain": "غالباً تقليل RFQ المهملة بنسبة 30-50%، وتحسين معدل تحويل التسعير لعقد.",
        "objections": ["large_project_complexity", "needs_human_engineer_review"],
        "first_sentence": "بدل ما تضيع طلبات تسعير المشاريع بين قنوات متعددة، نجمعها في مكان واحد.",
        "best_offer": "pilot_999", "best_channel": "phone_task",
    },
    "hospitality": {
        "brief": "فندق سعودي يستقبل حجوزات + استفسارات MICE/قاعات/إفطار-سحور.",
        "pain": "الاستفسارات تأتي بأي وقت، الموظف غير متاح ليلاً = خسارة حجز.",
        "fit": "Dealix يستقبل، يأخذ التاريخ + العدد + الباقة، ويحجز موعد معاينة في تقويم الفريق.",
        "gain": "غالباً استرجاع 10-20% من حجوزات MICE المهملة عبر الرد الفوري.",
        "objections": ["existing_PMS_system", "concern_about_pricing_quotes"],
        "first_sentence": "حجوزات MICE + قاعات = leads تحتاج رد فوري بأي ساعة.",
        "best_offer": "pilot_999", "best_channel": "phone_task",
    },
    "events": {
        "brief": "قاعة حفلات / مزود تأجير معدات حفلات سعودي.",
        "pain": "كل lead = موسم. خسارة واحدة = 5K-100K ريال ضائعة.",
        "fit": "Dealix يستقبل، يأخذ التاريخ + العدد + الباقة + الميزانية، ويحجز معاينة.",
        "gain": "غالباً زيادة حجز المعاينات بـ 30%+ عبر السرعة.",
        "objections": ["seasonality_concern", "small_team"],
        "first_sentence": "كل lead لقاعة حفل = موسم. لا تخسرونه لتأخر الرد.",
        "best_offer": "pilot_499", "best_channel": "phone_task",
    },
    "logistics": {
        "brief": "شركة شحن/نقل سعودية تستقبل RFQ شحنات يومياً.",
        "pain": "RFQ شحن: العميل يطلب عرض، إذا تأخر الرد 10 دقائق رحل لمنافس.",
        "fit": "Dealix يرد بالعربي خلال دقيقة، يجمع الوزن + الوجهة + التاريخ، ويفتح ticket في النظام.",
        "gain": "غالباً تحسين فوز RFQ بنسبة 15-25% عبر السرعة.",
        "objections": ["complex_pricing_models", "needs_dispatcher_review"],
        "first_sentence": "RFQ شحن: 10 دقائق فرق = خسارة عقد.",
        "best_offer": "pilot_999", "best_channel": "phone_task",
    },
    "restaurant": {
        "brief": "مطعم/كافيه سعودي يستقبل استفسارات تموين + حجوزات + فرنشايز.",
        "pain": "الاستفسارات تختلط مع طلبات الطعام اليومية على واتساب.",
        "fit": "Dealix يفرز الجاد (تموين/فرنشايز) عن العادي (حجز طاولة)، ويسلم الإدارة المؤهلين فقط.",
        "gain": "غالباً 3-7 leads جادة شهرياً للتموين كانت تضيع.",
        "objections": ["small_business_budget", "concern_about_complexity"],
        "first_sentence": "تموين شركة كبيرة = إيراد شهر كامل. لا تخسروه بسبب رد متأخر.",
        "best_offer": "pilot_499", "best_channel": "phone_task",
    },
    "saas": {
        "brief": "شركة SaaS سعودية تبيع للسوق المحلي.",
        "pain": "leads inbound باللغة العربية، الفريق غالباً يرد بالإنجليزية/ترجمة آلية.",
        "fit": "Dealix هو AI sales rep بالعربي الخليجي يتكامل مع HubSpot/Salesforce/Zoho. يكمل لا يستبدل.",
        "gain": "غالباً تحسين Arabic-lead-to-demo بـ 40%+.",
        "objections": ["already_has_AI_tool", "build_vs_buy"],
        "first_sentence": "إذا تبيعون SaaS داخل السعودية، الرد العربي السريع = ميزة تنافسية.",
        "best_offer": "pilot_999", "best_channel": "linkedin_manual",
    },
    "marketing_agency": {
        "brief": "وكالة تسويق سعودية تخدم عملاء B2B/B2C.",
        "pain": "العملاء يطلبون من الوكالة \"AI sales rep بالعربي\" — الوكالة بدون حل جاهز.",
        "fit": "Dealix شريك resell — الوكالة تبيعه لعملائها وتحصل 25% MRR شهرياً.",
        "gain": "غالباً 5-15 عميل وكالة × 25% = 5K-15K ريال passive recurring شهرياً.",
        "objections": ["white_label_requirement", "control_over_messaging"],
        "first_sentence": "Dealix شريك resell — أنتم تبيعونه، نحن نبنيه، 25% MRR لكم لمدى العلاقة.",
        "best_offer": "partnership", "best_channel": "linkedin_manual",
    },
}


DEFAULT_BRIEF = {
    "brief": "شركة سعودية في قطاع B2B.",
    "pain": "غالباً تستقبل استفسارات لكن الرد قد يتأخر أو يضيع بين القنوات.",
    "fit": "Dealix يرد على inbound leads بالعربي الخليجي خلال 45 ثانية ويفرزها للمبيعات.",
    "gain": "غالباً تحسين conversion ratio على inbound — نقيس بدقة خلال 7 أيام.",
    "objections": ["unsure_fit"],
    "first_sentence": "سرعة الرد على العميل = ميزة تنافسية مباشرة.",
    "best_offer": "pilot_499", "best_channel": "phone_task",
}


def research_company_rules(account: dict[str, Any]) -> CompanyBrief:
    """Deterministic research using sector + signal heuristics. Always runs."""
    sector = (account.get("sector") or "").lower()
    company_name = account.get("company_name") or "الشركة"
    tpl = SECTOR_BRIEFS.get(sector, DEFAULT_BRIEF)

    sources: list[str] = []
    if account.get("best_source"):
        sources.append(f"directory:{account['best_source']}")
    if account.get("google_place_id"):
        sources.append(f"google_places:{account['google_place_id'][:20]}")
    if account.get("website") or account.get("domain"):
        sources.append(f"website:{account.get('domain') or account['website']}")

    risk_note = ""
    if (account.get("risk_level") or "").lower() == "high":
        risk_note = "high_risk_data — requires explicit human approval before any send"
    elif not account.get("allowed_use") or account.get("allowed_use") in {"unknown", ""}:
        risk_note = "allowed_use_missing — gate at compliance before send"
    elif not (account.get("email") or account.get("phone")):
        risk_note = "no_business_contact — phone/email needed before send"
    else:
        risk_note = "ok"

    confidence = 0.7 if sector in SECTOR_BRIEFS else 0.4

    return CompanyBrief(
        company_name=company_name,
        company_brief=tpl["brief"],
        pain_hypothesis=tpl["pain"],
        dealix_fit=tpl["fit"],
        expected_gain=tpl["gain"],
        best_offer=tpl["best_offer"],
        best_channel=tpl["best_channel"],
        best_first_sentence=tpl["first_sentence"],
        objection_risks=list(tpl["objections"]),
        risk_note=risk_note,
        confidence=confidence,
        sources_used=sources,
    )


async def research_company_with_llm(account: dict[str, Any]) -> CompanyBrief:
    """
    Runs rules first, then optional 1-call LLM polish via Groq.
    Falls back to rules if no LLM key.
    """
    base = research_company_rules(account)
    has_llm = bool(
        os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    )
    if not has_llm:
        return base
    try:
        from core.llm.router import get_router
        from core.llm.base import Message
    except Exception:
        return base

    sector_hint = (
        account.get("sector_ar") or account.get("sector") or "B2B"
    )
    city_hint = account.get("city_ar") or account.get("city") or "السعودية"
    prompt = (
        f"شركة: {account.get('company_name')}\n"
        f"القطاع: {sector_hint}\n"
        f"المدينة: {city_hint}\n"
        f"website: {account.get('website') or account.get('domain') or '(unknown)'}\n\n"
        "اكتب جملة واحدة سعودية خليجية محددة عن (الألم المتوقع) لشركة بهذا الوصف، "
        "بحيث تذكر شيئاً ملموساً عن نشاطها (موسم، نوع leads، قناة شائعة، الخ).\n"
        "ممنوع: اختراع أرقام، ادعاء حقائق غير مذكورة، وعد عوائد.\n"
        "أرجع جملة واحدة فقط بدون مقدمة."
    )
    try:
        import asyncio
        router = get_router()
        resp = await asyncio.wait_for(
            router.complete([Message(role="user", content=prompt)], max_tokens=120, temperature=0.3),
            timeout=8.0,
        )
        polished = (resp.content or "").strip().split("\n")[0]
        if 20 < len(polished) < 400:
            base.pain_hypothesis = polished
            base.confidence = min(0.95, base.confidence + 0.15)
            base.sources_used.append("llm:groq_polish")
    except Exception as exc:  # noqa: BLE001
        log.info("research_llm_polish_skipped err=%s", exc)
    return base
