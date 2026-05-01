# 💰 Dealix — First Revenue Attempt Playbook

**Use this the exact moment a prospect verbally agrees to pay.**
**Target close-to-paid cycle: under 15 minutes.**

---

## 🎯 Preconditions (already true)

- Backend live: `https://web-dealix.up.railway.app/healthz` returns 200
- Landing live: `https://voxc2.github.io/dealix/`
- Moyasar dashboard accessible (KYC may still be pending — doesn't matter)
- Bank app / STC Pay on phone for manual confirmation
- `pipeline_tracker.csv` open in editor

---

## ⏱️ Minute-by-Minute Script

### 0:00 — The Verbal Yes

Prospect says one of:
- "نبي نجرب"
- "أرسل لي الرابط"
- "خلاص، ابدأ"
- "كم المدة للتفعيل؟"

**Response (on call, immediate):**
> "ممتاز. خلّني أرسل لك رابط الدفع خلال 3 دقائق على واتساب. الباقة [X]، المبلغ [Y] ريال، تفعيل خلال 24 ساعة. أي بطاقة سعودية تشتغل — Mada، Visa، Apple Pay."

### 0:00–0:03 — Generate Payment Link

**Path 1 — Moyasar active (preferred, one command):**

```bash
cd /path/to/dealix
export MOYASAR_SECRET_KEY=sk_live_xxxxxxxxx  # or sk_test_ for verification

# Pilot 1 SAR
bash docs/ops/moyasar_live_test.sh customer@company.com 1 pilot

# OR Starter
bash docs/ops/moyasar_live_test.sh customer@company.com 999 starter

# OR Growth
bash docs/ops/moyasar_live_test.sh customer@company.com 2999 growth
```

Script output contains: invoice URL + WhatsApp-ready Arabic template.

**Path 2 — Moyasar not active (manual):**

Open Moyasar dashboard → Invoices → Create Invoice manually (2 minutes in UI).
Copy URL.

**Path 3 — Moyasar completely unavailable:**

Use `MANUAL_PAYMENT_SOP.md` → send bank IBAN + STC Pay number via WhatsApp.

### 0:03–0:04 — Send WhatsApp

Paste the template from script output. Personalize with prospect name. Send.

Template:
```
مرحباً [الاسم]،

رابط دفع Dealix الخاص بك:
[INVOICE_URL]

المبلغ: [X] ريال
الباقة: [pilot/starter/growth/scale]
طرق الدفع: Mada / Visa / Mastercard / Apple Pay / STC Pay

بعد الدفع تواصل معي مباشرة للتفعيل.

سامي — Dealix
```

### 0:04–0:05 — Update Tracker

Open `pipeline_tracker.csv`, find the prospect's row, update:

| Column | Value |
|--------|-------|
| `plan` | pilot / starter / growth / scale |
| `payment_status` | invoice_sent |
| `notes` | Invoice ID: inv_xxxxx, sent HH:MM |

### 0:05–0:15 — Watch for Payment

- Keep Moyasar dashboard tab open
- Keep bank app open
- Most prospects pay within 10 minutes if they committed verbally

### 0:15 — If Paid

**Within 5 minutes of payment notification:**

1. Update `pipeline_tracker.csv`:
   - `payment_status` = paid
   - `revenue_sar` = [amount]

2. Send WhatsApp confirmation:
```
وصلت الدفعة بأمان. التفعيل خلال 24 ساعة.
سأتواصل معك خلال ساعة لبدء الإعداد.

شكراً لثقتك.
سامي
```

3. Open `FIRST_CUSTOMER_ONBOARDING_CHECKLIST.md` → execute Day 0 steps

4. Book kickoff call via Calendly: https://calendly.com/sami-assiri11/dealix-demo
   - Duration: 45 min
   - Purpose: onboarding kickoff
   - Send link in same WhatsApp thread

### 0:15 — If Not Paid (after 30 min)

One gentle nudge, only once:
```
مرحباً [الاسم]،
لاحظت إن الدفع لم يكتمل. هل في شيء أقدر أساعد فيه؟
- مشكلة تقنية مع الرابط؟
- تحتاج طريقة دفع أخرى؟
- تحتاج وقت أكثر للمراجعة؟
```

**Do NOT nudge more than once.** Move on to next prospect.

---

## 🧾 Post-Payment: Issue Proper Invoice Record

For the customer's records AND for your accounting:

1. Open `docs/sales-kit/dealix_invoice_template.html`
2. Fill:
   - Invoice number: `DLX-2026-XXXXX` (increment from last)
   - Customer name, CR if B2B
   - Plan, amount, VAT (if registered)
   - Payment reference: Moyasar Invoice ID
   - Status: `PAID`
3. Save as PDF (browser print → save as PDF)
4. Email to customer + keep copy in `docs/revenue/invoices/2026/`

**VAT note:** Dealix under 187,500 SAR annual revenue → not VAT-registered → no VAT line on invoice. See `REVENUE_READINESS.md` → ZATCA section.

---

## 📣 Post-First-Revenue Broadcast

Within 24 hours of first paid customer:

### Internal
- [ ] Update `DEALIX_COMPANY_OPERATIONAL_STATE.md`: Revenue status → ACTIVE
- [ ] Update `COMPANY_CONTROL_CENTER.md`: First Revenue Date = today
- [ ] Record learning in `daily_scorecard.md`

### External (optional but powerful)
- [ ] LinkedIn post: "Dealix has its first paying customer. 🎉" (founder voice, no specifics unless customer approves)
- [ ] X (Twitter) post same
- [ ] Tell 3 closest friends/mentors — social accountability
- [ ] If customer agrees: add to landing as social proof (logo + quote)

### For next customer
- [ ] Ask first customer for one referral: "أنت أول عميل لـ Dealix. تعرف أحد يستفيد مثلك؟"
- [ ] Offer referral credit: 500 SAR off if referred customer signs
- [ ] Update `dealix_referral_program.md` with actual customer #1 story

---

## 🔁 Repeat Loop

After first customer, the loop tightens:

```
Day 0:  First payment                 → 1 paid customer
Day 1:  Onboarding kickoff            → delight
Day 3:  Ask for referral              → pipeline + 1 warm
Day 7:  Check-in + case study ask     → social proof
Day 14: Second customer (from referral OR cold) closed same way
```

Every customer = one referral ask. This is how MRR compounds.

---

## 🚨 Gotchas (learned from industry, not yet from Dealix)

| Gotcha | Prevention |
|--------|------------|
| Prospect says yes but never pays | 30-min nudge once, then drop. Their intent is the asset. |
| Customer pays then ghosts on onboarding | Book kickoff call BEFORE sending invoice. "First, let's book the kickoff, then I send payment." |
| Card declined unexpectedly | Have backup: offer bank transfer immediately with IBAN |
| Wants invoice with CR/VAT before paying | Send PDF invoice template first, payment second. Adds 10 min. |
| Chargeback risk | First 10 customers: 100% manual fulfillment + weekly check-ins to prevent disputes |
| Refund requested within 7 days | Honor it immediately. Don't argue. The case study loss > refund value. |

---

## 🧭 When to Retire This Page

Retire this playbook once:
- 10+ customers closed successfully
- Full Moyasar automation live (webhook → welcome email → onboarding sequence)
- Average close time drops below 5 minutes from yes → paid

Until then: this is THE revenue playbook.

---

**First customer ≠ best customer. First customer teaches you more than they pay you.**
**One pilot at 1 SAR from a friend is a legitimate start. Case study + confidence > the fee.**

Ship the first invoice today.
