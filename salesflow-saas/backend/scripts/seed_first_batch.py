#!/usr/bin/env python3
"""Seed first 10 outreach drafts — real companies, real messages."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BATCH = [
    {
        "company": "Peak Content",
        "contact_name": "فريق Peak Content",
        "contact_email": "hello@peakcontent.sa",
        "contact_phone": "",
        "channel": "email",
        "sector": "agency",
        "subject": "خدمة جديدة تزيد إيراد عملائكم — بدون تكلفة عليكم",
        "body": """السلام عليكم فريق Peak Content،

أنا سامي من Dealix. شفت إنكم تخدمون عملاء في التسويق الرقمي.

المشكلة اللي نشوفها عند كل وكالة: العميل يدفع 5,000-20,000 ريال/شهر على إعلانات، لكن المتابعة على الـ leads ضعيفة. النتيجة: العميل يلوم الوكالة.

Dealix يحل هذا — نظام يرد على leads عملائكم بالعربي خلال 45 ثانية، يؤهلهم، ويحجز مواعيد تلقائياً.

الفكرة: تقدمونه كخدمة إضافية لعملائكم (Setup 3,000 + 990 ريال/شهر لكل عميل). إيراد جديد بدون تكلفة تشغيل.

أبي أعطيكم pilot مجاني لأول عميل عندكم — 7 أيام.

وقتكم 10 دقائق هالأسبوع؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، تابع لرسالتي السابقة عن Dealix. لو عندكم عميل واحد يعاني من متابعة الـ leads — نجربه مجاناً 7 أيام. وش رأيكم؟",
        "followup_5d": "آخر متابعة — لو الوقت مو مناسب الحين أفهم تماماً. بس لو تبون تشوفون كيف وكالات ثانية تستخدم Dealix كخدمة إضافية، أرسلوا 'مهتم' وأشارككم التفاصيل.",
        "fit_score": 92,
        "risk_score": 5,
    },
    {
        "company": "Aqar.fm",
        "contact_name": "فريق عقار",
        "contact_email": "info@aqar.fm",
        "contact_phone": "",
        "channel": "email",
        "sector": "real_estate",
        "subject": "300,000 ريال ضائعة سنوياً من استفسارات ما تُتابع — الحل",
        "body": """السلام عليكم فريق عقار،

أنا سامي من Dealix. منصتكم أكبر سوق عقاري بالسعودية — وهذا يعني آلاف الاستفسارات يومياً.

الواقع: 60-70% من استفسارات العقار ما تُتابع خلال أول ساعة. العميل يروح للمنافس.

لو 100 استفسار/شهر و60% تضيع = 60 فرصة. لو 10% كانت بتتحول = 6 صفقات × 50,000 ريال = ~300,000 ريال ضائعة سنوياً.

Dealix يرد خلال 45 ثانية بالعربي، يسأل عن الميزانية والموقع المفضل، ويحجز جولة عرض تلقائياً.

يحفظ 30-40% من الفرص الضائعة = ~120,000 ريال إضافية/سنة. تكلفة 990 ريال/شهر = ROI 10x.

نجرّب pilot 7 أيام بـ 499 ريال فقط مع ضمان استرداد كامل.

10 دقائق نتكلم؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، تابع لرسالتي عن Dealix. كل يوم تأخير = استفسارات تضيع. Pilot 7 أيام بـ 499 ريال مع ضمان استرداد. وش رأيكم؟",
        "followup_5d": "آخر متابعة — لو تبون تشوفون demo حي لكيف Dealix يرد على استفسارات العقار خلال 45 ثانية، أرسلوا 'demo'.",
        "fit_score": 95,
        "risk_score": 3,
    },
    {
        "company": "Foodics",
        "contact_name": "فريق Foodics",
        "contact_email": "sales@foodics.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "saas",
        "subject": "leads الموقع تبرد — حل يرد بالعربي خلال 45 ثانية",
        "body": """السلام عليكم فريق Foodics،

أنا سامي من Dealix. شفت إنكم تستخدمون HubSpot + WhatsApp — يعني عندكم pipeline قوي.

لكن السؤال: كم lead من الموقع يبرد خلال أول 24 ساعة قبل ما فريق المبيعات يتواصل؟

الواقع عند شركات SaaS: 30-50% من الـ leads تبرد. لو 200 lead/شهر و40% تبرد = 80 lead ضائع. لو 5% كانت بتشتري = 20,000 ريال ضائعة/شهر.

Dealix يرد بالعربي خلال 45 ثانية على كل lead، يؤهل، ويحجز demo تلقائياً. يشتغل مع HubSpot — يكمّل الـ stack مو يبدّله.

يحفظ 30% من الضائع = ~6,000 ريال إضافية/شهر. تكلفة 990 ريال/شهر = ROI 6x.

وقتكم 10 دقائق هالأسبوع؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، تابع لرسالتي عن Dealix. يكمّل HubSpot — يرد على الـ leads قبل ما تبرد. Pilot 7 أيام؟",
        "followup_5d": "آخر متابعة — لو تبون demo حي لكيف Dealix يشتغل مع HubSpot، أرسلوا 'demo'.",
        "fit_score": 88,
        "risk_score": 8,
    },
    {
        "company": "Rewaa",
        "contact_name": "فريق رواء",
        "contact_email": "info@rewaatech.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "saas",
        "subject": "الـ leads اللي تبرد قبل ما فريقكم يرد — حل سريع",
        "body": """السلام عليكم فريق رواء،

أنا سامي من Dealix. شفت إنكم تستخدمون WhatsApp widget على الموقع — ممتاز للتواصل.

السؤال: وش يصير لما lead يرسل رسالة الساعة 11 بالليل أو الجمعة؟ ينتظر للصباح؟

Dealix يرد بالعربي خلال 45 ثانية 24/7، يؤهل العميل، ويحجز demo. لو عندكم 200 lead/شهر و40% تبرد = 80 فرصة ضائعة.

Dealix يحفظ 30% = ~24 صفقة إضافية/شهر. بـ 990 ريال/شهر = ROI واضح.

Pilot 7 أيام بـ 499 ريال مع ضمان استرداد كامل.

10 دقائق نتكلم؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، تابع لرسالتي. كل ليلة بدون Dealix = leads تبرد. وش رأيكم بـ pilot سريع؟",
        "followup_5d": "آخر متابعة — أرسلوا 'demo' لو تبون تشوفون كيف يشتغل مع WhatsApp widget.",
        "fit_score": 86,
        "risk_score": 5,
    },
    {
        "company": "BRKZ",
        "contact_name": "فريق BRKZ",
        "contact_email": "info@brkz.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "construction",
        "subject": "فرز طلبات الأسعار تلقائياً — وفّروا 40 ساعة/شهر",
        "body": """السلام عليكم فريق BRKZ،

أنا سامي من Dealix. شركات المقاولات مثلكم تستقبل طلبات عروض أسعار يومياً.

المشكلة: فرز الطلبات الجادة من غيرها ياخذ ساعات من المهندسين — وقت المفروض يُصرف في التنفيذ.

لو فريقكم يقضي 2 ساعة/يوم في فرز الطلبات = 40 ساعة/شهر = ~8,000 ريال من وقت الفريق.

Dealix يستقبل الطلب، يسأل 3 أسئلة تأهيل (نوع المشروع، الميزانية، الجدول)، ويصنّف الجدية تلقائياً. يوفّر 80% من وقت الفرز = ~6,400 ريال/شهر. ROI: 6.5x.

Pilot 7 أيام بـ 499 ريال مع ضمان استرداد.

10 دقائق نتكلم؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، تابع لرسالتي. كل طلب عرض سعر ما يُتابع = فرصة تروح للمنافس. Pilot 7 أيام؟",
        "followup_5d": "آخر متابعة — لو تبون تشوفون كيف Dealix يفرز طلبات الأسعار تلقائياً، أرسلوا 'demo'.",
        "fit_score": 84,
        "risk_score": 5,
    },
    {
        "company": "Qoyod",
        "contact_name": "فريق قيود",
        "contact_email": "info@qoyod.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "saas",
        "subject": "الـ leads اللي تجيكم من الموقع — كم واحد يبرد؟",
        "body": """السلام عليكم فريق قيود،

أنا سامي من Dealix. شفت إنكم تستخدمون HubSpot + WhatsApp — pipeline ممتاز.

سؤال واحد: كم lead يجيكم من الموقع ويبرد قبل ما أحد يرد؟

عند شركات SaaS المحاسبية: 30-50% تبرد خلال 24 ساعة. الحل مو توظيف أكثر — الحل رد فوري بالعربي.

Dealix يرد خلال 45 ثانية، يسأل عن حجم الشركة ونوع النشاط، ويحجز demo. يشتغل مع HubSpot.

990 ريال/شهر. Pilot 7 أيام بـ 499 ريال مع ضمان استرداد.

وقتكم 10 دقائق؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، متابعة سريعة. Dealix + HubSpot = كل lead يُتابع فوراً. مهتمين بـ pilot؟",
        "followup_5d": "آخر متابعة — أرسلوا 'demo' لو تبون تشوفون Dealix يشتغل.",
        "fit_score": 85,
        "risk_score": 5,
    },
    {
        "company": "Maqsam",
        "contact_name": "فريق مقسم",
        "contact_email": "info@maqsam.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "saas",
        "subject": "أنتم في الاتصالات — جربوا AI SDR يرد بالعربي",
        "body": """السلام عليكم فريق مقسم،

أنا سامي من Dealix. أنتم تبنون حلول اتصالات سحابية — يعني تفهمون قيمة الرد السريع أكثر من أي أحد.

سؤال: كم من leads موقعكم تبرد لأن فريق المبيعات مشغول بالمكالمات الحالية؟

Dealix = AI SDR يرد بالعربي خلال 45 ثانية على كل lead، يؤهل، ويحجز demo. يكمّل HubSpot — مو يبدّله.

الفكرة: أنتم تبيعون أدوات اتصال. لو أضفتوا Dealix كطبقة فوق منتجكم = ميزة تنافسية.

نتكلم 10 دقائق عن partnership أو pilot؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، متابعة. ممكن يكون في فرصة partnership — Dealix فوق مقسم = حل متكامل. مهتمين نتكلم؟",
        "followup_5d": "آخر متابعة — أرسلوا 'مهتم' لو تبون نستكشف الفكرة.",
        "fit_score": 82,
        "risk_score": 10,
    },
    {
        "company": "Digital8",
        "contact_name": "فريق Digital8",
        "contact_email": "hello@digital8.sa",
        "contact_phone": "",
        "channel": "email",
        "sector": "agency",
        "subject": "خدمة جديدة لعملائكم — إيراد إضافي بدون تكلفة تشغيل",
        "body": """السلام عليكم فريق Digital8،

أنا سامي من Dealix. أنتم وكالة رقمية — يعني تديرون حملات لعملاء.

المشكلة المتكررة: العميل يدفع على الإعلانات لكن يلوم الوكالة لما الـ leads ما تتحول. السبب مو الإعلان — السبب بطء المتابعة.

Dealix يحل هذا: يرد على leads عملائكم خلال 45 ثانية بالعربي، يؤهل، ويحجز مواعيد.

تقدمونه كخدمة جديدة: Setup 3,000 ريال + 990/شهر لكل عميل. هذا إيراد جديد لكم + عميل سعيد ما يطلع.

Pilot مجاني لأول عميل عندكم. 7 أيام.

10 دقائق نتكلم؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، متابعة. لو عندكم عميل واحد يعاني من متابعة leads — نجربه مجاناً. وش رأيكم؟",
        "followup_5d": "آخر متابعة — وكالات ثانية بدأت تبيع Dealix كخدمة إضافية. مهتمين بالتفاصيل؟ أرسلوا 'مهتم'.",
        "fit_score": 90,
        "risk_score": 5,
    },
    {
        "company": "Floward",
        "contact_name": "فريق Floward",
        "contact_email": "b2b@floward.com",
        "contact_phone": "",
        "channel": "email",
        "sector": "logistics",
        "subject": "طلبات الشركات اللي ما تُتابع — كل واحد = إيراد ضائع",
        "body": """السلام عليكم فريق Floward،

أنا سامي من Dealix. عندكم قسم طلبات الشركات (B2B) — هدايا موظفين، مناسبات، عملاء VIP.

هالطلبات تحتاج متابعة سريعة: الشركة تبي عرض سعر لـ 50 باقة قبل المناسبة. كل ساعة تأخير = احتمال يطلب من المنافس.

Dealix يستقبل الطلب فوراً بالعربي، يسأل عن العدد والميزانية والتاريخ، ويعطي تقدير أولي. فريقكم يستلم طلب مؤهّل جاهز.

990 ريال/شهر. Pilot 7 أيام بـ 499 ريال مع ضمان استرداد.

وقتكم 10 دقائق؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، متابعة. كل طلب B2B ما يُتابع = إيراد يروح. Dealix يرد فوراً. مهتمين؟",
        "followup_5d": "آخر متابعة — أرسلوا 'demo' لو تبون تشوفون كيف يشتغل مع طلبات الشركات.",
        "fit_score": 78,
        "risk_score": 8,
    },
    {
        "company": "Sary",
        "contact_name": "فريق ساري",
        "contact_email": "info@sary.sa",
        "contact_phone": "",
        "channel": "email",
        "sector": "logistics",
        "subject": "طلبات التجار اللي تضيع — حل رد فوري",
        "body": """السلام عليكم فريق ساري،

أنا سامي من Dealix. أنتم أكبر منصة B2B supply بالسعودية — يعني volume كبير من طلبات التجار.

المشكلة عند منصات B2B: التاجر يبي رد سريع على الأسعار والتوفر. كل طلب ما يُتابع = التاجر يطلب من مورد ثاني.

Dealix يستقبل طلبات التجار فوراً بالعربي، يسأل عن المنتج والكمية، ويعطي تقدير أولي. يحفظ 40% من الطلبات الضائعة.

990 ريال/شهر. Pilot 7 أيام بـ 499 ريال.

10 دقائق نتكلم؟

سامي عسيري
مؤسس Dealix
dealix.me

إذا ما يناسبكم، اكتبوا 'إيقاف' ولن نتواصل مرة ثانية.""",
        "followup_2d": "السلام عليكم، متابعة. حجم طلباتكم كبير — Dealix يضمن ما يضيع منها شي. مهتمين بـ pilot؟",
        "followup_5d": "آخر متابعة — أرسلوا 'demo' لو تبون تشوفون Dealix يشتغل.",
        "fit_score": 75,
        "risk_score": 10,
    },
]


async def seed():
    """Insert drafts directly into DB."""
    os.environ.setdefault("DATABASE_URL", "")
    from app.database import async_session, init_db
    from app.models.outreach_draft import OutreachDraft
    import uuid
    from datetime import datetime, timezone

    await init_db()

    async with async_session() as session:
        batch_id = f"founder_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        for item in BATCH:
            draft = OutreachDraft(
                id=uuid.uuid4(),
                company=item["company"],
                contact_name=item["contact_name"],
                contact_email=item["contact_email"],
                contact_phone=item.get("contact_phone", ""),
                channel=item["channel"],
                subject=item["subject"],
                body=item["body"],
                followup_2d=item["followup_2d"],
                followup_5d=item["followup_5d"],
                sector=item["sector"],
                pain_hypothesis=f"sector:{item['sector']}",
                fit_score=item["fit_score"],
                risk_score=item["risk_score"],
                status="draft",
                approval_required=True,
                batch_id=batch_id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(draft)
        await session.commit()
        print(f"✅ Seeded {len(BATCH)} drafts — batch_id: {batch_id}")
        print(f"   Companies: {', '.join(d['company'] for d in BATCH)}")
        print(f"\n   Next: GET /api/v1/drafts?status=draft to review")
        print(f"         POST /api/v1/drafts/approve-batch to approve")
        print(f"         POST /api/v1/drafts/send-approved-batch to send")


if __name__ == "__main__":
    asyncio.run(seed())
