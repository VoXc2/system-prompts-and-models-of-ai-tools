# Dealix — Founder Launch Kit

Three assets you ship publicly to manufacture inbound + signal.

## 1. Founder launch post (LinkedIn / X)

**LinkedIn (Arabic-first, English subtitle):**

> 🚀 أطلقنا Dealix.
>
> AI sales rep بالعربي الخليجي يرد على leads إنبوند خلال 45 ثانية.
> يأخذ التفاصيل، ييؤهل العميل، ويحجز موعد مع المندوب — قبل ما يبرد الـ lead.
>
> بنيناه عشان السوق السعودي:
> • عربي خليجي طبيعي مو ترجمة
> • دفع Mada / STC Pay / Apple Pay
> • متوافق مع PDPL من اليوم الأول
> • integration مع HubSpot / Salesforce / Zoho / Bitrix
>
> Pilot 7 أيام بـ 499 ريال — تشتغل لكم في خلفية، تشوفون النتائج، ثم تقررون.
> الاسترجاع 100% لو ما اقتنعتم.
>
> العقار، الفنادق، الشحن، التدريب: لو leadsكم تنزل سرعتها بسبب وقت الرد، ابعثوا "Dealix" — أرتب 20 دقيقة.
>
> 📅 https://calendly.com/sami-assiri11/dealix-demo
> 🌐 https://dealix.me
>
> #سعودي #SaaS #AI #المبيعات #VisionWithCode

**X / Twitter (160 chars + thread):**

```
أطلقنا Dealix —
AI sales rep سعودي يرد على leads بالعربي الخليجي خلال 45 ثانية.

7-day pilot بـ 499 ريال.

Thread 🧵👇
```

Thread parts:
1. The problem (Saudi B2B response time = 11h average)
2. Why generic AI tools fail (English / formal Arabic / no Mada)
3. What Dealix does (45-sec response in Khaliji + handoff to closer)
4. Pricing (Pilot 499 → Starter 999 → Pro 5K)
5. Why now (PDPL + Vision 2030 + huge Saudi B2B demand)
6. CTA: "ابعثوا Dealix لـ DM إذا تبون نحجز Pilot"

## 2. Payment request template

**Sami sends after verbal yes:**

```
أهلاً {اسم العميل},

شكراً للثقة. هذا تأكيد ال Pilot:

📦 Dealix Managed Pilot 7 Days
💰 499 ريال (شامل ضريبة القيمة المضافة)
📅 يبدأ: {التاريخ}
🔚 ينتهي: {التاريخ + 7 أيام}
💸 الاسترجاع: 100% خلال 3 أيام لو لم نرد على lead واحد بالعربي

طرق الدفع:
1. رابط Moyasar (Mada / STC Pay / Apple Pay):
   {رابط فاتورة Moyasar}

2. تحويل بنكي (إن فضّلتم):
   البنك: {البنك}
   IBAN: {IBAN}
   الاسم: {اسم الحساب}

بعد الدفع، نرسل رابط Calendly لـ kickoff call (45 دقيقة) — الاثنين أو الثلاثاء يفضّل لـ Sami.

شكراً،
سامي
Dealix — https://dealix.me
WA: +966 {whatsapp_number}
```

## 3. Day-1 onboarding checklist

### Within 30 min of payment:

- [ ] Confirmation email sent (above template)
- [ ] Calendly kickoff link sent
- [ ] Customer added to Dealix Slack/WhatsApp group
- [ ] `customers` row created in DB (POST /api/v1/customers/onboard)
- [ ] `pilot_start_at` timestamp set
- [ ] `pilot_end_at` = +7 days
- [ ] Internal: Sami's calendar blocked for daily 10-min check-ins

### Day 1 — Kickoff call (45 min agenda):

- [ ] **0–5 min:** Welcome, confirm pilot scope
- [ ] **5–20 min:** Intake form (see `customer_intake_template.md`):
  - Customer's offerings
  - Common questions Dealix should handle
  - Pricing tiers (so Dealix can quote correctly)
  - Lead sources (website form? WhatsApp? email?)
  - Existing CRM (HubSpot? Zoho? Excel?)
  - Booking link (Calendly? internal?)
  - Tone preference (formal / Khaliji / mixed)
- [ ] **20–35 min:** Walk through Dealix admin dashboard
- [ ] **35–40 min:** Set success metric (e.g., "respond to 20 leads, book 5 demos")
- [ ] **40–45 min:** Daily check-in schedule + next steps

### Day 2–6 — Daily (5 min):

- [ ] Pull yesterday's leads from `outreach_queue`
- [ ] Review Sami's reply quality
- [ ] Send daily report to customer (via Slack/WhatsApp): "اليوم: ردّينا على X leads، حجزنا Y demos"
- [ ] Capture objections + winning messages

### Day 7 — Review call (30 min):

- [ ] Send pre-call metrics summary (Day 0)
- [ ] Run review meeting
- [ ] Make upgrade ask
- [ ] If yes → switch billing in Moyasar
- [ ] If no → ask "ما اللي منع الاستمرار؟" + log
- [ ] Ask for testimonial regardless
- [ ] Ask for referral regardless

## 4. Day-1 launch scorecard (live)

| Metric | Target | Actual |
|---|---:|---:|
| Outbound reaches | 11 (5 calls + 5 emails + 1 LinkedIn) | _____ |
| Replies | ≥ 2 | _____ |
| Demos booked | ≥ 1 | _____ |
| Pilot pay request sent | ≥ 1 | _____ |
| Pilot pay received | ≥ 1 | _____ |
| LinkedIn manual notes | ≤ 10 | _____ |
| Suppression hits | 0 | _____ |
| Hours worked | ≤ 6 | _____ |

**Day 1 success criterion:** ≥ 1 pilot paid by EOD.

## 5. Anti-burnout reminder

- Don't blast all 100 today. Pace.
- Don't auto-send.
- Don't promise customizations beyond pilot scope.
- Stop calls at 6pm.
- 1 day off per week, non-negotiable.
- Every call ends with ONE concrete next-action — never "I'll think about it".
