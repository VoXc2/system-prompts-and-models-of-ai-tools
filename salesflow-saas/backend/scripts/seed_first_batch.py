#!/usr/bin/env python3
"""Seed 20 outreach drafts — 10 email + 10 WhatsApp for top Saudi companies."""
import asyncio, sys, os, uuid
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 10 EMAIL DRAFTS ===
EMAILS = [
    {"company": "Peak Content", "contact_email": "hello@peakcontent.sa", "sector": "agency", "fit": 92,
     "subject": "خدمة جديدة تزيد إيراد عملائكم — بدون تكلفة عليكم",
     "body": "السلام عليكم فريق Peak Content،\n\nأنا سامي من Dealix. المشكلة عند كل وكالة: العميل يدفع 5-20K ريال/شهر على إعلانات لكن المتابعة ضعيفة = يلوم الوكالة.\n\nDealix يرد على leads عملائكم بالعربي خلال 45 ثانية، يؤهل، ويحجز مواعيد.\n\nتقدمونه كخدمة: Setup 3,000 + 990/شهر لكل عميل = إيراد جديد.\n\nPilot مجاني لأول عميل — 7 أيام.\n\n10 دقائق نتكلم؟\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "تابع لرسالتي عن Dealix. لو عندكم عميل يعاني من متابعة leads — نجربه مجاناً 7 أيام.", "f5": "آخر متابعة — وكالات بدأت تبيع Dealix كخدمة إضافية. أرسلوا 'مهتم' للتفاصيل."},
    {"company": "Aqar.fm", "contact_email": "info@aqar.fm", "sector": "real_estate", "fit": 95,
     "subject": "300K ريال ضائعة سنوياً من استفسارات ما تُتابع",
     "body": "السلام عليكم فريق عقار،\n\nأنا سامي من Dealix. 60-70% من استفسارات العقار ما تُتابع خلال ساعة = العميل يروح للمنافس.\n\n100 استفسار/شهر × 60% ضائعة × 10% تحويل × 50K = ~300K ريال ضائعة/سنة.\n\nDealix يرد خلال 45 ثانية، يسأل عن الميزانية والموقع، ويحجز جولة عرض. يحفظ 30-40% = ~120K إضافية/سنة. تكلفة 990/شهر = ROI 10x.\n\nPilot 7 أيام بـ 499 ريال مع ضمان استرداد.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "كل يوم تأخير = استفسارات تضيع. Pilot 499 ريال مع ضمان استرداد.", "f5": "آخر متابعة — أرسلوا 'demo' لنعرض كيف يرد خلال 45 ثانية."},
    {"company": "Foodics", "contact_email": "sales@foodics.com", "sector": "saas", "fit": 88,
     "subject": "leads موقعكم تبرد — حل يرد بالعربي خلال 45 ثانية",
     "body": "السلام عليكم فريق Foodics،\n\nأنا سامي من Dealix. شفت إنكم تستخدمون HubSpot + WhatsApp.\n\n30-50% من leads SaaS تبرد خلال 24 ساعة. 200 lead/شهر × 40% بارد × 5% تحويل × 5K = 20K ضائعة/شهر.\n\nDealix يرد بالعربي خلال 45 ثانية، يؤهل، ويحجز demo. يكمّل HubSpot مو يبدّله.\n\nيحفظ 30% = ~6K إضافية/شهر. ROI 6x.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "يكمّل HubSpot — يرد قبل ما الـ leads تبرد. Pilot 7 أيام؟", "f5": "أرسلوا 'demo' لنعرض كيف يشتغل مع HubSpot."},
    {"company": "Rewaa", "contact_email": "info@rewaatech.com", "sector": "saas", "fit": 86,
     "subject": "الـ leads اللي تبرد بالليل والويكند — حل 24/7",
     "body": "السلام عليكم فريق رواء،\n\nأنا سامي من Dealix. عندكم WhatsApp widget — ممتاز. بس وش يصير لما lead يرسل الساعة 11 بالليل؟\n\nDealix يرد 24/7 بالعربي خلال 45 ثانية، يؤهل، ويحجز demo.\n\n990 ريال/شهر. Pilot 499 ريال مع ضمان استرداد.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "كل ليلة بدون Dealix = leads تبرد. pilot سريع؟", "f5": "أرسلوا 'demo' لنعرض كيف يشتغل."},
    {"company": "BRKZ", "contact_email": "info@brkz.com", "sector": "construction", "fit": 84,
     "subject": "فرز طلبات الأسعار تلقائياً — وفّروا 40 ساعة/شهر",
     "body": "السلام عليكم فريق BRKZ،\n\nأنا سامي من Dealix. فرز طلبات عروض الأسعار ياخذ 2 ساعة/يوم = 40 ساعة/شهر = ~8K ريال.\n\nDealix يستقبل الطلب، يسأل 3 أسئلة تأهيل، ويصنّف الجدية. يوفّر 80% = ~6.4K/شهر. ROI 6.5x.\n\nPilot 499 ريال مع ضمان استرداد.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "كل طلب ما يُتابع = فرصة تروح للمنافس. Pilot 7 أيام؟", "f5": "أرسلوا 'demo' لنعرض فرز الطلبات."},
    {"company": "Qoyod", "contact_email": "info@qoyod.com", "sector": "saas", "fit": 85,
     "subject": "كم lead يجيكم ويبرد قبل ما أحد يرد؟",
     "body": "السلام عليكم فريق قيود،\n\nأنا سامي من Dealix. عند شركات SaaS: 30-50% تبرد خلال 24 ساعة.\n\nDealix يرد خلال 45 ثانية بالعربي، يسأل عن حجم الشركة، ويحجز demo. يشتغل مع HubSpot.\n\n990/شهر. Pilot 499 ريال مع ضمان.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "Dealix + HubSpot = كل lead يُتابع فوراً. مهتمين؟", "f5": "أرسلوا 'demo' لنعرض."},
    {"company": "Maqsam", "contact_email": "info@maqsam.com", "sector": "saas", "fit": 82,
     "subject": "أنتم في الاتصالات — جربوا AI SDR يرد بالعربي",
     "body": "السلام عليكم فريق مقسم،\n\nأنا سامي من Dealix. أنتم تفهمون الرد السريع أكثر من أي أحد.\n\nDealix = AI SDR يرد بالعربي خلال 45 ثانية، يؤهل، ويحجز demo.\n\nالفكرة: Dealix فوق مقسم = حل متكامل. Partnership أو pilot؟\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "Dealix فوق مقسم = حل متكامل. مهتمين نتكلم؟", "f5": "أرسلوا 'مهتم' لنستكشف."},
    {"company": "Digital8", "contact_email": "hello@digital8.sa", "sector": "agency", "fit": 90,
     "subject": "خدمة جديدة لعملائكم — إيراد إضافي",
     "body": "السلام عليكم فريق Digital8،\n\nأنا سامي من Dealix. العميل يدفع على الإعلانات لكن يلوم الوكالة لما leads ما تتحول. السبب: بطء المتابعة.\n\nDealix يرد خلال 45 ثانية بالعربي. تقدمونه كخدمة: Setup 3K + 990/شهر لكل عميل.\n\nPilot مجاني لأول عميل. 7 أيام.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "عندكم عميل يعاني من leads؟ نجربه مجاناً.", "f5": "وكالات بدأت تبيع Dealix. أرسلوا 'مهتم'."},
    {"company": "Floward", "contact_email": "b2b@floward.com", "sector": "logistics", "fit": 78,
     "subject": "طلبات الشركات B2B — كل واحد ما يُتابع = إيراد ضائع",
     "body": "السلام عليكم فريق Floward،\n\nأنا سامي من Dealix. طلبات B2B (هدايا، مناسبات) تحتاج رد سريع. كل تأخير = يطلب من المنافس.\n\nDealix يستقبل الطلب فوراً، يسأل عن العدد والميزانية والتاريخ. فريقكم يستلم طلب مؤهّل.\n\n990/شهر. Pilot 499 ريال.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "كل طلب B2B ما يُتابع = إيراد يروح. مهتمين؟", "f5": "أرسلوا 'demo'."},
    {"company": "Sary", "contact_email": "info@sary.sa", "sector": "logistics", "fit": 75,
     "subject": "طلبات التجار اللي تضيع — رد فوري",
     "body": "السلام عليكم فريق ساري،\n\nأنا سامي من Dealix. كل طلب تاجر ما يُتابع = يطلب من مورد ثاني.\n\nDealix يرد فوراً بالعربي، يسأل عن المنتج والكمية. يحفظ 40% من الضائع.\n\n990/شهر. Pilot 499 ريال.\n\nسامي عسيري — مؤسس Dealix\ndealix.me\n\nإذا ما يناسبكم، اكتبوا 'إيقاف'.",
     "f2": "حجم طلباتكم كبير — Dealix يضمن ما يضيع. pilot؟", "f5": "أرسلوا 'demo'."},
]

# === 10 WHATSAPP DRAFTS (shorter, direct) ===
WHATSAPP = [
    {"company": "Peak Content", "phone": "", "sector": "agency", "fit": 92,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. عندنا نظام يرد على leads عملاء الوكالات خلال 45 ثانية بالعربي.\n\nتقدرون تقدمونه كخدمة لعملائكم (990 ريال/شهر لكل عميل).\n\nPilot مجاني لأول عميل. مهتمين؟"},
    {"company": "Aqar.fm", "phone": "", "sector": "real_estate", "fit": 95,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. 60% من استفسارات العقار تضيع بسبب تأخر الرد.\n\nDealix يرد خلال 45 ثانية ويحجز جولة عرض تلقائياً.\n\nPilot 7 أيام بـ 499 ريال مع ضمان استرداد. مهتمين؟"},
    {"company": "Foodics", "phone": "", "sector": "saas", "fit": 88,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. شفت إنكم تستخدمون HubSpot.\n\nDealix يرد على leads موقعكم خلال 45 ثانية بالعربي ويحجز demo. يكمّل HubSpot.\n\n10 دقائق نتكلم؟"},
    {"company": "Rewaa", "phone": "", "sector": "saas", "fit": 86,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. عندكم WhatsApp widget — بس وش يصير لما lead يرسل بالليل؟\n\nDealix يرد 24/7 خلال 45 ثانية. Pilot 499 ريال. مهتمين؟"},
    {"company": "BRKZ", "phone": "", "sector": "construction", "fit": 84,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. فرز طلبات الأسعار عندكم ياخذ وقت المهندسين.\n\nDealix يفرز تلقائياً — يسأل 3 أسئلة ويصنّف الجدية. يوفّر 80% من الوقت.\n\nPilot 499 ريال. مهتمين؟"},
    {"company": "Salla", "phone": "", "sector": "saas", "fit": 88,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. تجار سلة يحتاجون رد سريع على استفسارات العملاء.\n\nDealix يرد خلال 45 ثانية بالعربي ويؤهل العميل. ممكن يكون إضافة على منصتكم.\n\nمهتمين نتكلم partnership؟"},
    {"company": "Zid", "phone": "", "sector": "saas", "fit": 85,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. تجار زد يخسرون طلبات بسبب بطء الرد.\n\nDealix يرد فوراً ويؤهل. ممكن يكون إضافة على منصتكم.\n\npartnership أو pilot؟"},
    {"company": "Lean Technologies", "phone": "", "sector": "saas", "fit": 80,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. فريق مبيعات صغير + leads كثيرة = فرص تضيع.\n\nDealix يرد بالعربي خلال 45 ثانية ويحجز demo تلقائياً.\n\nPilot 7 أيام؟"},
    {"company": "Lucidya", "phone": "", "sector": "saas", "fit": 83,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. شفت عندكم 4 أدوات GTM.\n\nDealix يكمّل الـ stack — يرد على leads خلال 45 ثانية بالعربي قبل ما تبرد.\n\n10 دقائق نتكلم؟"},
    {"company": "HyperPay", "phone": "", "sector": "saas", "fit": 79,
     "body": "السلام عليكم 👋\n\nأنا سامي من Dealix. استفسارات التجار عن بوابة الدفع تحتاج رد سريع.\n\nDealix يرد فوراً بالعربي ويؤهل التاجر.\n\nPilot 499 ريال. مهتمين؟"},
]


async def seed():
    os.environ.setdefault("DATABASE_URL", "")
    from app.database import async_session, init_db
    from app.models.outreach_draft import OutreachDraft

    await init_db()
    now = datetime.now(timezone.utc)
    batch_id = f"founder_batch_{now.strftime('%Y%m%d_%H%M')}"
    count = 0

    async with async_session() as session:
        for e in EMAILS:
            session.add(OutreachDraft(
                id=uuid.uuid4(), company=e["company"], contact_name=f"فريق {e['company']}",
                contact_email=e["contact_email"], contact_phone="", channel="email",
                subject=e["subject"], body=e["body"], followup_2d=e["f2"], followup_5d=e["f5"],
                sector=e["sector"], pain_hypothesis=f"sector:{e['sector']}",
                fit_score=e["fit"], risk_score=5, status="draft", approval_required=True,
                batch_id=batch_id, created_at=now))
            count += 1

        for w in WHATSAPP:
            session.add(OutreachDraft(
                id=uuid.uuid4(), company=w["company"], contact_name=f"فريق {w['company']}",
                contact_email="", contact_phone=w["phone"], channel="whatsapp",
                subject="", body=w["body"], followup_2d="", followup_5d="",
                sector=w["sector"], pain_hypothesis=f"sector:{w['sector']}",
                fit_score=w["fit"], risk_score=5, status="draft", approval_required=True,
                batch_id=batch_id, created_at=now))
            count += 1

        await session.commit()
        print(f"✅ Seeded {count} drafts (10 email + 10 WhatsApp)")
        print(f"   Batch: {batch_id}")
        print(f"\n   Review:  GET /api/v1/drafts?status=draft")
        print(f"   Approve: POST /api/v1/drafts/approve-batch")
        print(f"   Send:    POST /api/v1/drafts/send-approved-batch?channel=email&batch_size=5")

if __name__ == "__main__":
    asyncio.run(seed())
