# 🚚 Dealix — First Customer Delivery Template

**Purpose:** Serve the first 10 customers manually, before customer dashboard exists.
**Time from payment → Dealix live for customer:** 48 hours max.

---

## Hour 0 — Payment Received

1. Sami confirms payment in bank / STC Pay / Moyasar dashboard
2. Updates `pipeline_tracker.csv` row: `payment_status=paid, revenue_sar=[amount]`
3. Sends acknowledgment WhatsApp/email within 30 min:
   ```
   استلمنا الدفعة ✅
   سنبدأ setup خلال 24 ساعة.
   قبل كذا، ممكن تحجز kick-off call 30 دقيقة هنا:
   https://calendly.com/sami-assiri11/dealix-kickoff
   ```

---

## Hour 1-4 — Customer Intake

Send this form/email to customer (or cover in kick-off call):

**Subject:** Dealix — Kick-off · مرحباً بك

```
أهلاً [الاسم]،

مبروك على الانطلاق! قبل نبدأ، نحتاج بعض المعلومات:

1️⃣ **Business Info**
   - الاسم التجاري الكامل:
   - القطاع:
   - عدد مندوبي المبيعات:
   - الموقع:

2️⃣ **Lead Sources**
   من أين تأتي leads حالياً؟
   ( ) موقع + form
   ( ) WhatsApp
   ( ) Instagram DM
   ( ) مكالمات
   ( ) إعلانات مدفوعة
   ( ) Referrals

3️⃣ **Current CRM/Tools**
   ( ) HubSpot  ( ) Zoho  ( ) Salesforce  ( ) Excel  ( ) None
   أي أدوات أخرى:

4️⃣ **Calendly / Booking**
   رابط Calendly الخاص بك أو بالفريق:

5️⃣ **Qualification (8 أسئلة Dealix تسأل كل lead)**
   اقترح 8 أسئلة مهمة لتأهيل عميلك:
   1.
   2.
   3.
   ... (حتى 8)

6️⃣ **Offer / Pricing Rules**
   - Price range للمنتج/الخدمة:
   - هل تقبل نسبة Discount؟ كم max?
   - شروط دفع:

7️⃣ **Handoff**
   عند تأهل lead A، لمن نرسل الإشعار؟
   - Email:
   - WhatsApp:

8️⃣ **Dialect**
   ( ) سعودي/خليجي  ( ) عربي فصحى أبسط  ( ) Arabic + English mix

9️⃣ **Business hours**
   ساعات العمل للرد اليدوي عند الحاجة:

نجتمع بعد ما تعبيها 30 دقيقة kick-off.
```

---

## Hour 4-24 — Setup (Sami manual work)

### 24.1 — Custom Dealix Configuration
For each customer, create a Google Doc: `Customer_[CompanyName]_Config.md` with:

```markdown
# Dealix Config: [Company]

## BANT Questions (from intake form)
1. [Budget question]
2. [Authority question]
3. [Need question]
4. [Timeline question]
5. [Custom 5]
6. [Custom 6]
7. [Custom 7]
8. [Custom 8]

## Qualification Scoring
- A (hot): Budget confirmed + decision maker + need urgent + timeline < 1 month
- B (warm): Any 3 of above
- C (cold): Any 2
- D (disqualified): Missing budget OR wrong fit

## Handoff Template (to customer's team)
Subject: [Dealix] New qualified lead — [Contact] from [Their Company]

Hi [Customer team],

New A/B-tier lead qualified:
- Name: [Lead name]
- Company: [Their company]
- Pain: [One line from conversation]
- Budget: [Range]
- Timeline: [When]
- Best contact: [Phone/email]
- Demo booked: [Calendly URL]

Full conversation: [Link to Notion/Doc]

Sami / Dealix
```

### 24.2 — Call Forwarding Setup
- Get customer's website / form / WhatsApp number
- Configure forwarding: 
  - Customer's web form → Sami's email (until API integration built)
  - Customer's WhatsApp → Sami's phone
  - Customer's Instagram DMs → Sami handles via Meta Business

### 24.3 — Monitoring Sheet
Create per-customer Google Sheet:
```
Date | Lead Source | Lead Name | Contact | Qualification Score | Demo Booked? | Handoff Status | Notes
```

---

## Day 1-7 — Active Manual Operation

### Daily for this customer (30-60 min each)
- Morning: Check customer's incoming leads (forwarded to Sami)
- Within 1 hour: Reply to each lead using Dealix BANT framework manually
  - Use Claude or own AI to help draft responses in < 45 seconds
  - Be the "Dealix AI" until product is automated
- Book demos in customer's Calendly
- Send qualification summary to customer's team via Slack/email
- Evening: Update per-customer tracking sheet

### Response Template (use for every lead)
```
السلام عليكم [الاسم]،

شكراً لتواصلك مع [Company]. فريقي جاهز يخدمك.
قبل نحجز اجتماع مع [مدير المبيعات]، سؤالين بسرعة:

1. [سؤال BANT مخصّص 1]؟
2. [سؤال BANT مخصّص 2]؟

بعدها نحدد وقت demo مناسب.
```

---

## Day 3 — Mid-Week Customer Check-in

Send to customer:
```
[الاسم]،

بعد 3 أيام من go-live، هذا التقدم:
📊 Leads received: X
📊 Leads qualified (A/B): Y
📊 Demos booked: Z
⏱️ Avg response time: X min
📈 Qualification rate: Y%

ملاحظات مبكرة:
- [ما ينجح]
- [ما نحتاج نحسّنه]

نجتمع يوم الخميس 15 دقيقة؟
```

---

## Day 7 — Week 1 Report + Decision Point

Send formal Week 1 report:
```
[الاسم]،

تقرير أسبوع 1 — Dealix @ [Company]

📊 METRICS
Leads total: __
Qualified (A/B): __ (%__)
Demos booked: __
Demos attended: __ (%__)
Pipeline value: __ SAR

⏱️ TIMING
Avg first response: __ min (target: <60 sec after Moyasar automation)
Avg qualification: __ min
Demo booking rate: __%

✨ WINS
- [Highlight 1]
- [Highlight 2]

⚠️ LEARNINGS
- [What's not working]
- [What to adjust]

📅 NEXT 7 DAYS
- Continue manual operation through week 2
- Move to automated dashboard when live (target: post 10th customer)
- Optimize BANT questions based on replies

Decision: نكمل Pilot + ننتقل لـ Starter plan شهرياً؟ أو نعدّل شي أولاً؟
```

---

## Transition to Automated (after customer 10+)

When self-serve dashboard is ready (post-Moyasar + post-10 customers):

1. Invite customer to dashboard (via invite link email)
2. Migrate their config (BANT questions, handoff email, scoring rules)
3. Train them 60 min on using dashboard
4. Continue Sami support for 30 days
5. Reduce manual touch to weekly check-ins only

---

## Refund / Cancellation Path

**Pilot (1 SAR, 7 days):** Unconditional refund if requested. Bank-to-bank within 7 days.

**Paid month (Starter/Growth/Scale):**
- First 30 days: Prorated refund
- After 30 days: Cancel effective end of month

**Process:**
1. Customer sends cancel request via WhatsApp/email
2. Sami acknowledges within 4 hours
3. Exit interview (15 min call) to understand why
4. Refund processed via same payment channel
5. Update tracker: `payment_status=refunded`
6. Document in `docs/ops/churn_reasons.md` (create if doesn't exist)
7. Remove customer access after 30-day data grace period

---

## Manual Fulfillment Rules (Important)

### DO
- Respond to every customer lead within 1 hour during business hours
- Match dealix's quality expectations (as if AI were doing it)
- Log everything: can't improve what isn't measured
- Bill hours honestly to track cost-per-customer
- Share metrics with customer weekly

### DON'T
- Promise features not in product
- Commit to response times you can't keep manually
- Take on more than 3 customers manually before automation
- Discount below Pilot 1 SAR floor
- Skip the intake form (it makes manual work 10x harder without context)

---

## Success Criteria for First Customer (before scaling)

Before Sami takes customer #2, customer #1 must show:
- ✅ NPS ≥ 7
- ✅ 3+ qualified leads delivered
- ✅ 1+ demo booked from Dealix leads
- ✅ Renewal commitment for month 2
- ✅ Permission to publish case study (anonymous OK)

If customer #1 doesn't hit these → fix product/process before customer #2.
