# Revenue Today Playbook — تحويل Dealix إلى دخل اليوم

> **القاعدة:** الهدف اليوم ليس إطلاق عام. الهدف **أول 499 ريال أو commitment** عبر Private Beta + Pilot 7 أيام.

---

## 1. العروض المدفوعة المتاحة اليوم

### Pilot 7 أيام — 499 ريال (الأساسي)
- 10 فرص B2B + رسائل عربية + خطة متابعة + Proof Pack.
- بدائل: مجاني مقابل case study.
- مدة التسليم: 7 أيام، تبدأ يوم الأحد بعد الدفع.

### Growth OS Pilot — 1,500–3,000 ريال (30 يوم)
- التشغيل الكامل لشهر: command feed + drafts + اجتماعات + Proof Pack أسبوعي.
- الترقية المنطقية لـ Growth OS Monthly (2,999/شهر).

### Free Growth Diagnostic — 0 ريال (24 ساعة)
- 3 فرص + رسالة + توصية بخدمة مدفوعة.
- يقود لـ Pilot 499 أو Growth OS Pilot.

---

## 2. من نستهدف اليوم (4 فئات × 5 = 20 prospect)

| Segment | عدد | عرض أساسي | عرض احتياطي | قناة |
|---------|----:|-----------|-------------|------|
| وكالات تسويق B2B | 5 | Growth OS Pilot | Free Case Study | Email |
| تدريب/استشارات | 5 | Pilot 499 | Free Case Study | Email |
| SaaS/تقنية صغيرة | 5 | Pilot 499 | Growth OS Pilot | LinkedIn Lead Form |
| خدمات بقاعدة واتساب | 5 | List Intelligence | WhatsApp Compliance | Email |

**القواعد:**
- لا scraping ولا قوائم مشتراة.
- استخدم علاقاتك المباشرة + جهات تعرفها.
- كل رسالة يدوية، لا automation.
- حد أقصى 3 follow-ups ثم أرشفة.

---

## 3. أول 20 رسالة — جاهزة للنسخ

استخدم endpoint:
```
GET /api/v1/launch/outreach/first-20
```

أو يدوياً:

### رسالة عامة
هلا [الاسم]، أطلقنا Beta محدودة لـ Dealix.
Dealix يساعد الشركات تطلع فرص B2B مناسبة، يكتب الرسائل بالعربي، ويخلي صانع القرار يوافق قبل أي تواصل، وبعدها يعطي Proof Pack.
أفتح 5 مقاعد Pilot هذا الأسبوع. يناسبك أعطيك Free Diagnostic لشركتكم؟

### وكالة
هلا [الاسم]، عندي Beta خاص للوكالات.
Dealix يطلع فرص لعملاءكم، يجهز رسائل عربية، يدير موافقات، ويطلع Proof Pack بعلامة الوكالة.
أبحث عن وكالة واحدة نجرب معها Pilot مشترك على عميل حقيقي. يناسبك ديمو 15 دقيقة؟

### SaaS
هلا [الاسم]، رأيت إصدار النسخة الجديدة من منتجكم — مبروك.
نشتغل على مدير نمو عربي يطلع 10 فرص B2B عبر LinkedIn Lead Forms (لا scraping) ويكتب الرسائل بالعربي.
أبغى أجربه مع شركة SaaS سعودية واحدة. يناسبك ديمو 12 دقيقة؟

---

## 4. الديمو — 12 دقيقة

استخدم:
```
GET /api/v1/launch/demo/flow
```

ملخص: 0–2 الفكرة → 2–4 Daily Brief → 4–6 10 فرص → 6–8 Trust + Approval → 8–10 الأمان → 10–12 العرض والـCTA.

**الإغلاق:**
> "تمام، نبدأ Pilot 7 أيام بـ499 ريال. أرسل لك خلال ساعة intake form + Moyasar invoice + موعد كيك-أوف."

---

## 5. Pipeline Tracker

8 stages:
```
identified → contacted → replied → demo_booked →
diagnostic_sent → pilot_offered → paid → (or lost)
```

استخدم:
```
GET /api/v1/revenue-launch/pipeline/schema
POST /api/v1/revenue-launch/pipeline/summarize
```

أو افتح Sheet باسم `Dealix First 20 Pipeline` بالعمدة المعرّفة في الـ schema.

---

## 6. تسليم أول Pilot — خلال 24 ساعة

بعد الدفع:
1. **T+0h** — كيك-أوف + استلام intake.
2. **T+1h** — Diagnosis (targeting + contactability).
3. **T+6h** — Drafting (10 رسائل عربية + safety/tone evals).
4. **T+18h** — Approval Pack (cards مع ≤3 أزرار).
5. **T+24h** — Proof Pack v1 + جدولة جلسة المراجعة.

استخدم:
```
GET /api/v1/revenue-launch/pilot-delivery/intake-form
POST /api/v1/revenue-launch/pilot-delivery/24h-plan
```

---

## 7. الدفع اليدوي عبر Moyasar

**لا live charge من API.** فقط:
- Moyasar Dashboard → Invoices → Create Invoice.
- 499 ريال = 49,900 halalas.
- وصف: "Dealix Private Beta Pilot — 7 days".
- إرسال للعميل بالإيميل.

استخدم:
```
POST /api/v1/revenue-launch/payment/invoice-instructions
POST /api/v1/revenue-launch/payment/link-message
GET  /api/v1/revenue-launch/payment/confirmation-checklist
```

**قبل بدء التسليم:** تأكد invoice في حالة `paid` على Moyasar dashboard.

---

## 8. Proof Pack — في نهاية الأسبوع

5 أسطر executive summary + 8 metrics + توصية بالخطوة التالية.

استخدم:
```
POST /api/v1/revenue-launch/proof-pack/template
POST /api/v1/revenue-launch/proof-pack/client-summary
POST /api/v1/revenue-launch/proof-pack/next-step
```

---

## 9. أهداف اليوم

| Metric | Target |
|--------|-------:|
| Outreach sent | 20 |
| Replies | 5 |
| Demos booked | 3 |
| Pilots paid | 1 |

أهداف 7 أيام: 100 outreach / 20 ردود / 10 ديمو / 2 pilots مدفوعة.

استخدم:
```
GET /api/v1/launch/scorecard/demo
POST /api/v1/launch/scorecard/event
POST /api/v1/launch/scorecard/daily
POST /api/v1/launch/scorecard/weekly
```

---

## 10. Go / No-Go اليوم

10 بوابات (`POST /api/v1/launch/go-no-go` أو `python scripts/launch_readiness_check.py`):

1. Tests passed.
2. Routes check OK.
3. No secrets in repo.
4. Staging /health → 200.
5. Supabase staging configured.
6. Service catalog ≥4 services.
7. landing/private-beta.html ready.
8. First-20 prospects identified.
9. WHATSAPP/GMAIL/CALENDAR/MOYASAR live=false.
10. Moyasar invoice/payment-link manual flow ready.

**Critical gates** (must pass): `no_secrets`, `live_sends_disabled`, `staging_health`. Otherwise: NO-GO.

---

## 11. ما لا تفعله اليوم

- لا live WhatsApp/Gmail/Calendar/Moyasar من API.
- لا scraping LinkedIn ولا auto-DM.
- لا cold WhatsApp.
- لا Public Launch / إعلان صحفي.
- لا "نضمن نتائج".

---

## 12. الخطوة بعد أول Pilot

- Proof Pack → Case Study → ترقية لـ Growth OS Monthly.
- Case Study → استخدمه في الـ outreach التالي.
- متابعة شهرية مع Service Excellence backlog (ما يحسّن الخدمة).
