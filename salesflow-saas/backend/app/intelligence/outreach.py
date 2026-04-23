"""
Outreach Brief Generator — Arabic-first
Generates personalized outreach messages for B2B, B2C, B2T motions.
Templates are rule-based with signal-driven personalization.
Plugs into LLM when OPENAI_API_KEY is set.
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class OutreachBrief:
    lead_id: str
    company_name: str
    contact_name: str
    contact_title: str
    motion: str          # sales | partnership | channel | tender

    # Arabic messages
    whatsapp_ar: str = ""
    email_subject_ar: str = ""
    email_body_ar: str = ""
    linkedin_ar: str = ""

    # English fallback
    email_subject_en: str = ""
    email_body_en: str = ""

    # Strategy
    angle: str = ""          # the specific hook being used
    pain_hypothesis: str = "" # what problem we assume they have
    value_proposition: str = ""
    call_to_action: str = ""

    # Metadata
    personalization_score: int = 0   # 0-100 how personalized this is
    generated_by: str = "template"   # template | llm


# Signal → angle mapping
SIGNAL_ANGLES = {
    "hiring": {
        "angle": "توسع الفريق",
        "hook_ar": "لاحظنا أنكم تُوسّعون فريقكم — هذا المرحلة تحتاج منظومة مبيعات قوية",
        "hook_en": "Noticed you're scaling your team — this is exactly when a strong sales OS matters",
    },
    "funding": {
        "angle": "تمويل جديد",
        "hook_ar": "تهانينا على جولة التمويل — الشركات بعد التمويل تبني محرك إيرادات سريع",
        "hook_en": "Congrats on the funding — post-investment is when you need to build your revenue engine fast",
    },
    "expansion": {
        "angle": "توسع جغرافي",
        "hook_ar": "رأينا توسعكم في السوق — دعونا نساعدكم تُحوّل هذا التوسع لعقود حقيقية",
        "hook_en": "Saw your expansion news — let us help you convert that market entry into real contracts",
    },
    "digital_transformation": {
        "angle": "تحول رقمي",
        "hook_ar": "مبادرات التحول الرقمي تحتاج محرك مبيعات ذكي يواكبها",
        "hook_en": "Digital transformation initiatives need an intelligent sales engine to match",
    },
    "ipo": {
        "angle": "استعداد للطرح العام",
        "hook_ar": "الاستعداد للطرح العام يتطلب منظومة إيرادات موثوقة وقابلة للتدقيق",
        "hook_en": "IPO readiness demands a verifiable and auditable revenue system",
    },
    "pain_point_crm": {
        "angle": "إدارة علاقات العملاء",
        "hook_ar": "إدارة العملاء بالإكسل في 2026 تُكلّف الشركة عقوداً ضائعة",
        "hook_en": "Managing clients in spreadsheets in 2026 costs you real contracts",
    },
    "pain_point_outreach": {
        "angle": "التواصل مع العملاء",
        "hook_ar": "فرق المبيعات اليوم تحتاج أدوات ذكية تُولّد ليدز وتُغلق صفقات تلقائياً",
        "hook_en": "Sales teams today need AI tools that generate leads and close deals automatically",
    },
}

# Motion-specific value propositions
MOTION_VALUE_PROPS = {
    "sales": {
        "ar": "Dealix يُحوّل فريق مبيعاتكم إلى ماكينة إيرادات ذاتية بـ 9 أنظمة تشغيل مدمجة",
        "en": "Dealix turns your sales team into a self-driving revenue machine with 9 integrated operating systems",
    },
    "partnership": {
        "ar": "Dealix يبني منظومة شراكة تُدير التحالفات والحوافز والإيرادات من مكان واحد",
        "en": "Dealix builds a partnership ecosystem that manages alliances, incentives and revenues in one place",
    },
    "channel": {
        "ar": "برنامج الشركاء في Dealix يمنح موزّعيكم أدوات المبيعات الاحترافية بدون تكلفة إضافية",
        "en": "Dealix partner program gives your resellers professional sales tools at no extra cost",
    },
    "tender": {
        "ar": "Dealix يُساعد في بناء ملف المؤهلات الكامل وتتبع الفرص الحكومية والتجارية",
        "en": "Dealix helps build full qualification packages and track government and commercial opportunities",
    },
}

CTA_BY_TIER = {
    "P1": {
        "ar": "هل لديكم 15 دقيقة هذا الأسبوع لعرض سريع؟",
        "en": "Do you have 15 minutes this week for a quick demo?",
    },
    "P2": {
        "ar": "أودّ إرسال لكم ملف موجز يوضح كيف تستفيد شركات مثلكم من Dealix",
        "en": "I'd like to send you a brief overview of how companies like yours benefit from Dealix",
    },
    "P3": {
        "ar": "سأُبقيكم على اطلاع بتحديثات Dealix — هل موافقون؟",
        "en": "I'll keep you updated on Dealix — would that be okay?",
    },
    "P4": {
        "ar": "تواصل معنا عند الجاهزية",
        "en": "Reach out when the time is right",
    },
}


def pick_angle(signals: List[str]) -> Dict:
    """Pick the best outreach angle based on available signals"""
    priority_order = ["funding", "ipo", "expansion", "hiring", "digital_transformation",
                      "pain_point_crm", "pain_point_outreach"]
    for sig in priority_order:
        if sig in signals:
            return SIGNAL_ANGLES[sig]
    return {
        "angle": "تطوير الأعمال",
        "hook_ar": "نساعد الشركات الرائدة في السعودية على بناء محرك إيرادات ذكي",
        "hook_en": "We help leading Saudi companies build an intelligent revenue engine",
    }


def build_whatsapp_message(
    company: str, contact: str, angle_data: Dict, motion: str, tier: str
) -> str:
    """Build a short WhatsApp-optimized Arabic message"""
    hook = angle_data.get("hook_ar", "")
    vp = MOTION_VALUE_PROPS.get(motion, MOTION_VALUE_PROPS["sales"])["ar"]
    cta = CTA_BY_TIER.get(tier, CTA_BY_TIER["P3"])["ar"]

    contact_greeting = f"مرحباً {contact}" if contact else f"مرحباً فريق {company}"

    return f"""{contact_greeting}،

{hook}.

{vp}.

{cta}

— فريق Dealix"""


def build_email(
    company: str, contact: str, title: str,
    angle_data: Dict, motion: str, tier: str,
    signals: List[str]
) -> Dict[str, str]:
    """Build email subject and body in Arabic + English"""
    hook_ar = angle_data.get("hook_ar", "")
    hook_en = angle_data.get("hook_en", "")
    vp_ar = MOTION_VALUE_PROPS.get(motion, MOTION_VALUE_PROPS["sales"])["ar"]
    vp_en = MOTION_VALUE_PROPS.get(motion, MOTION_VALUE_PROPS["sales"])["en"]
    cta_ar = CTA_BY_TIER.get(tier, CTA_BY_TIER["P3"])["ar"]
    cta_en = CTA_BY_TIER.get(tier, CTA_BY_TIER["P3"])["en"]

    contact_ar = f"{contact}" if contact else f"فريق {company}"
    title_mention_ar = f" | {title}" if title else ""
    title_mention_en = f", {title}" if title else ""

    subject_ar = f"Dealix × {company} — {angle_data.get('angle', 'فرصة تعاون')}"
    subject_en = f"Dealix × {company} — {angle_data.get('angle', 'Partnership Opportunity')}"

    body_ar = f"""مرحباً {contact_ar}{title_mention_ar}،

{hook_ar}.

{vp_ar}.

نحن نعمل مع شركات في قطاعكم ونرى نتائج واضحة:
• زيادة في معدل إغلاق الصفقات
• تقليل وقت دورة المبيعات
• رؤية كاملة للـ pipeline التنفيذي

{cta_ar}

مع التقدير،
فريق Dealix
https://dealix.ai"""

    body_en = f"""Hi {contact or 'there'}{title_mention_en},

{hook_en}.

{vp_en}.

We work with companies in your sector and see clear results:
• Higher deal close rates
• Shorter sales cycle time
• Full executive pipeline visibility

{cta_en}

Best regards,
The Dealix Team
https://dealix.ai"""

    return {
        "subject_ar": subject_ar,
        "body_ar": body_ar,
        "subject_en": subject_en,
        "body_en": body_en,
    }


def build_linkedin_message(
    company: str, contact: str, angle_data: Dict, motion: str
) -> str:
    """LinkedIn connection message — short and professional (300 chars)"""
    hook = angle_data.get("hook_ar", "نساعد الشركات على بناء محرك إيرادات ذكي")
    return f"مرحباً {contact or 'colleague'}، {hook}. نعمل مع شركات مثل {company} لبناء منظومة مبيعات ذكية. أودّ التواصل معكم."[:300]


def generate_outreach_brief(
    lead_dict: Dict,
    score_dict: Dict,
    motion: str = "sales"
) -> OutreachBrief:
    """
    Generate a full outreach brief for a scored lead.
    lead_dict: from EnrichedLead.to_dict()
    score_dict: from score_lead()
    """
    company = lead_dict.get("company_name", "")
    contact = lead_dict.get("contact_name", "")
    title = lead_dict.get("contact_title", "")
    signals = lead_dict.get("signals", [])
    tier = score_dict.get("tier", "P3")

    angle_data = pick_angle(signals)
    email_data = build_email(company, contact, title, angle_data, motion, tier, signals)

    personalization = 30
    if signals: personalization += 30
    if contact: personalization += 20
    if title: personalization += 10
    if lead_dict.get("recent_news"): personalization += 10

    brief = OutreachBrief(
        lead_id=lead_dict.get("id", ""),
        company_name=company,
        contact_name=contact,
        contact_title=title,
        motion=motion,
        whatsapp_ar=build_whatsapp_message(company, contact, angle_data, motion, tier),
        email_subject_ar=email_data["subject_ar"],
        email_body_ar=email_data["body_ar"],
        email_subject_en=email_data["subject_en"],
        email_body_en=email_data["body_en"],
        linkedin_ar=build_linkedin_message(company, contact, angle_data, motion),
        angle=angle_data.get("angle", ""),
        pain_hypothesis=angle_data.get("hook_ar", ""),
        value_proposition=MOTION_VALUE_PROPS.get(motion, MOTION_VALUE_PROPS["sales"])["ar"],
        call_to_action=CTA_BY_TIER.get(tier, CTA_BY_TIER["P3"])["ar"],
        personalization_score=min(100, personalization),
        generated_by="template",
    )
    return brief


def generate_batch_briefs(
    scored_leads: List[Dict], motion: str = "sales"
) -> List[Dict]:
    """Generate outreach briefs for a list of scored leads (P1+P2 only by default)"""
    briefs = []
    for item in scored_leads:
        tier = item.get("score", {}).get("tier", "P4")
        if tier in ("P1", "P2"):  # Only generate for actionable leads
            brief = generate_outreach_brief(item["lead"], item["score"], motion)
            briefs.append({
                "company": brief.company_name,
                "tier": tier,
                "angle": brief.angle,
                "whatsapp_ar": brief.whatsapp_ar,
                "email_subject_ar": brief.email_subject_ar,
                "email_body_ar": brief.email_body_ar,
                "linkedin_ar": brief.linkedin_ar,
                "personalization_score": brief.personalization_score,
            })
    return briefs
