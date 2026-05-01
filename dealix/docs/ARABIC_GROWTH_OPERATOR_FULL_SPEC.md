# Arabic Growth Operator — Full Spec

> **الرؤية:** Dealix ليس CRM ولا أداة WhatsApp ولا بوت رسائل. هو **Saudi Autonomous Revenue OS**: بوت عربي ذكي داخل WhatsApp/الداشبورد يفهم الشركة، السوق السعودي، الأرقام المرفوعة من العميل، الشراكات، الاجتماعات، المتابعة، الدفع، والامتثال — ويقترح وينفذ بموافقة واضحة.
> **آخر تحديث:** 2026-05-01
> **حالة الكود:** ✅ مبني، 50/50 unit tests خضراء على Python 3.10 venv

---

## 1. الجملة المحورية

> **Dealix هو مدير نمو عربي ذكي للشركات السعودية:
> يعرف من تستهدف، ماذا تقول، متى تتابع، من تشارك، وكيف تثبت أن كل هذا جاب نتيجة.**

---

## 2. تجربة WhatsApp مثل Boardy لكن أقوى

**Boardy** يقترح علاقات.
**Dealix** يقترح علاقات + leads + رسائل + اجتماعات + مدفوعات + proof + revenue.

كل بطاقة في الـ feed:
- **Why now** ولماذا الآن تحديداً
- **Recommended action** بعربي طبيعي
- **3 buttons فقط** (حد WhatsApp Reply Buttons): قبول / تخطي / رسالة
- لو ضغط "رسالة" → يدخل draft mode: اعتماد / تعديل / إلغاء

---

## 3. أنواع العملاء التي تخدمهم

| النوع | كيف يخدمه Dealix |
|---|---|
| **صاحب الشركة** | daily brief 3 قرارات صباحاً، قرار مطلوب feed، Proof Pack أسبوعي |
| **مدير المبيعات** | deals at risk، reps slow follow-up، messages to approve، forecast، coaching |
| **متجر / SMB** | تصنيف العملاء VIP/inactive/repeat/leads، حملات استرجاع، payment links، عروض موسمية |
| **مؤسس فردي** | First 10 Customers Autopilot، Personal Operator، Strategic Board Brief |
| **وكالة تسويق** | reseller / revenue share + سياسة موافقات لكل عميل |

---

## 4. استخدام الأرقام المرفوعة من العميل

> **القاعدة الذهبية:** الأرقام لازم تكون مملوكة/مصرّح بها أو عندها علاقة مناسبة. لا cold WhatsApp بدون lawful basis.

العميل يرفع ملف:

```text
name, phone, company, city, sector, source, relationship_status,
opt_in_status, last_contacted_at, notes
```

ثم Dealix يعمل تلقائياً:

1. **normalize_phone** — تطبيع للأرقام السعودية (E.164)
2. **dedupe_contacts** — إزالة التكرار، الإبقاء على السجل الأغنى
3. **classify_contact_source** — existing / inbound / event / referral / old_lead / cold / unknown
4. **detect_opt_out** — إشارات الـ opt-out بالعربي + الإنجليزي
5. **score_contactability** — `safe / needs_review / blocked` مع أسباب عربية واضحة
6. **summarize_import** — ملخص مرئي يطلع للعميل

### المخرج للعميل
```text
رفعت 1,000 رقم.
- 420 آمن للتواصل
- 180 يحتاج مراجعة
- 90 opt-out أو ممنوع
- 310 غير واضح المصدر
أقترح نبدأ فقط بـ 420 رقم الآمنة.
[اعرض العينة] [جهز الرسائل] [احذف غير الآمن]
```

---

## 5. Contactability + opt-in

### القرارات الـ 3
- **safe**: علاقة قائمة (existing/inbound/referral) + رقم صالح + ليس opt-out
- **needs_review**: مصدر غير واضح / lead قديم بدون last_contacted_at
- **blocked**: opt-out / cold WhatsApp بدون lawful basis / رقم غير صالح

### قاعدة WhatsApp الافتراضية
```text
لا cold WhatsApp بدون lawful basis (PDPL م.5).
السياسة: لا cold WhatsApp افتراضياً.
```

العميل يقدر يعدل القاعدة لكل قائمة بعد توثيق المصدر، لكن الأمر الافتراضي هو **الحماية**.

---

## 6. WhatsApp Approvals

WhatsApp Reply Buttons محدودة بـ 3:

```text
[قبول] [تخطي] [رسالة]
```

لو ضغط "رسالة":

```text
[اعتماد] [تعديل] [إلغاء]
```

كل draft يخرج بـ:
- `approval_required: True`
- `approval_status: "pending_approval"`
- `guardrails_ar`: قائمة قواعد عربية واضحة

---

## 7. Gmail Drafts (لا إرسال مباشر)

- Endpoint يستخدم `gmail.compose` scope فقط
- ينشئ مسودة في صندوق المستخدم بـ label `DRAFT`
- المستخدم يضغط "Send" بنفسه من Gmail

---

## 8. Calendar Drafts (لا إنشاء مباشر)

- `build_calendar_draft()` يرجع dict مطابق لـ Google Calendar `events.insert` body
- `live_inserted: False` دائماً
- `conferenceDataVersion: 1` للحصول على Google Meet
- الـ insert الفعلي يحدث في خدمة منفصلة، فقط بعد:
  - موافقة OAuth صريحة من المستخدم
  - ضغط زر "أنشئ الاجتماع"

---

## 9. Payment Links (Moyasar)

- `build_moyasar_payment_link_draft()` يبني payload بصيغة Moyasar
- المبلغ بالـ halalas (1 SAR = 100)
- `live_charged: False` دائماً
- `POST /v1/payments` الفعلي يحدث في billing service

داخل المحادثة:

```text
الباقة المقترحة:
نظام النمو (Growth OS) — 2,999 ريال
[ادفع الآن]   [أرسل فاتورة]   [كلم المبيعات]
```

ضغط "ادفع الآن" → ينقل لـ Moyasar Hosted Checkout (PCI-safe)، **ليس** إدخال بطاقة داخل WhatsApp.

---

## 10. الشراكات

`suggest_partner_types()` يرجع 6 أنواع شركاء جاهزة:
- marketing_agency
- sales_consultant
- tech_integrator (Supabase / Make.com)
- crm_vendor (Zoho / Salla / Odoo سعودي)
- founder_community
- sector_influencer (عقار / صحة / لوجستيات)

كل نوع له: rationale_ar، model_ar (Reseller / Revenue share / Affiliate / Equity)، ideal_size.

`partner_scorecard()` يحسب: tier (platinum / gold / silver / bronze) من intros + deals + revenue share + age.

---

## 11. الاجتماعات

`build_meeting_agenda()` يخلق agenda سعودي مناسب:
- 15min → 4 فقرات
- 20-30min → 5 فقرات
- 45min+ → 6 فقرات (يشمل demo حي + ROI breakdown)

`build_post_meeting_followup()` ينتج draft شكر + ملخص + خطوة تالية.

---

## 12. Proof Pack

`build_weekly_proof_pack()` يولد تقرير أسبوعي:
- **Activity:** 10 أرقام (opportunities, drafts, sent, replies, meetings, proposals, deals)
- **Money:** Pipeline + Revenue + Multiple
- **Quality:** drafts خطرة محبوطة (PDPL gates) + leaks recovered + avg response
- **Best of:** أفضل subject + reply rate
- **Next week plan:** قائمة عربية ديناميكية بناءً على الأرقام

التقدير: A+ / A / B / C / D حسب pipeline / cost multiple + deals.

تصدير Markdown جاهز للإرسال للإدارة.

---

## 13. Growth Missions (6 مهمات outcome-shaped)

| ID | Title AR | Kill Metric | Endpoint |
|---|---|---|---|
| **first_10_opportunities** ⭐ | اطلع لي 10 فرص | ten_drafts_approved | `/api/v1/innovation/opportunities/ten-in-ten` |
| recover_stalled_deals | أنقذ الصفقات المتوقفة | stalled_deals_revived | `/api/v1/revenue-os/leaks` |
| partnership_sprint | ابدأ شراكات | partner_intros_replied | `/api/v1/growth-operator/partners/suggest` |
| safe_whatsapp_campaign | جهز حملة واتساب آمنة | safe_messages_drafted | `/api/v1/growth-operator/contacts/import-preview` |
| meeting_booking_sprint | احجز لي 3 اجتماعات | meetings_confirmed | `/api/v1/growth-operator/meetings/draft` |
| list_cleanup | ارفع قائمتي ونظفها | safe_contacts_extracted | `/api/v1/growth-operator/contacts/import-preview` |

**Kill feature:** `first_10_opportunities` — الميزة التي تبيع.

---

## 14. حدود البحث في السوق والسوشال

### المصادر المسموحة
- موقع الشركة + صفحات عامة
- Google Search / Maps (API مع keys)
- LinkedIn (API / يدوي مصرّح)
- X / Instagram / Facebook Graph API (بإذن العميل)
- Job boards / event pages / tender feeds
- CRM العميل + ملفاته + Google Sheets / Gmail / Calendar (بإذن)
- WhatsApp opt-in / inbound

### ما لا يُبنى أبداً
- Scraping مخالف
- تجاوز login
- DM تلقائي بدون موافقة
- جمع أرقام عشوائية
- تخزين PII غير ضرورية
- إرسال جماعي غير مصرح

> **اللغة الصحيحة في المنتج:**
> "Dealix يبحث في المصادر المصرح بها والمتاحة، ويحوّلها إلى فرص قابلة للمراجعة، ولا يرسل بدون موافقة."

---

## 15. القواعد الـ 12 الأساسية (Compliance)

1. **Client Growth Profile** — كل عميل له ملف، بدونه البوت عام
2. **Contactability Engine** — كل رقم/lead له decision
3. **WhatsApp Approval OS** — 3 buttons فقط، draft-first
4. **Lead Intelligence** — fit_score, intent_score, why_now, best_angle, risk
5. **Saudi Message Engine** — قصير، غير مبالغ، سبب واضح، طلب بسيط
6. **Objection-to-Action** — كل رد → action مع interpretation
7. **Meeting Operator** — agenda + draft + followup، بدون live insert
8. **Gmail Draft Operator** — `gmail.compose` فقط، draft مع label DRAFT
9. **Payment-in-Chat** — Moyasar payment link، لا بطاقات في WhatsApp
10. **Partnership Operator** — 6 أنواع + outreach + scorecard
11. **Proof Pack** — weekly evidence ضد churn
12. **Growth Missions** — outcome-shaped tasks (لا dashboard معقد)

---

## 16. ما يُنفَّذ الآن (في الكود)

✅ **مبني وعليه 50 unit test ناجحة:**

```
auto_client_acquisition/growth_operator/
├── __init__.py              # exports
├── client_profile.py        # ClientGrowthProfile + defaults
├── contact_importer.py      # normalize/dedupe/classify/opt_out/summarize
├── contactability.py        # safe/needs_review/blocked + reasons
├── targeting.py             # segment + rank + top-10 + why_now stub
├── message_planner.py       # Arabic drafts + followups + objections
├── partnership_planner.py   # types + outreach + scorecard
├── meeting_planner.py       # agenda + calendar draft + followup
├── payment_offer.py         # Moyasar payment link draft
├── proof_pack.py            # weekly proof pack
└── mission_planner.py       # 6 growth missions

api/routers/growth_operator.py     # 16 endpoints under /api/v1/growth-operator/
tests/unit/test_growth_operator.py  # 50 passing
```

### Endpoints الـ 16

```
POST /api/v1/growth-operator/contacts/import-preview
POST /api/v1/growth-operator/contactability/score
POST /api/v1/growth-operator/targets/top-10
POST /api/v1/growth-operator/messages/draft
POST /api/v1/growth-operator/messages/followup
POST /api/v1/growth-operator/messages/objection-response
POST /api/v1/growth-operator/partners/suggest
POST /api/v1/growth-operator/partners/outreach
POST /api/v1/growth-operator/partners/scorecard
POST /api/v1/growth-operator/meetings/draft
POST /api/v1/growth-operator/meetings/post-followup
POST /api/v1/growth-operator/payment-offer/draft
GET  /api/v1/growth-operator/missions
POST /api/v1/growth-operator/missions/{id}/run
GET  /api/v1/growth-operator/proof-pack/demo
POST /api/v1/growth-operator/profile
```

---

## 17. ما يُؤجَّل (بعد أول 10 عملاء)

❌ **لا تنفذ الآن:**
- Live WhatsApp send (نظل draft-first)
- Live Calendar `events.insert` (يحتاج OAuth + UI confirm)
- Live Moyasar charges (يحتاج billing service منفصل)
- Live LinkedIn / X / Instagram scraping
- Multi-tenant SSO
- Mobile app
- MCP gateway مفتوح
- Marketplace خارجي
- Local LLM infra

---

## 18. الجاهزية للتجربة (Beta)

| المعيار | الحالة |
|---|---|
| Unit tests | ✅ 527 passed (50 منها growth_operator + 477 موجودة) |
| AST + import sanity | ✅ كل الـ 13 ملف |
| Approval invariant | ✅ كل draft عنده `approval_required: True` |
| لا live charge / send | ✅ كل drafts فقط |
| PDPL guardrails | ✅ no cold WhatsApp by default |
| Arabic body content | ✅ كل القوالب عربية طبيعية |
| Endpoint coverage | ✅ 16 endpoint + 6 missions + Top-10 + Proof Pack |

**جاهز للـ private beta** بمجرد:
1. ربط Railway env vars
2. ربط Moyasar live keys
3. ربط WhatsApp Cloud / Green API
4. 10 شركات pilot

---

## 19. المقارنة الموجزة

| ضد | قوته | تميزنا |
|---|---|---|
| **Boardy** | اقتراح علاقات | علاقات + leads + رسائل + اجتماعات + payments + proof |
| **HubSpot** | عام، شامل | عربي، سعودي، WhatsApp-first، outcome-first |
| **Gong** | conversation intelligence | نبدأ من market signal → action، لا فقط analytics |
| **أدوات WhatsApp** | إرسال bulk | نقرر هل ترسل، ماذا، لمن، متى، آمن أم لا |
| **الوكالات** | تنفيذ يدوي | system قابل للقياس + شفاف + scalable |

---

## 20. الخطوة التالية المباشرة

1. **Beta-recruit 10 شركات سعودية** (real_estate / clinics / training / agencies — لكل قطاع 2-3)
2. **شغّل `first_10_opportunities` mission** لكل شركة في أول 24 ساعة
3. **اقصد 50% approval rate + 5+ replies** في أول أسبوع
4. **أرسل Proof Pack الأسبوع الأول** لكل عميل
5. **اجمع feedback** وحدّث القوالب

> هذا النهج (kill feature → 10 عملاء → proof) أقوى من إطلاق عام بدون validation.
> Boardy للعلاقات + Dealix للنمو والإيرادات.

— Dealix · Saudi Autonomous Revenue Platform · 🇸🇦
