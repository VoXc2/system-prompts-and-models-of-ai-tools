# Dealix — Full Ops Growth Max System

## Mission
نظام اختراق سوق كامل عبر 5 قنوات بالتوازي. الهدف: أول 3 عملاء يدفعون خلال 21 يوم.

---

## 8 طبقات النمو

### Layer 1 — Market Intelligence

**القطاعات المستهدفة (بالأولوية):**

| الأولوية | القطاع | الألم | حجم الفرصة | سهولة الوصول |
|----------|--------|-------|-----------|-------------|
| P0 | وكالات تسويق | عملاؤهم يخسرون leads بعد الإعلان | عالي (multiplier) | LinkedIn + Email |
| P0 | عقارات | 150+ استفسار/شهر، 60% ما يُتابع | 300K ريال/سنة ضائعة | Email + WhatsApp |
| P0 | عيادات/خدمات | حجوزات ضائعة من واتساب | مباشر | WhatsApp |
| P0 | SaaS سعودي | leads من الموقع تبرد | مباشر | Email |
| P0 | e-commerce | استفسارات واتساب ما تُتابع | مباشر | Email |
| P1 | مقاولات | طلبات أسعار بدون متابعة | متوسط | Email |
| P1 | تدريب | استفسارات دورات ضائعة | متوسط | Email |
| P1 | توظيف | مرشحين ما يُتابعون | متوسط | LinkedIn |
| P2 | Enterprise | multi-branch / high-volume | كبير | Referral |

**Buyer Personas:**

| Persona | الألم | الـ Hook | العرض |
|---------|-------|---------|-------|
| مؤسس صغير (1-10 موظفين) | يرد بنفسه على العملاء | "وقتك أغلى من الرد على استفسارات" | Pilot 499 |
| مدير مبيعات | فريقه ما يلحق | "الفريق يركّز على الصفقات الكبيرة" | Starter 990 |
| صاحب وكالة | عملاؤه يشتكون من المتابعة | "خدمة جديدة تبيعها + إيراد إضافي" | Partner 20% |
| مدير تسويق | يصرف على إعلانات والـ leads تضيع | "حافظ على ROI حملاتك" | Pilot 499 |
| مؤسس SaaS | SDR مكلّف + leads تبرد | "3 SDRs بسعر 1" | Starter 990 |

**Trigger Events (إشارات شراء):**
1. الشركة فتحت وظيفة SDR/مبيعات → يحتاجون مساعدة
2. الشركة أطلقت حملة إعلانية جديدة → leads بتزيد
3. الشركة توسّعت لمدينة جديدة → فريق صغير + استفسارات كثيرة
4. مؤسس يشتكي على LinkedIn من ضغط العملاء
5. وكالة خسرت عميل → تبحث عن خدمات إضافية
6. شركة غيّرت CRM → فرصة integration

---

### Layer 2 — Targeting Engine

**نموذج التسجيل:**
```
total_score = urgency(1-5) + fit(1-5) + access(1-5) + partner(1-5)
```
- 16-20: أرسل اليوم
- 12-15: أرسل هذا الأسبوع
- 8-11: أرسل هذا الشهر
- 4-7: backlog

**Channel Choice Logic:**
- warm network → WhatsApp
- agencies → Email + LinkedIn DM
- real estate → Email
- SaaS → Email
- clinics/services → WhatsApp
- e-commerce → Email + Instagram

---

### Layer 3 — Content Engine

**المنصات:**
| المنصة | النوع | التكرار | الهدف |
|--------|-------|---------|-------|
| LinkedIn | بوستات مؤسس | يومياً | authority + inbound |
| X/Twitter | تغريدات + threads | يومياً | reach + discovery |
| Instagram | carousels + reels + stories | 3x/أسبوع | visual trust + local |
| WhatsApp Status | updates | يومياً | warm network awareness |

**أنواع المحتوى (rotate):**
1. مشكلة → إحصائية
2. حل → بدون بيع مباشر
3. قصة مؤسس
4. ROI calculation
5. نصيحة عملية
6. case study / نتيجة
7. عرض شراكة
8. سؤال تفاعلي

---

### Layer 4 — Direct Outreach Engine

**القنوات بالتوازي:**

| القناة | الهدف اليومي | النوع | الأمان |
|--------|-------------|-------|--------|
| Warm WhatsApp | 3-5 | رسالة شخصية | آمن — أشخاص يعرفهم سامي |
| Email | 5-7 | sector-specific | آمن — targeted + opt-out |
| LinkedIn DM | 3 max | manual only | آمن — NO bots |
| X reply/DM | 2-3 | engagement-based | آمن — بعد تفاعل |
| Instagram DM | 1-2 | inbound reply only | آمن — بعد تفاعل |

**Sequence لكل قناة:**
1. أول رسالة: value + pain + pilot offer
2. Follow-up +2 يوم: "شفت رسالتي؟" + value add
3. Follow-up +5 أيام: case study أو insight
4. Final +10 أيام: "آخر متابعة — مهتم أو إيقاف؟"

---

### Layer 5 — Conversion Engine

**مسار التحويل:**
```
رسالة → رد → تأهيل → demo (10 دقائق) → pilot (499) → starter (990/شهر)
```

**CTAs حسب المرحلة:**
| المرحلة | CTA |
|---------|-----|
| أول تواصل | "15 دقيقة أوريك النظام — calendly link" |
| بعد اهتمام | "نسوي pilot 7 أيام بـ 499 ريال — ضمان استرداد" |
| بعد demo | "رابط الدفع: [checkout link]" |
| بعد pilot ناجح | "نحوّلك لـ starter بـ 990/شهر" |
| شريك | "20% من كل عميل تحوّله" |

---

### Layer 6 — Revenue Ops

**Trackers يومية:**
→ ملف `DAILY_REVENUE_SCORECARD.md`
→ ملف `FIRST_20_TARGETS.md`

**مسار الإيراد:**
```
يوم 1-7: 50 رسالة → 5 ردود → 2 demos
يوم 8-14: 100 رسالة تراكمي → 10 ردود → 4 demos → 1 pilot
يوم 15-21: 150 رسالة → 15 رد → 6 demos → 3 pilots
```

**الإيراد المتوقع (حد أدنى):**
- 3 pilots × 499 = 1,497 ريال
- 1 starter conversion × 990 = 990 ريال
- 1 partner referral × 499 = 499 ريال
- **شهر 1 = ~3,000 ريال**

---

### Layer 7 — Compliance Guardrails

→ ملف `SAFE_OUTBOUND_POLICY.md` (تفصيل كامل)

**الملخص:**
- ❌ لا scraping لأي منصة
- ❌ لا بوتات رسائل
- ❌ لا spam أرقام عشوائية
- ❌ لا ادعاءات كاذبة
- ✅ manual + AI-assisted drafting
- ✅ opt-out في كل رسالة
- ✅ stop فوري عند "إيقاف"
- ✅ max 10-15 رسالة/يوم بالبداية

---

### Layer 8 — Learning Loop

**أسبوعياً (كل أحد):**
1. أي رسالة حققت أعلى reply rate? → كرّرها
2. أي قناة حققت أعلى demos? → زد الجهد فيها
3. أي قطاع حقق أعلى conversion? → ركّز عليه
4. أي رسالة ما جابت نتيجة? → أوقفها
5. حدّث ICP بناءً على البيانات

---

## الروتين اليومي الدقيق

### الصباح (8:00 - 9:00)
- [ ] شيك الردود (email + WhatsApp + LinkedIn + X)
- [ ] صنّف كل رد (مهتم/سعر/demo/لا/اعتراض/شريك)
- [ ] احجز أي demo فوراً
- [ ] حدّث scorecard

### كتلة الـ Outreach (9:00 - 11:00)
- [ ] انشر LinkedIn post
- [ ] انشر X tweet/thread
- [ ] أرسل 5 warm WhatsApp (أو email)
- [ ] أرسل 5 targeted emails
- [ ] علّق على 5 بوستات LinkedIn ذات صلة
- [ ] رد على 5 tweets ذات صلة

### الظهر (2:00 - 3:00)
- [ ] أرسل 5 follow-ups
- [ ] نفّذ أي demo محجوز
- [ ] أرسل payment link لأي interested
- [ ] تواصل مع وكالة/شريك واحد

### المساء (8:00 - 9:00)
- [ ] حدّث scorecard
- [ ] جهّز Instagram story/carousel
- [ ] حدّث WhatsApp Status
- [ ] خطّط أهداف بكرا

---

## 12 زاوية استهداف مبتكرة

1. **Missed Lead Pain**: استهدف شركات ترد ببطء على العملاء
2. **Agency Multiplier**: الوكالة تبيع Dealix لـ 10 عملاء = 10x
3. **Founder Overload**: مؤسسين يردون بأنفسهم على الاستفسارات
4. **Campaign Leakage**: مسوقين يصرفون على إعلانات والـ leads تضيع بعد الكلك
5. **WhatsApp Chaos**: شركات واتسابها مليان بدون CRM
6. **Arabic Follow-up**: ميزة تنافسية — الرد بالعربي السعودي مو فصحى
7. **Pilot Wedge**: 499 ريال + ضمان = صفر مخاطرة
8. **Speed-to-Lead Audit**: عرض مجاني "كم تاخذون وقت ترردون؟"
9. **Partner Service Exchange**: الوكالة تسوّق، Dealix يفعّل = تبادل
10. **Content-to-Demo Loop**: بوست LinkedIn → تعليق → DM → demo
11. **Sector-Specific Hooks**: كل قطاع له ألم مختلف وhook مختلف
12. **Reply Classification**: كل رد يتحوّل لـ action تلقائياً

---

## المراجع

| الملف | المحتوى |
|-------|---------|
| `FIRST_20_TARGETS.md` | أول 20 هدف مع scoring |
| `DAILY_REVENUE_SCORECARD.md` | tracker يومي |
| `PLATFORM_PLAYBOOK_LINKEDIN.md` | LinkedIn كامل |
| `PLATFORM_PLAYBOOK_X.md` | X/Twitter كامل |
| `PLATFORM_PLAYBOOK_INSTAGRAM.md` | Instagram كامل |
| `PLATFORM_PLAYBOOK_WHATSAPP.md` | WhatsApp كامل |
| `EMAIL_OUTREACH_SYSTEM.md` | email sequences |
| `PARTNER_AGENCY_ACQUISITION.md` | شراكات وكالات |
| `CONTENT_CALENDAR_30_DAYS.md` | تقويم 30 يوم |
| `SAFE_OUTBOUND_POLICY.md` | سياسة أمان |
| `LINKEDIN_30_POSTS.md` | 30 بوست جاهز |
| `AGENCY_PARTNER_PITCH.md` | عرض الشراكة |
