"""
Rules Router — deterministic, zero-LLM lead classification + scoring + messaging.

Works fully without any LLM API key. Uses explicit rules over:
- sector keywords
- signals (from tech_detect output OR manual)
- company hints (name/URL/country)

Produces:
- opportunity_type (9 types)
- fit_score / intent_score / access_score / revenue_score (100-pt model)
- priority_tier (P0/P1/P2/BACKLOG)
- risk_level (LOW/MEDIUM/HIGH/BLOCKED)
- recommended_channel
- next_action
- first_message_angle
- compliance_note

This is the "graceful degraded mode" backbone. When LLM becomes available, it
can layer on top of this — but the rules alone are production-usable today.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

# ── Keyword taxonomies (lowercased substring match) ───────────

AGENCY_KEYWORDS = {
    "agency", "digital marketing", "performance marketing", "media agency",
    "creative", "branding", "pr agency", "paid ads", "content agency",
    "وكالة", "تسويق", "إعلام", "إبداع",
}
IMPL_PARTNER_KEYWORDS = {
    "crm consultant", "hubspot partner", "salesforce partner", "revops",
    "implementation partner", "automation consultant", "zapier expert",
    "make expert", "integration services",
}
STRATEGIC_KEYWORDS = {
    "platform", "marketplace", "ecosystem", "payment gateway", "crm vendor",
    "accelerator", "incubator", "manso'ah", "misk", "kaust",
    "accounting saas", "wafeq", "qoyod", "dafater",
    "tap payments", "moyasar", "paytabs", "hyperpay", "stc pay",
    "salla", "zid", "shopify", "foodics",
}
INVESTOR_KEYWORDS = {
    "investor", "venture", "capital", "vc", "angel", "fund",
    "sanabil", "stv", "wamda", "raed", "500 startups", "gate ventures",
    "arzan", "vision ventures", "investment",
}
CONTENT_KEYWORDS = {
    "podcast", "newsletter", "community", "creator", "writer", "influencer",
    "content platform", "thought leader", "founder community",
    "مجتمع", "بودكاست", "نشرة",
}
SUPPLIER_KEYWORDS = {
    "supplier", "vendor", "tool", "integration partner",
}
B2C_KEYWORDS = {
    "delivery", "retail", "consumer", "b2c", "ecommerce",
    "food delivery", "grocery", "fashion",
}
DIRECT_CUSTOMER_SECTORS = {
    "saas", "fintech", "proptech", "contech", "edtech", "healthtech",
    "logistics", "marketplace", "b2b marketplace",
    "hr tech", "hr saas", "cxm", "restaurant", "ecom platform",
}

# ── Intent signal names (match against detected signals) ──────
INTENT_SIGNALS = {
    "uses booking tool": 5,
    "CRM in use": 6,
    "marketing automation": 4,
    "payment gateway": 3,
    "MENA payment gateway": 5,
    "e-commerce platform": 4,
    "Salla/Zid merchant": 8,
    "live chat": 3,
    "WhatsApp widget": 8,
    "analytics active": 3,
    "running paid ads": 6,
    "inbound form": 5,
    "CMS": 1,
    "framework": 1,
}

FIT_ANCHORS = {
    "saas": 10, "fintech": 9, "proptech": 8, "contech": 8,
    "restaurant": 8, "ecom": 8, "marketplace": 9,
    "cxm": 9, "hr tech": 7, "hr saas": 8, "logistics": 7,
    "edtech": 6, "healthtech": 5, "agency": 8,
    "retail": 5, "telecom": 4,
}

CHANNELS_BY_TYPE = {
    "DIRECT_CUSTOMER":        "LINKEDIN_MANUAL",
    "AGENCY_PARTNER":         "LINKEDIN_MANUAL",
    "IMPLEMENTATION_PARTNER": "LINKEDIN_MANUAL",
    "REFERRAL_PARTNER":       "LINKEDIN_MANUAL",
    "STRATEGIC_PARTNER":      "PARTNER_INTRO",
    "CONTENT_COLLABORATION":  "LINKEDIN_MANUAL",
    "INVESTOR_OR_ADVISOR":    "EMAIL",
    "SUPPLIER_OR_INTEGRATION":"EMAIL",
    "B2C_AUDIENCE":           "CONTENT_MENTION",
}

NEXT_ACTION_BY_TYPE = {
    "DIRECT_CUSTOMER":        "PREPARE_DM",
    "AGENCY_PARTNER":         "PREPARE_PARTNER_PITCH",
    "IMPLEMENTATION_PARTNER": "PREPARE_PARTNER_PITCH",
    "REFERRAL_PARTNER":       "PREPARE_PARTNER_PITCH",
    "STRATEGIC_PARTNER":      "PREPARE_PARTNER_PITCH",
    "CONTENT_COLLABORATION":  "PREPARE_DM",
    "INVESTOR_OR_ADVISOR":    "PREPARE_INVESTOR_NOTE",
    "SUPPLIER_OR_INTEGRATION":"RESEARCH_MORE",
    "B2C_AUDIENCE":           "RESEARCH_MORE",
}

MESSAGE_ANGLES = {
    "DIRECT_CUSTOMER": (
        "AI sales rep بالعربي يرد على leads خلال 45 ثانية، يؤهّل، ويحجز demo — "
        "يركب فوق CRM الحالي ويسلّم sequence جاهزة للـ SDR."
    ),
    "AGENCY_PARTNER": (
        "للوكالات: setup 3-15K + 20-30% من MRR كل عميل دائم. "
        "3-5 عملاء = revenue stream جديد بدون tech build."
    ),
    "IMPLEMENTATION_PARTNER": (
        "شريك تنفيذ: Dealix يوفر الطبقة، أنت تقدم setup + retainer لعملائك."
    ),
    "REFERRAL_PARTNER": (
        "referral 10% من MRR لـ 12 شهر على كل عميل يجي عبرك — صفر setup."
    ),
    "STRATEGIC_PARTNER": (
        "Dealix + منتجك = offering مكمّل لعملائكم. add-on أو bundle — نناقش النسب."
    ),
    "CONTENT_COLLABORATION": (
        "محتوى سعودي حول AI sales + GTM — تعاون podcast/newsletter/سلسلة."
    ),
    "INVESTOR_OR_ADVISOR": (
        "Dealix = Arabic-first AI sales operator. نبحث عن portfolio introductions + advisory."
    ),
    "SUPPLIER_OR_INTEGRATION": (
        "integration أو supply مقترح — نناقش التفاصيل."
    ),
    "B2C_AUDIENCE": (
        "جمهور B2C — تفعيل عبر content + paid عبر الوكالات/الشركاء."
    ),
}

COMPLIANCE_NOTES = {
    "LOW":    "Public business contact only; no personal PII used.",
    "MEDIUM": "Public business contact from public source; single personalized manual DM/email; no bots.",
    "HIGH":   "Personal PII path — requires explicit human approval before outreach.",
    "BLOCKED":"Source or channel disallowed; do not contact without legal review.",
}


@dataclass
class RouteResult:
    opportunity_type: str
    fit_score: int
    intent_score: int
    access_score: int
    revenue_score: int
    priority_score: int
    priority_tier: str
    risk_level: str
    recommended_channel: str
    next_action: str
    first_message_angle: str
    human_approval_required: bool
    compliance_note: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _contains_any(text: str, bag: set[str]) -> bool:
    t = (text or "").lower()
    return any(k in t for k in bag)


def _classify_opportunity(*, sector: str, company: str, tags: str) -> str:
    combined = " ".join([sector or "", company or "", tags or ""]).lower()

    if _contains_any(combined, AGENCY_KEYWORDS):
        return "AGENCY_PARTNER"
    if _contains_any(combined, IMPL_PARTNER_KEYWORDS):
        return "IMPLEMENTATION_PARTNER"
    if _contains_any(combined, INVESTOR_KEYWORDS):
        return "INVESTOR_OR_ADVISOR"
    if _contains_any(combined, CONTENT_KEYWORDS):
        return "CONTENT_COLLABORATION"
    if _contains_any(combined, STRATEGIC_KEYWORDS):
        # Only flag strategic if it's a platform/ecosystem — not e.g. a customer using salla
        if any(k in combined for k in ("platform", "ecosystem", "marketplace", "vendor", "accelerator", "partner", "accounting saas")):
            return "STRATEGIC_PARTNER"
    if _contains_any(combined, SUPPLIER_KEYWORDS):
        return "SUPPLIER_OR_INTEGRATION"
    if _contains_any(combined, B2C_KEYWORDS):
        # Only B2C_AUDIENCE if consumer-final, not b2b-ecom platform
        if "b2c" in combined or "consumer" in combined:
            return "B2C_AUDIENCE"

    # Default — direct customer
    return "DIRECT_CUSTOMER"


def _score(
    *,
    opportunity_type: str,
    sector: str,
    signals: list[dict],
    country: str,
    has_decision_maker: bool,
    size_hint: str,
) -> tuple[int, int, int, int]:
    """Returns (fit, intent, access, revenue) — each capped at max."""
    s_text = (sector or "").lower()
    fit = 0
    for anchor, pts in FIT_ANCHORS.items():
        if anchor in s_text:
            fit = max(fit, pts)

    # Saudi / GCC market bump
    if country and country.upper() in {"SA", "KSA", "AE-SA", "SA-GCC"}:
        fit += 5
    elif country and country.upper() in {"AE", "KW", "QA", "BH", "OM"}:
        fit += 2

    # Size fit (sweet spot 20-500)
    size_bump = 5 if size_hint in {"10-50", "50-200", "200-1000"} else 2
    fit += size_bump

    # Lead flow + sales workflow — credit if signals include forms/CRM/booking
    sig_names = [s.get("name", "").lower() for s in (signals or [])]
    sig_evid = [s.get("evidence", "").lower() for s in (signals or [])]
    sig_all = " ".join(sig_names + sig_evid)
    if "form" in sig_all or "inbound form" in sig_all:
        fit += 5
    if "crm" in sig_all:
        fit += 5
    if "booking" in sig_all:
        fit += 5
    fit = min(fit, 40)

    # Intent
    intent = 0
    for sig in (signals or []):
        name = sig.get("name", "")
        w = sig.get("weight", 0)
        # Look up known intent signal weights
        for k, default in INTENT_SIGNALS.items():
            if k.lower() in name.lower():
                intent += min(w or default, default)
                break
    intent = min(intent, 30)

    # Access
    access = 5 if has_decision_maker else 3
    if opportunity_type in {"DIRECT_CUSTOMER", "AGENCY_PARTNER"}:
        access += 5  # public LinkedIn path
    else:
        access += 3
    # personalization angle — any non-trivial signal counts
    access += 5 if len(signals or []) >= 2 else (3 if signals else 2)
    access = min(access, 15)

    # Revenue
    revenue = 5  # pilot affordable for anyone w/ real business
    if opportunity_type in {"AGENCY_PARTNER", "STRATEGIC_PARTNER", "REFERRAL_PARTNER"}:
        revenue += 7  # partner distribution multiplies
    elif opportunity_type == "DIRECT_CUSTOMER":
        revenue += 7  # retainer potential
    else:
        revenue += 3
    revenue += 3  # default partner expansion credit
    revenue = min(revenue, 15)

    return fit, intent, access, revenue


def _tier(priority_score: int) -> str:
    if priority_score >= 80:
        return "P0"
    if priority_score >= 65:
        return "P1"
    if priority_score >= 45:
        return "P2"
    return "BACKLOG"


def _risk(
    *,
    opportunity_type: str,
    has_decision_maker: bool,
    contact_channel: str,
    is_government: bool,
) -> str:
    if is_government:
        return "HIGH"
    if contact_channel.upper() in {"PHONE", "WHATSAPP_UNKNOWN"}:
        return "HIGH"
    if opportunity_type in {"DIRECT_CUSTOMER", "AGENCY_PARTNER", "REFERRAL_PARTNER"}:
        return "LOW" if has_decision_maker else "MEDIUM"
    if opportunity_type == "INVESTOR_OR_ADVISOR":
        return "MEDIUM"
    return "LOW"


def route_account(
    *,
    company: str,
    sector: str = "",
    country: str = "",
    domain: str = "",
    signals: list[dict] | None = None,
    tags: str = "",
    decision_maker: str | None = None,
    size_hint: str = "",
    is_government: bool = False,
    desired_goal: str | None = None,
) -> RouteResult:
    """
    Classify + score + route — deterministic, no LLM required.
    Returns a RouteResult ready for the Lead Output Schema.
    """
    signals = signals or []

    opportunity_type = _classify_opportunity(
        sector=sector, company=company, tags=tags
    )
    # If explicit hint provided by caller, prefer it
    if desired_goal:
        hint = desired_goal.upper().replace("-", "_").replace(" ", "_")
        if hint in set(CHANNELS_BY_TYPE.keys()):
            opportunity_type = hint

    has_dm = bool(decision_maker and decision_maker.strip())
    fit, intent, access, revenue = _score(
        opportunity_type=opportunity_type,
        sector=sector,
        signals=signals,
        country=country,
        has_decision_maker=has_dm,
        size_hint=size_hint,
    )
    priority_score = fit + intent + access + revenue
    tier = _tier(priority_score)
    channel = CHANNELS_BY_TYPE.get(opportunity_type, "LINKEDIN_MANUAL")
    risk = _risk(
        opportunity_type=opportunity_type,
        has_decision_maker=has_dm,
        contact_channel=channel,
        is_government=is_government,
    )
    human_approval = risk in {"HIGH", "BLOCKED"}
    if human_approval:
        channel = "HOLD_FOR_APPROVAL"

    reason_parts = []
    if country:
        reason_parts.append(f"market={country}")
    if sector:
        reason_parts.append(f"sector={sector}")
    if signals:
        reason_parts.append(f"signals={len(signals)}")
    if has_dm:
        reason_parts.append("DM known")
    reason = " · ".join(reason_parts) or "baseline classification"

    return RouteResult(
        opportunity_type=opportunity_type,
        fit_score=fit,
        intent_score=intent,
        access_score=access,
        revenue_score=revenue,
        priority_score=priority_score,
        priority_tier=tier,
        risk_level=risk,
        recommended_channel=channel,
        next_action=NEXT_ACTION_BY_TYPE.get(opportunity_type, "RESEARCH_MORE"),
        first_message_angle=MESSAGE_ANGLES.get(opportunity_type, ""),
        human_approval_required=human_approval,
        compliance_note=COMPLIANCE_NOTES[risk],
        reason=reason,
    )


# ── Message generator ──────────────────────────────────────────

def _primary_signal(signals: list[dict]) -> dict | None:
    if not signals:
        return None
    return max(signals, key=lambda s: s.get("weight", 0))


def generate_messages(
    *,
    company: str,
    decision_maker: str | None,
    opportunity_type: str,
    signals: list[dict] | None = None,
    calendly_url: str = "https://calendly.com/sami-assiri11/dealix-demo",
    partners_url: str = "https://dealix.me/partners.html",
) -> dict[str, str]:
    """Return LinkedIn DM + email + WhatsApp (warm only) + 3 follow-ups."""
    name = decision_maker or f"فريق {company}"
    sig = _primary_signal(signals or [])
    sig_evid = sig.get("evidence", "") if sig else ""
    sig_name = sig.get("name", "") if sig else ""

    def linkedin_direct() -> str:
        hook = ""
        if "WhatsApp" in sig_evid:
            hook = f"لاحظت إن {company} تستخدم WhatsApp كقناة مبيعات رئيسية — Dealix يضاعف الاستجابة بردود عربية خلال 45 ثانية، يؤهّل، ويحجز demo قبل ما يبرد."
        elif "CRM" in sig_name:
            hook = f"لاحظت إن {company} تستخدم {sig_evid} — Dealix يركب فوقه: يرد بالعربي، يؤهّل BANT، ويسلّم سجل جاهز داخل نفس الـ CRM."
        elif "booking" in sig_name:
            hook = f"لاحظت {sig_evid} عند {company} — Dealix يسبقه: يرد، يؤهّل، ويحجز slot في نفس الأداة."
        elif "paid ads" in sig_name or "ads" in sig_name:
            hook = f"{company} تدير حملات مدفوعة. المشكلة الشائعة بعد click: lead يدخل funnel، الرد بطيء، CPA يرتفع. Dealix يرد بالعربي خلال 45 ثانية."
        elif "Salla" in sig_evid or "Zid" in sig_evid or "ecom_mena" in sig_name:
            hook = f"{company} على منصة {sig_evid} — Dealix يرد على استفسارات المتجر بالعربي، يؤكد الطلب، ويسلّم للـ agent فقط عند negotiation."
        else:
            hook = f"Dealix = AI sales rep بالعربي يرد على leads خلال 45 ثانية، يؤهّل، ويحجز demo — فوق CRM الحالي."
        return (
            f"{name} مرحباً،\n\n{hook}\n\n"
            f"20 دقيقة demo نشوف مناسبته لـ {company}؟\n"
            f"📅 {calendly_url}\n\n"
            f"سامي — Dealix"
        )

    def linkedin_partner() -> str:
        return (
            f"{name} السلام عليكم،\n\n"
            f"{company} تقدّم خدمات تسويق/CRM/automation لعملاء B2B. Dealix يضاعف قيمة خدمتك:\n"
            f"- AI sales rep بالعربي فوق عملاء {company}\n"
            f"- setup 3-15K ريال + 20-30% من MRR كل عميل دائم\n"
            f"- 3-5 عملاء = 1,500-3,750 ريال شهري إضافي بدون tech build\n\n"
            f"20 دقيقة partner meeting هذا الأسبوع؟\n"
            f"🤝 {partners_url}\n📅 {calendly_url}\n\nسامي"
        )

    def linkedin_strategic() -> str:
        return (
            f"{name} مرحباً،\n\n"
            f"Dealix = Arabic-first AI sales ops layer. {company} منصة / ecosystem مكمّل لذلك.\n"
            f"اقتراح شراكة استراتيجية: بحث add-on داخل منصتكم أو bundle مشترك.\n"
            f"20 دقيقة نستكشف الفكرة؟\n📅 {calendly_url}\n\nسامي"
        )

    def linkedin_investor() -> str:
        return (
            f"{name} السلام عليكم،\n\n"
            f"Dealix = Arabic-first AI sales operator للسوق السعودي. "
            f"نبحث عن advisor/investor familiar with B2B SaaS + MENA GTM. "
            f"15 دقيقة مكالمة نستكشف fit + possible portfolio introductions؟\n"
            f"📅 {calendly_url}\n\nسامي"
        )

    def email_variant(base_linkedin: str) -> str:
        return (
            base_linkedin
            + "\n\n---\n"
            "لإيقاف هذه الرسائل، رد بكلمة: لا شكراً. نحترم رغبتك فوراً."
        )

    def whatsapp_warm() -> str:
        return (
            f"السلام عليكم،\n"
            f"سامي من Dealix. AI sales rep بالعربي — يرد، يؤهّل، يحجز demo.\n"
            f"مناسب نتكلم 10 دقائق؟"
        )

    picker = {
        "DIRECT_CUSTOMER":        linkedin_direct,
        "AGENCY_PARTNER":         linkedin_partner,
        "IMPLEMENTATION_PARTNER": linkedin_partner,
        "REFERRAL_PARTNER":       linkedin_partner,
        "STRATEGIC_PARTNER":      linkedin_strategic,
        "CONTENT_COLLABORATION":  linkedin_direct,
        "INVESTOR_OR_ADVISOR":    linkedin_investor,
        "SUPPLIER_OR_INTEGRATION":linkedin_direct,
        "B2C_AUDIENCE":           linkedin_direct,
    }
    base = picker.get(opportunity_type, linkedin_direct)()

    return {
        "linkedin": base,
        "email": email_variant(base),
        "whatsapp_warm_only": whatsapp_warm(),
        "follow_up_plus_2": (
            f"{name} تذكير سريع للرسالة السابقة — هل فرصة لـ 15 دقيقة demo هذا الأسبوع؟\n📅 {calendly_url}"
        ),
        "follow_up_plus_5": (
            f"{name} مرحباً — شاركت لك case study قصير عن شركة سعودية حصلت نتائج في 7 أيام. "
            f"أرسله؟ [أو فقط قل: اهتمام/لاحقاً/لا]"
        ),
        "follow_up_plus_10": (
            f"{name} آخر متابعة — لو ما هو الوقت المناسب حالياً، تمام.\n"
            f"سؤال أخير: هل تعرف شركة ثانية في السعودية قد تستفيد؟ "
            f"referral 10% من MRR لـ 12 شهر."
        ),
    }
