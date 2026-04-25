"""Daily Targeting Automation — generates personalized outreach queue.

Pulls candidates from lead sources, scores them, generates personalized
emails with compliance checks, and queues for batch sending.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("dealix.automation")

router = APIRouter(prefix="/automation", tags=["Automation"])

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "mail.com", "protonmail.com", "yandex.com",
    "aol.com", "live.com", "msn.com",
}

SECTOR_PAIN_MAP = {
    "real_estate": {
        "pain_ar": "استفسارات كثيرة عن الأسعار والمواقع والمساحات تضيع بسبب تأخر الرد",
        "angle_ar": "ديلكس يرد خلال 45 ثانية، يسأل عن الميزانية والموقع المفضل، ويحجز معاينة",
        "roi_ar": "لو عندكم 30-100 استفسار/شهر، الرد السريع يحفظ 5-15 فرصة كانت بتبرد",
    },
    "construction": {
        "pain_ar": "طلبات عروض أسعار متكررة تحتاج فرز سريع قبل تحويلها للمهندسين",
        "angle_ar": "ديلكس يستقبل الطلب، يسأل عن نوع المشروع والميزانية، ويصنّف الجدية",
        "roi_ar": "تقليل وقت الفرز من ساعات إلى دقائق لكل طلب عرض سعر",
    },
    "hospitality": {
        "pain_ar": "حجوزات قاعات ومناسبات واستفسارات أسعار تحتاج رد سريع قبل ما العميل يروح للمنافس",
        "angle_ar": "ديلكس يرد فوراً، يسأل عن التاريخ وعدد الضيوف والميزانية، ويحجز مبدئي",
        "roi_ar": "كل ساعة تأخير في الرد = احتمال 50% يحجز عند غيركم",
    },
    "food_beverage": {
        "pain_ar": "طلبات تموين وحفلات B2B تجي على واتساب وتضيع بين الرسائل",
        "angle_ar": "ديلكس يستقبل طلب التموين، يسأل عن العدد والتاريخ والميزانية، ويحوّل للمبيعات",
        "roi_ar": "طلبات B2B عادة أعلى قيمة — حفظها يرفع الإيراد بنسبة ملحوظة",
    },
    "logistics": {
        "pain_ar": "طلبات أسعار شحن متكررة تحتاج رد سريع ومعلومات دقيقة",
        "angle_ar": "ديلكس يسأل عن نوع الشحنة والوجهة والحجم ويعطي تقدير أولي",
        "roi_ar": "كل طلب شحن ما يُتابع = إيراد ضائع مباشر",
    },
    "agency": {
        "pain_ar": "عملاء الوكالة يجيبون leads بالإعلانات لكن المتابعة ضعيفة",
        "angle_ar": "ديلكس يصير خدمة جديدة تبيعونها لعملائكم: رد + تأهيل + حجز",
        "roi_ar": "كل عميل وكالة = setup fee + 20-30% MRR شهري متكرر",
    },
    "saas": {
        "pain_ar": "leads تجي من الموقع والإعلانات وتبرد لأن فريق المبيعات صغير",
        "angle_ar": "ديلكس يرد بالعربي خلال 45 ثانية، يؤهل، ويحجز demo تلقائياً",
        "roi_ar": "شركات SaaS تخسر 30% من leads بسبب تأخر الرد — ديلكس يقلّص هذا",
    },
    "healthcare": {
        "pain_ar": "مرضى يتصلون ويسألون عن المواعيد والأسعار — الموظفين مشغولين",
        "angle_ar": "ديلكس يرد على الأسئلة المتكررة ويحجز الموعد مباشرة",
        "roi_ar": "تقليل الضغط على الاستقبال وزيادة نسبة الحجوزات المؤكدة",
    },
    "education": {
        "pain_ar": "استفسارات تسجيل ورسوم متكررة تأخذ وقت الإدارة",
        "angle_ar": "ديلكس يجاوب على الأسئلة الشائعة ويجمع بيانات المهتمين",
        "roi_ar": "تحويل الاستفسارات لتسجيلات فعلية بدل ما تضيع",
    },
}


class TargetingRequest(BaseModel):
    sectors: List[str] = ["real_estate", "construction", "hospitality", "logistics", "agency"]
    cities: List[str] = ["الرياض", "جدة", "الدمام"]
    daily_target_count: int = 50
    batch_size: int = 10
    approval_required: bool = True


class ComplianceCheckRequest(BaseModel):
    email: str
    company: str = ""
    source: str = ""
    opt_out: bool = False
    bounced_before: bool = False
    risk_score: int = 0


class EmailGenerateRequest(BaseModel):
    company: str
    sector: str
    city: str = ""
    contact_name: str = ""
    pain_hypothesis: str = ""
    website: str = ""
    signals: List[str] = []


def _is_personal_email(email: str) -> bool:
    if not email or "@" not in email:
        return True
    domain = email.split("@")[1].lower()
    return domain in FREE_EMAIL_DOMAINS


def _compliance_check(req: ComplianceCheckRequest) -> Dict[str, Any]:
    if req.opt_out:
        return {"allowed": False, "reason": "opt_out", "action": "suppress"}
    if req.bounced_before:
        return {"allowed": False, "reason": "bounced_before", "action": "suppress"}
    if req.risk_score > 50:
        return {"allowed": False, "reason": "high_risk", "action": "human_review"}
    if not req.email or "@" not in req.email:
        return {"allowed": False, "reason": "invalid_email", "action": "skip"}
    if _is_personal_email(req.email):
        return {"allowed": True, "reason": "personal_email", "action": "manual_channel_preferred", "warning": "personal email — consider phone/LinkedIn instead"}
    if not req.source:
        return {"allowed": False, "reason": "no_source", "action": "add_source_first"}
    return {"allowed": True, "reason": "compliant", "action": "send"}


def _generate_email(req: EmailGenerateRequest) -> Dict[str, Any]:
    sector_info = SECTOR_PAIN_MAP.get(req.sector, SECTOR_PAIN_MAP.get("saas", {}))
    pain = req.pain_hypothesis or sector_info.get("pain_ar", "تأخر الرد على العملاء المحتملين")
    angle = sector_info.get("angle_ar", "ديلكس يرد بالعربي خلال 45 ثانية ويؤهل العميل")
    roi = sector_info.get("roi_ar", "الرد السريع يحفظ فرص كانت بتضيع")

    name_greeting = f"فريق {req.company}" if not req.contact_name else req.contact_name
    city_mention = f" في {req.city}" if req.city else ""

    signal_line = ""
    if "hubspot" in [s.lower() for s in req.signals]:
        signal_line = f"لاحظت إن {req.company} تستخدمون HubSpot — "
    elif "whatsapp_widget" in [s.lower() for s in req.signals]:
        signal_line = f"شفت إن عندكم واتساب كقناة للعملاء — "

    subject = f"تجربة تأهيل عملاء لـ {req.company}"

    body = f"""السلام عليكم {name_greeting}،

{signal_line}{pain}{city_mention}.

أنا سامي من Dealix. {angle}.

{roi}.

نقدم تجربة 7 أيام على 10–25 lead مع تقرير يومي.
سعر الإطلاق لأول عملاء: 499 ريال.

يناسبك أرسل لك مثال مبني على نشاطكم؟

إذا ما يناسبكم، اكتبوا "إيقاف" ولن أتواصل مرة ثانية.

سامي العسيري
Dealix — مندوب مبيعات ذكي بالعربي
dealix.me"""

    followup_2 = f"""السلام عليكم {name_greeting}،

أرسلت لكم رسالة قبل يومين عن Dealix.

باختصار: نجرب 7 أيام على leads عندكم — رد سريع + تأهيل + تقرير يومي.

يناسبك 10 دقائق هذا الأسبوع؟
calendly.com/sami-assiri11/dealix-demo

إذا ما يناسبكم، اكتبوا "إيقاف".

سامي — Dealix"""

    followup_5 = f"""السلام عليكم {name_greeting}،

آخر رسالة — أبي أتأكد إنها وصلتكم.

Dealix يساعد شركات {req.sector} ترد على الاستفسارات بسرعة وتحول الجاد منها للمبيعات.

لو مناسب نتكلم، أنا متاح. لو لا، شكرًا على وقتكم ولن أتواصل مرة ثانية.

سامي — Dealix"""

    call_script = f"""مرحبا، أنا سامي من Dealix.

أتصل لأن شركات في قطاع {req.sector} عادةً تستقبل استفسارات كثيرة وتضيع بعضها بسبب تأخر الرد.

Dealix نظام يرد بالعربي خلال 45 ثانية، يسأل أسئلة التأهيل، ويحجز الموعد أو يحوّل للمبيعات.

عندنا تجربة 7 أيام بـ 499 ريال.

هل يناسبكم أرسل تفاصيل؟"""

    linkedin_msg = f"""{name_greeting} مرحباً،

Dealix = AI sales rep بالعربي يرد على leads خلال 45 ثانية، يؤهّل، ويحجز demo.

20 دقيقة demo نشوف مناسبته لـ {req.company}؟
calendly.com/sami-assiri11/dealix-demo

سامي — Dealix"""

    return {
        "company": req.company,
        "sector": req.sector,
        "subject_ar": subject,
        "body_ar": body,
        "followup_day_2": followup_2,
        "followup_day_5": followup_5,
        "call_script_ar": call_script,
        "linkedin_manual_message": linkedin_msg,
        "opt_out_included": True,
        "word_count": len(body.split()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/compliance/check")
async def check_compliance(req: ComplianceCheckRequest) -> Dict[str, Any]:
    return _compliance_check(req)


@router.post("/email/generate")
async def generate_email(req: EmailGenerateRequest) -> Dict[str, Any]:
    return _generate_email(req)


@router.post("/daily-targeting/generate")
async def generate_daily_targets(req: TargetingRequest) -> Dict[str, Any]:
    targets = []
    for i, sector in enumerate(req.sectors):
        sector_info = SECTOR_PAIN_MAP.get(sector, {})
        for j, city in enumerate(req.cities[:3]):
            idx = i * 3 + j
            if idx >= req.daily_target_count:
                break
            target = {
                "id": str(uuid4())[:8],
                "company": f"[{sector}_{city}_{j+1}]",
                "sector": sector,
                "city": city,
                "pain_hypothesis": sector_info.get("pain_ar", ""),
                "angle": sector_info.get("angle_ar", ""),
                "roi_estimate": sector_info.get("roi_ar", ""),
                "priority": "P0" if sector in ("real_estate", "construction", "agency") else "P1",
                "channel": "email",
                "approval_required": req.approval_required,
                "status": "ready",
            }
            targets.append(target)

    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_generated": len(targets),
        "sectors": req.sectors,
        "cities": req.cities,
        "batch_size": req.batch_size,
        "approval_required": req.approval_required,
        "targets": targets[:req.daily_target_count],
    }


REPLY_CATEGORIES = {
    "interested": {"next": "propose_demo", "auto_reply": True},
    "ask_price": {"next": "explain_pilot_499", "auto_reply": True},
    "ask_details": {"next": "send_brief_explanation", "auto_reply": True},
    "ask_demo": {"next": "send_calendly", "auto_reply": True},
    "not_now": {"next": "schedule_followup_30d", "auto_reply": True},
    "unsubscribe": {"next": "opt_out_suppress", "auto_reply": False},
    "objection_budget": {"next": "explain_roi_pilot", "auto_reply": True},
    "objection_ai": {"next": "explain_manual_first", "auto_reply": True},
    "objection_privacy": {"next": "human_review", "auto_reply": False},
    "already_has_crm": {"next": "position_as_layer", "auto_reply": True},
    "partnership": {"next": "route_partner_flow", "auto_reply": False},
    "angry": {"next": "apologize_opt_out", "auto_reply": False},
}

REPLY_RESPONSES = {
    "interested": "ممتاز! يناسبك نحجز 20 دقيقة هذا الأسبوع؟\ncalendly.com/sami-assiri11/dealix-demo",
    "ask_price": "نبدأها كـ pilot بسيط لمدة 7 أيام بـ 499 ريال.\nنجرب على 10-25 lead، ونقيس النتائج.\nلو ما عجبك — استرداد كامل.",
    "ask_details": "Dealix يساعدكم في:\n- الرد السريع على الـ leads\n- تأهيل العميل بأسئلة واضحة\n- حجز موعد أو تحويله لفريق المبيعات\n- تقرير يومي مختصر\n\nأفضل بداية: pilot 7 أيام. يناسبك أشرح أكثر؟",
    "ask_demo": "تمام! احجز الوقت المناسب:\ncalendly.com/sami-assiri11/dealix-demo\n\nأو قلي وقتين يناسبونك وأنا أنسّق.",
    "not_now": "تمام، شكراً على وقتك. أتواصل معك بعد شهر لو مناسب؟",
    "objection_budget": "فاهم. لذلك نبدأ بـ pilot بسيط بـ 499 ريال فقط.\nلو ما شفت قيمة خلال 7 أيام — استرداد كامل.",
    "already_has_crm": "ممتاز، Dealix ما يستبدل الـ CRM.\nهو طبقة قبله: يرد على الـ lead، يأهله، يحجز الموعد،\nوبعدها يسلّم البيانات لفريقكم أو للـ CRM.",
    "unsubscribe": "تم، لن أتواصل معكم مرة ثانية. شكراً على وقتكم.",
}


class ClassifyReplyRequest(BaseModel):
    reply_text: str
    company: str = ""
    original_sector: str = ""


@router.post("/reply/classify")
async def classify_reply(req: ClassifyReplyRequest) -> Dict[str, Any]:
    text = req.reply_text.lower()

    if any(w in text for w in ["إيقاف", "stop", "unsubscribe", "لا تتواصل", "remove"]):
        cat = "unsubscribe"
    elif any(w in text for w in ["كم السعر", "كم التكلفة", "how much", "pricing", "أسعار"]):
        cat = "ask_price"
    elif any(w in text for w in ["عرض", "demo", "ديمو", "أوريني", "شرح"]):
        cat = "ask_demo"
    elif any(w in text for w in ["مهتم", "interested", "أبي أجرب", "نجرب", "تمام"]):
        cat = "interested"
    elif any(w in text for w in ["تفاصيل", "details", "أكثر", "وش بالضبط"]):
        cat = "ask_details"
    elif any(w in text for w in ["لاحقاً", "later", "مو الحين", "بعدين"]):
        cat = "not_now"
    elif any(w in text for w in ["ميزانية", "budget", "غالي", "مكلف"]):
        cat = "objection_budget"
    elif any(w in text for w in ["CRM", "crm", "نظام", "عندنا حل"]):
        cat = "already_has_crm"
    elif any(w in text for w in ["شراكة", "partner", "وكالة", "نبيع"]):
        cat = "partnership"
    elif any(w in text for w in ["خصوصية", "privacy", "بيانات", "PDPL"]):
        cat = "objection_privacy"
    elif any(w in text for w in ["ذكاء", "AI", "عربي طبيعي", "مضبوط"]):
        cat = "objection_ai"
    elif any(w in text for w in ["زعلان", "angry", "spam", "مزعج"]):
        cat = "angry"
    else:
        cat = "ask_details"

    info = REPLY_CATEGORIES.get(cat, {"next": "human_review", "auto_reply": False})
    response = REPLY_RESPONSES.get(cat, "شكراً على ردك. براجع وأرد عليك قريب.")

    return {
        "category": cat,
        "next_action": info["next"],
        "auto_reply_allowed": info["auto_reply"],
        "suggested_response": response,
        "human_review_required": not info["auto_reply"],
        "company": req.company,
    }
