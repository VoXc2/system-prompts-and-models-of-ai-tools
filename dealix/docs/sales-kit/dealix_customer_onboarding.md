# 🎉 Dealix — Customer Onboarding Playbook

**للتطبيق:** يوم توقيع العميل على pilot/عقد
**المدة:** 7-14 يوم من التوقيع إلى "first value"
**الهدف:** عميل يرى نتيجة ملموسة خلال أسبوع = احتفاظ عالٍ

---

## 📐 فلسفة الـ Onboarding

**قاعدة الـ 7 أيام:**
لو العميل لم يرَ قيمة ملموسة خلال أسبوع من التوقيع، احتمال الـ churn بعد 3 شهور = 80%.
لو رأى قيمة → 85% يصبح عميلاً دائماً.

**كل شي يُقاس بـ "first value moment":**
- أول lead يتأهل تلقائياً
- أول demo يُحجز بدون تدخل بشري
- أول ساعة BDR محرّرة

اجعل هذا يحدث **خلال 72 ساعة من التوقيع**.

---

## 🗓️ خطة الـ 14 يوم

### يوم 0 — التوقيع

**من Dealix (أنا):**
- [ ] إرسال welcome email خلال ساعة من التوقيع
- [ ] إرسال Calendly link لـ kick-off call (خلال 24 ساعة)
- [ ] إضافة العميل لـ "Active Customers" في CRM
- [ ] تحضير workspace مخصص في Dealix dashboard

**Welcome Email Template:**
```
الموضوع: أهلاً بك في Dealix — لنبدأ خلال 24 ساعة

[الاسم]،

مبروك على الخطوة! Dealix الآن جاهز لبدء العمل لـ [اسم شركتك].

الخطوات التالية:
1️⃣ احجز kick-off call (30 دقيقة): [Calendly link]
2️⃣ أكمل نموذج setup السريع: [link]
3️⃣ احضّر access لـ [CRM name] + موقع الشركة

خلال 72 ساعة من الآن:
✅ Dealix يستقبل أول lead حقيقي
✅ تشاهد أول conversation
✅ تقرر: هل هذا يستحق؟

متوفر 24/7 على WhatsApp: [رقمك]

سامي
```

### يوم 1 — Kick-off Call (30 دقيقة)

**Agenda دقيقة بدقيقة:**

**0-5 دقيقة:** Rapport + شكر
- "شكراً على الثقة. اليوم نرسي الأسس — بعد 30 دقيقة يكون عندك Dealix جاهز للعمل."

**5-15 دقيقة:** Discovery عميق
- "أخبرني أكثر عن أنواع leads اللي تأتي لك"
- "ما معلومات BANT اللي تريد الـ AI يجمعها؟"
- "أي leads يجب رفضها فوراً؟ (مثل: طلاب، competitors)"
- "لو حدّدت 3 shortcuts للـ BDR team، ما هي؟"

**15-25 دقيقة:** التخصيص
- Share screen → Dealix admin panel
- معاً، نضبط:
  - Tone of voice (formal/casual)
  - Qualification questions (8 max)
  - Booking calendar integration
  - CRM sync

**25-30 دقيقة:** الخطوات التالية
- "خلال 48 ساعة: أشحن 10 test leads. راجعها وأرسل feedback."
- "يوم 5: نُفعّل على 20% من leads الحقيقية"
- "يوم 7: تقرير أسبوع أول + قرار — نكمل أم نعدّل؟"

### يوم 2 — Technical Setup

**Integration checklist:**
- [ ] CRM webhook مُثبّت + tested
- [ ] Calendar integration (Calendly/Google)
- [ ] WhatsApp Business API (إذا طُلب)
- [ ] Analytics pixel (Dealix sends events)
- [ ] Branding (logo, colors in chat widget)
- [ ] Custom domain (chat.customer.com → dealix)

**Email بعد Setup:**
```
الموضوع: Setup مُكتمل — 10 test leads قادمة خلال ساعة

[الاسم]،

Dealix الآن مُتصل بـ [CRM]. إليك ما حصل:

✅ Webhook integration tested
✅ أسئلة التأهيل: [عرض القائمة]
✅ Calendar sync: [التاريخ]
✅ 10 test leads تُحقن خلال ساعة للمراجعة

راجعها في dashboard.dealix.ai (login attached).

أنتظر feedback يوم 3.

سامي
```

### يوم 3 — Review Test Leads

**اجتماع: 15 دقيقة (async محتمل)**

**الأسئلة للعميل:**
1. جودة الإجابات — هل التعامل طبيعي؟
2. أسئلة التأهيل — هل تكفي؟
3. التصنيف — تتفق مع تقييم Dealix؟

**إذا كل شي OK → شحن 20% من leads الحقيقية**
**إذا في مشاكل → تعديلات محددة، إعادة test**

### يوم 4 — Team Training Call (60 دقيقة)

**الحضور:**
- BDRs
- Sales managers
- RevOps (إذا موجود)

**Agenda:**

**0-10:** كيف يعمل Dealix في خلفيتك
- flow من lead لـ demo
- كيف تقرأ الـ briefs

**10-30:** Live demo على بيانات حقيقية
- leads test تم جمعها يوم 2
- اقرأ معهم — هذا lead A vs B vs C ليش؟

**30-45:** Hand-off process
- "لما Dealix يحجز demo، أنت تستقبل notification في Slack"
- "قبل الـ demo بـ 10 دقائق، افتح الـ brief"
- "الـ brief يحتوي: الاسم، الشركة، use case، budget range"

**45-60:** Q&A + مخاوف

### يوم 5 — Full Rollout

- 100% من leads → Dealix
- BDRs يستقبلون فقط leads فئة A
- Sales managers يستقبلون dashboard يومي

**Monitoring:**
- فحص كل ساعة لأول 24 ساعة
- أي escalation → رد خلال 10 دقائق

### يوم 6 — Mid-week Check-in (15 دقيقة)

**الأسئلة:**
- "أي surprise سلبي خلال 24 ساعة؟"
- "أي lead عدّل Dealix تصنيفه خطأ؟"
- "هل BDRs راضين عن جودة الـ briefs؟"

### يوم 7 — Week 1 Review (30 دقيقة)

**Dashboard متضمّن:**
- كم lead دخل
- % تأهّل (vs قبل)
- Demos محجوزة
- ساعات BDR موفّرة (vs baseline)
- NPS من BDRs (1-10)

**قرار:**
- ✅ نكمل + نزيد scope → commit للـ Starter/Growth/Scale الشهري
- 🟡 تعديلات + أسبوع آخر من pilot (بدون تكلفة)
- ❌ إلغاء — استرداد كامل + export بيانات

---

## 📊 KPIs للـ Onboarding

| المؤشر | الهدف | التنبيه |
|---------|-------|---------|
| Time to first lead | < 72 ساعة | > 5 أيام |
| Training attendance | 100% | < 70% |
| Setup call rating | ≥ 8/10 | < 7 |
| First week qualification rate | > 25% | < 15% |
| BDR NPS | ≥ 7 | < 5 |

**إذا أي KPI في منطقة "تنبيه" → escalate إلى founder (أنت) مباشرة.**

---

## 🎯 أول 30 يوم — Retention Playbook

### أسبوع 2: تعميق
- Weekly metrics email (تلقائي)
- Check-in call (30 دقيقة)
- جمع feedback عن missing features

### أسبوع 3: توسيع
- Introduce advanced features (custom workflows)
- A/B test مختلف qualification questions
- Share industry benchmarks

### أسبوع 4: تجديد
- Monthly business review (60 دقيقة)
- ROI report (formal)
- Expansion conversation (إذا النتائج ممتازة)

---

## 🔔 إشارات خطر Churn

### أخضر (صحي):
- ✅ login أسبوعي
- ✅ استجابة للـ emails خلال 3 أيام
- ✅ tickets ≤ 2 أسبوعياً
- ✅ NPS ≥ 8

### أصفر (انتبه):
- ⚠️ no login لـ 10 أيام
- ⚠️ no response لـ email ≥ 7 أيام
- ⚠️ NPS 5-7
- ⚠️ billing disputes

**عند الأصفر:** founder يتصل مباشرة خلال 48 ساعة.

### أحمر (خطر):
- 🔴 no login لـ 21 يوم
- 🔴 cancellation request
- 🔴 team downsizing من العميل
- 🔴 NPS < 5

**عند الأحمر:**
1. Emergency call خلال 24 ساعة
2. "Save" offer (2 شهر مجاني + feature request prioritized)
3. إذا رفض → exit interview مفصّل

---

## 📧 Email Cadence للعميل الجديد

| اليوم | الموضوع | الهدف |
|------|----------|--------|
| 0 | Welcome + kick-off booking | معلومات + commitment |
| 2 | Test leads ready | engagement |
| 3 | Review feedback needed | participation |
| 5 | Full rollout live | excitement |
| 7 | Week 1 results | validation |
| 14 | Month 1 halfway check | retention |
| 28 | Month 1 review + renewal | expansion |
| 45 | Feature showcase | education |
| 60 | Q1 roadmap preview | loyalty |
| 90 | Quarterly business review | strategic |

---

## 🏆 Success Metrics — أول 3 شهور

**هدف Dealix لكل عميل:**
- شهر 1: Break-even بالوقت المُوفّر
- شهر 2: 2X ROI
- شهر 3: Case study ready للنشر (بموافقة العميل)

**تتبّع:**
- Weekly: usage metrics
- Monthly: ROI calculation
- Quarterly: NPS + renewal probability

---

## 💡 قاعدة ذهبية

**"أول عميل هو الأهم في تاريخ Dealix."**

اقضِ 10 ساعات أسبوعياً على أول عميل لمدة شهر. هذا:
- يضمن نجاحه (احتفاظ)
- يعلّمك ماذا يحتاج السوق
- يبني أول case study
- ينتج أول referral

**بعد أول 3 عملاء ناجحين:** أنت جاهز للتوسع.
