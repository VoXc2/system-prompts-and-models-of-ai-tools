# DEALIX — لوحة التحكم الكاملة
# افتح هذا الملف كل صباح. نفّذ بالترتيب. لا تتخطى.

---

## الحالة الحالية

- GitHub: **213 ملف / 31,712 سطر** — كامل ومدموج في main
- Backend: FastAPI + 100+ endpoint + DLQ + PostHog + Circuit Breaker + Pricing
- Frontend: Landing + Dashboard + Trial Signup
- Lead Machine: 60 هدف سعودي مسمّى + رسائل جاهزة
- Revenue Kit: pricing + pilot offer + payment flow + onboarding
- Tests: 26/26 D0 + 6/6 fault injection
- Railway: يحتاج env vars + deploy
- Moyasar: يحتاج KYC/key fix
- Outreach: 0 رسائل مرسلة

---

## خطوة 1: شغّل السيرفر (10 دقائق — مرة وحدة)

افتح https://railway.com → مشروع dealix

**أ) أضف PostgreSQL:**
+ New → Database → PostgreSQL → ينشأ DATABASE_URL تلقائي

**ب) أضف Redis:**
+ New → Database → Redis → ينشأ REDIS_URL تلقائي

**ج) أضف هذي المتغيرات في service "web" → Variables:**
```
ENVIRONMENT=production
SECRET_KEY=أي_نص_عشوائي_64_حرف
APP_NAME=Dealix
LLM_PRIMARY_PROVIDER=groq
GROQ_API_KEY=مفتاحك_من_console.groq.com
EXPOSE_OPENAPI=true
MARKETING_STATIC_ENABLED=false
SELF_IMPROVEMENT_INTERVAL_SECONDS=9999
```

**د) Deploy** → انتظر 90 ثانية

**هـ) اختبر:**
افتح المتصفح → `https://اسم-railway.up.railway.app/health`
لو رجع `{"status":"ok"}` → السيرفر شغّال

---

## خطوة 2: أرسل أول 5 رسائل (30 دقيقة — اليوم)

### واتساب (أسرع طريقة — الأفضل تبدأ فيها):

افتح واتساب → أرسل لـ **5 أشخاص تعرفهم** يملكون business:

```
السلام عليكم [الاسم]،

أطلقت Dealix اليوم — AI sales rep بالعربي الخليجي
يرد على leads الشركات خلال 45 ثانية، يؤهّلهم، ويحجز demos.

أبحث عن 3 أصدقاء عندهم business حقيقي لتجربة
pilot بـ 1 ريال لمدة 7 أيام.

فكرت فيك لأن [سبب محدد].

مهتم نتكلم 10 دقائق الآن؟
```

### LinkedIn (بالتوازي):

افتح https://www.linkedin.com/in/abdullahalassiri/

أرسل Connect + Note:

```
السلام عليكم عبدالله،

أنا سامي، أشتغل على Dealix — مندوب مبيعات AI بالعربي
للشركات اللي عندها leads كثيرة وتحتاج تأهيل وحجز أسرع.

أبي أوريك تجربة 20 دقيقة على سيناريو قريب من Lucidya.

يناسبك بكرة 11 ص أو 3 م؟
calendly.com/sami-assiri11/dealix-demo
```

---

## خطوة 3: انشر أول بوست (5 دقائق — اليوم)

افتح LinkedIn → New Post → الصق:

```
أطلقنا Dealix 🚀

Dealix هو مندوب مبيعات AI بالعربي للشركات اللي عندها
leads كثيرة وتحتاج رد أسرع وتأهيل أفضل.

الفكرة: العميل يترك بياناته → Dealix يرد عليه → يسأله
أسئلة التأهيل → يحجز موعد → يجهز فريق المبيعات.

نبدأ بـ pilot يدوي لأول الشركات.

إذا عندك leads تضيع بسبب بطء الرد، أقدر أوريك
تجربة 20 دقيقة:

🌐 dealix.me
📅 calendly.com/sami-assiri11/dealix-demo

#SaudiSaaS #AI #Sales #ArabicAI #BuildInPublic
```

---

## خطوة 4: لما أحد يرد (جاهز)

### لو قال "كم السعر؟":
```
نبدأها كـ pilot بسيط لمدة 7 أيام.
نجرب Dealix على 10–25 lead، ونقيس النتائج.
499 ريال فقط — مع ضمان استرداد كامل لو ما عجبك.
```

### لو قال "عندنا CRM":
```
ممتاز، Dealix ما يستبدل الـ CRM.
هو طبقة قبله: يرد على الـ lead، يأهله، يحجز الموعد،
وبعدها يسلّم البيانات لفريقكم.
```

### لو قال "أبي أجرب":
```
تمام! أرسل لك رابط الدفع (499 ريال / 7 أيام).
بعد التأكيد نبدأ الإعداد خلال 4 ساعات.

الدفع:
- تحويل بنكي: [رقم حسابك]
- STC Pay: [رقمك]
```

### لو قال "لا مهتم":
```
تمام، شكراً على وقتك.
هل تعرف أحد ممكن يستفيد؟ 10% من أول سنة لك.
```

---

## خطوة 5: أول عميل يدفع (اليوم أو خلال أسبوع)

**عند الدفع:**
1. تأكد من إثبات الدفع (screenshot تحويل)
2. ابدأ onboarding خلال 4 ساعات
3. اجمع: اسم الشركة، قطاع، مصدر الليدز، رقم واتساب، أسئلة التأهيل
4. ابدأ رد يدوي على أول 10 leads
5. أرسل تقرير يومي مختصر
6. بعد 7 أيام: حوّله لـ Starter (990 ريال/شهر)

---

## الجدول اليومي (كل يوم حتى أول 10 عملاء)

```
08:00  تحقق من الردود
09:00  أرسل 10 LinkedIn DMs
10:00  أرسل 5 واتساب warm
11:00  Demo لو محجوز
12:00  Follow-ups
14:00  5 رسائل وكالات
16:00  انشر 1-2 بوست
17:00  3 referral asks
20:00  ردود متأخرة + scorecard
```

---

## الأرقام المستهدفة

| الأسبوع | رسائل | ردود | demos | pilots | مدفوع | MRR |
|---------|-------|------|-------|--------|-------|-----|
| 1 | 50 | 5 | 1 | 1 | 0 | 0 |
| 2 | 100 | 10 | 3 | 2 | 1 | 990 |
| 3 | 150 | 15 | 5 | 3 | 3 | 2,970 |
| 4 | 200 | 25 | 8 | 5 | 5 | 4,950 |

---

## الملفات المهمة على GitHub

| الملف | الغرض |
|-------|--------|
| `docs/ops/DAILY_REVENUE_MACHINE.md` | 8 قنوات إيراد + جدول يومي |
| `docs/ops/lead_machine/SAUDI_60_TARGETS.md` | 60 هدف مسمّى + رسائل |
| `docs/ops/10_CUSTOMERS_PER_WEEK_MACHINE.md` | خطة 10 عملاء/أسبوع |
| `revenue-activation/FIRST_3_CLIENTS_PLAN.md` | خطة أول 3 عملاء |
| `revenue-activation/sales-pack/ONE_PAGER.md` | ملخص صفحة واحدة |
| `docs/customer_learnings/pilot_agreement_template.md` | عقد pilot |
| `docs/customer_learnings/pricing_discovery.md` | بحث التسعير |
| `RUNBOOK.md` | 5 سيناريوهات طوارئ |
| `SLO.md` | أهداف الأداء |
| `LAUNCH_GATES.md` | 33 gate checklist |
| `landing/trial-signup.html` | صفحة تسجيل عربية |

---

## قاعدة ذهبية

**لا تبني أكثر. ابدأ أبيع.**

كل شي تقني جاهز. الشي الوحيد اللي ينقص = أول SENT.
