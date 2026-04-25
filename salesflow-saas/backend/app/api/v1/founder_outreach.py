"""Founder Outreach — hyper-personalized emails from Sami as founder.

Each email researches the company's weakness, estimates lost revenue,
and writes a personal message showing exact ROI Dealix can deliver.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger("dealix.founder_outreach")

router = APIRouter(prefix="/founder-outreach", tags=["Founder Outreach"])

SECTOR_WEAKNESS_MAP = {
    "real_estate": {
        "weakness_ar": "شركات العقار تستقبل 50-200 استفسار/شهر عن الأسعار والمواقع. المشكلة: 60-70% ما يُتابع خلال أول ساعة = العميل يروح للمنافس",
        "weakness_en": "Real estate companies receive 50-200 inquiries/month about prices and locations. Problem: 60-70% don't get a response within the first hour = client goes to competitor",
        "revenue_loss_ar": "لو عندكم 100 استفسار/شهر و60% تضيع = 60 فرصة ضائعة. لو 10% منها كانت بتتحول = 6 صفقات × متوسط 50,000 ريال = ~300,000 ريال ضائعة سنوياً",
        "revenue_loss_en": "If you get 100 inquiries/month and 60% are lost = 60 missed opportunities. If 10% would convert = 6 deals × avg 50,000 SAR = ~300,000 SAR lost annually",
        "dealix_impact_ar": "Dealix يرد خلال 45 ثانية ويحفظ 30-40% من الفرص الضائعة = ~120,000 ريال إضافية/سنة. تكلفة Dealix = 990 ريال/شهر = ROI 10x",
        "dealix_impact_en": "Dealix responds in 45 seconds and saves 30-40% of lost opportunities = ~120,000 SAR additional/year. Dealix costs 990 SAR/month = 10x ROI",
    },
    "construction": {
        "weakness_ar": "شركات المقاولات تستقبل طلبات عروض أسعار يومياً. المشكلة: فرز الطلبات الجادة من غيرها ياخذ ساعات من المهندسين — وقت ممكن يُصرف في التنفيذ",
        "weakness_en": "Construction companies receive quote requests daily. Problem: Sorting serious from non-serious requests takes hours of engineer time",
        "revenue_loss_ar": "لو فريق المبيعات يقضي 2 ساعة/يوم في فرز الطلبات = 40 ساعة/شهر = تكلفة ~8,000 ريال/شهر من وقت الفريق",
        "revenue_loss_en": "If sales team spends 2 hours/day sorting requests = 40 hours/month = ~8,000 SAR/month in team time cost",
        "dealix_impact_ar": "Dealix يستقبل الطلب، يسأل 3 أسئلة تأهيل، ويصنّف الجدية تلقائياً. يوفّر 80% من وقت الفرز = ~6,400 ريال/شهر. ROI: 6.5x",
        "dealix_impact_en": "Dealix receives requests, asks 3 qualifying questions, and auto-classifies urgency. Saves 80% of sorting time = ~6,400 SAR/month. ROI: 6.5x",
    },
    "hospitality": {
        "weakness_ar": "الفنادق والقاعات تستقبل استفسارات حجز يومياً. المشكلة: كل ساعة تأخير = احتمال 50% العميل يحجز عند المنافس",
        "weakness_en": "Hotels and event venues receive booking inquiries daily. Problem: every hour of delay = 50% chance the client books with a competitor",
        "revenue_loss_ar": "لو 10 استفسارات/أسبوع تضيع بسبب تأخر الرد × متوسط حجز 5,000 ريال = 200,000 ريال ضائعة/سنة",
        "revenue_loss_en": "If 10 inquiries/week are lost due to slow response × avg booking 5,000 SAR = 200,000 SAR lost/year",
        "dealix_impact_ar": "Dealix يرد فوراً، يسأل عن التاريخ والعدد والميزانية، ويحجز مبدئي. يحفظ 40% من الحجوزات الضائعة = ~80,000 ريال/سنة",
        "dealix_impact_en": "Dealix responds instantly, asks about date, guest count, and budget, and makes a preliminary booking. Saves 40% of lost bookings = ~80,000 SAR/year",
    },
    "agency": {
        "weakness_ar": "الوكالات تصرف على إعلانات عملائها لكن المتابعة على الـ leads ضعيفة. النتيجة: العميل يلوم الوكالة على ضعف النتائج",
        "weakness_en": "Agencies spend on client ads but lead follow-up is weak. Result: client blames agency for poor results",
        "revenue_loss_ar": "كل عميل وكالة يدفع 5,000-20,000 ريال/شهر. لو عميل واحد يطلع بسبب ضعف المتابعة = خسارة 60,000-240,000 ريال/سنة",
        "revenue_loss_en": "Each agency client pays 5,000-20,000 SAR/month. If one client leaves due to poor follow-up = loss of 60,000-240,000 SAR/year",
        "dealix_impact_ar": "Dealix يصير خدمة جديدة تبيعونها: رد ذكي + تأهيل + حجز. Setup fee 3,000 + MRR 990/عميل = إيراد جديد بدل خسارة عميل",
        "dealix_impact_en": "Dealix becomes a new service you sell: smart response + qualification + booking. Setup fee 3,000 + MRR 990/client = new revenue instead of losing a client",
    },
    "saas": {
        "weakness_ar": "شركات SaaS تجيها leads من الموقع والإعلانات لكن فريق المبيعات صغير. المشكلة: 30-50% من الـ leads تبرد خلال أول 24 ساعة",
        "weakness_en": "SaaS companies get leads from website and ads but sales team is small. Problem: 30-50% of leads go cold within 24 hours",
        "revenue_loss_ar": "لو 200 lead/شهر و40% تبرد = 80 lead ضائع. لو 5% كانت بتشتري × متوسط 5,000 ريال/سنة = 20,000 ريال ضائعة/شهر",
        "revenue_loss_en": "If 200 leads/month and 40% go cold = 80 lost leads. If 5% would buy × avg 5,000 SAR/year = 20,000 SAR lost/month",
        "dealix_impact_ar": "Dealix يرد بالعربي خلال 45 ثانية على كل lead، يؤهل، ويحجز demo. يحفظ 30% من الضائع = ~6,000 ريال إضافية/شهر. ROI: 6x",
        "dealix_impact_en": "Dealix responds in Arabic within 45 seconds to every lead, qualifies, and books demos. Saves 30% of lost leads = ~6,000 SAR additional/month. ROI: 6x",
    },
    "logistics": {
        "weakness_ar": "شركات الشحن تستقبل طلبات أسعار متكررة. المشكلة: كل طلب ما يُتابع = شحنة تروح للمنافس مباشرة",
        "weakness_en": "Shipping companies receive repeated quote requests. Problem: every unfollowed request = shipment goes directly to competitor",
        "revenue_loss_ar": "لو 5 طلبات/أسبوع تضيع × متوسط 3,000 ريال/شحنة = 60,000 ريال ضائعة/شهر",
        "revenue_loss_en": "If 5 requests/week are lost × avg 3,000 SAR/shipment = 60,000 SAR lost/month",
        "dealix_impact_ar": "Dealix يستقبل الطلب، يسأل عن نوع الشحنة والوجهة، ويعطي تقدير أولي فوراً. يحفظ 40% = ~24,000 ريال/شهر",
        "dealix_impact_en": "Dealix receives requests, asks about shipment type and destination, gives instant estimate. Saves 40% = ~24,000 SAR/month",
    },
}


class FounderEmailRequest(BaseModel):
    company: str
    sector: str
    contact_name: str = ""
    contact_email: str = ""
    city: str = ""
    website: str = ""
    signals: List[str] = []
    language: str = "ar"
    estimated_monthly_leads: int = 100


@router.post("/generate")
async def generate_founder_email(req: FounderEmailRequest) -> Dict[str, Any]:
    """Generate a hyper-personalized founder email that targets the company's weakness."""
    sector_data = SECTOR_WEAKNESS_MAP.get(req.sector, SECTOR_WEAKNESS_MAP.get("saas", {}))
    lang = req.language

    if lang == "en":
        return _build_en(req, sector_data)

    name = req.contact_name or f"فريق {req.company}"
    weakness = sector_data.get("weakness_ar", "")
    revenue_loss = sector_data.get("revenue_loss_ar", "")
    impact = sector_data.get("dealix_impact_ar", "")

    signal_line = ""
    if "hubspot" in [s.lower() for s in req.signals]:
        signal_line = f"شفت إن {req.company} تستخدمون HubSpot — يعني عندكم leads تجي من الموقع. "
    elif "whatsapp_widget" in [s.lower() for s in req.signals]:
        signal_line = f"لاحظت إن عندكم واتساب كقناة رئيسية للعملاء. "

    subject = f"{name} — فرصة توفير {req.estimated_monthly_leads * 50} ريال/شهر لـ {req.company}"

    body = f"""مرحباً {name}،

أنا سامي العسيري، مؤسس Dealix.

{signal_line}أكتب لك شخصياً لأن لاحظت شي مهم عن {req.company}:

📊 المشكلة:
{weakness}

💰 التكلفة الحقيقية:
{revenue_loss}

🎯 الحل:
{impact}

ما أبي أبيعك شي الحين — أبي أوريك بالأرقام.

نسوي pilot 7 أيام على leads حقيقية عندكم:
• نرد على كل استفسار خلال 45 ثانية
• نسأل أسئلة التأهيل المهمة لقطاعكم
• نحجز المواعيد أو نحوّل للمبيعات
• نرسل تقرير يومي بالنتائج

السعر: 499 ريال فقط (مع ضمان استرداد كامل).

يناسبك 15 دقيقة هذا الأسبوع أوريك النظام على سيناريو من شغلكم؟
📅 calendly.com/sami-assiri11/dealix-demo

وإذا عندك سؤال — رد على هالإيميل مباشرة. أنا شخصياً أرد.

سامي العسيري
مؤسس Dealix
dealix.me
+966 59 778 8539

إذا ما يناسبكم هالنوع من الرسائل، اكتبوا "إيقاف" وما بنتواصل مرة ثانية."""

    return {
        "type": "founder_personal",
        "company": req.company,
        "language": "ar",
        "subject": subject,
        "body": body,
        "weakness_targeted": weakness[:100],
        "revenue_loss_estimate": revenue_loss[:100],
        "dealix_roi": impact[:100],
        "opt_out_included": True,
        "word_count": len(body.split()),
    }


def _build_en(req: FounderEmailRequest, sector_data: Dict) -> Dict[str, Any]:
    name = req.contact_name or f"{req.company} team"
    weakness = sector_data.get("weakness_en", "")
    revenue_loss = sector_data.get("revenue_loss_en", "")
    impact = sector_data.get("dealix_impact_en", "")

    signal_line = ""
    if "hubspot" in [s.lower() for s in req.signals]:
        signal_line = f"I noticed {req.company} uses HubSpot — meaning you have leads coming from your website. "

    subject = f"{name} — opportunity to save {req.estimated_monthly_leads * 50} SAR/month for {req.company}"

    body = f"""Hi {name},

I'm Sami Alassiri, founder of Dealix.

{signal_line}I'm writing personally because I noticed something important about {req.company}:

📊 The Problem:
{weakness}

💰 The Real Cost:
{revenue_loss}

🎯 The Solution:
{impact}

I'm not trying to sell you anything right now — I want to show you with numbers.

We'll run a 7-day pilot on your actual leads:
• Respond to every inquiry within 45 seconds
• Ask the right qualifying questions for your industry
• Book meetings or route to sales
• Send you a daily results report

Price: 499 SAR only (with full money-back guarantee).

Do you have 15 minutes this week? I'll show you the system on a scenario from your business.
📅 calendly.com/sami-assiri11/dealix-demo

Questions? Reply to this email directly. I personally respond.

Sami Alassiri
Founder, Dealix
dealix.me
+966 59 778 8539

To stop receiving these emails, reply "STOP"."""

    return {
        "type": "founder_personal",
        "company": req.company,
        "language": "en",
        "subject": subject,
        "body": body,
        "weakness_targeted": weakness[:100],
        "revenue_loss_estimate": revenue_loss[:100],
        "dealix_roi": impact[:100],
        "opt_out_included": True,
        "word_count": len(body.split()),
    }
