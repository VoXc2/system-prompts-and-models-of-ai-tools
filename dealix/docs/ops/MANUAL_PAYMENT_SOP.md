# 💳 Dealix — Manual Payment SOP

**Use while Moyasar KYC is pending.**
**Valid for first 10 customers** — after that, automate.

---

## Why manual?

Moyasar API returns `account_inactive_error` until full KYC verification completes (1–3 business days). Until then, payments collected via any of these compliant paths:

1. **Bank transfer** — Sami's business bank IBAN
2. **STC Pay** — mobile wallet
3. **Moyasar hosted invoice** (dashboard-created) — works for some merchants before full API activation
4. **Tap Payments** — alternative gateway if needed

---

## Customer Agreement Flow

```
1. Customer says "yes" on demo
  ↓
2. Send manual invoice (HTML / PDF) by email + WhatsApp
  ↓
3. Customer pays via bank transfer, STC Pay, or hosted invoice
  ↓
4. Sami receives bank notification
  ↓
5. Sami logs payment in pipeline_tracker.csv
  ↓
6. Sami onboards customer manually (see ONBOARDING_CHECKLIST.md)
```

---

## Invoice Template (copy-paste)

```
فاتورة Dealix — [رقم الفاتورة]

العميل: [اسم الشركة]
التاريخ: [YYYY-MM-DD]
تاريخ الاستحقاق: [+7 أيام]

---

البند                                     الكمية   السعر
Dealix — [الباقة]                          1        [999/2999/7999] ريال
---
المجموع الفرعي:                                     [X] ريال
ضريبة القيمة المضافة (15%):                        [X] ريال
المجموع الكلي:                                      [X] ريال

---

طرق الدفع:

1. تحويل بنكي:
   اسم المستفيد: [سامي العسيري]
   البنك: [اسم البنك]
   IBAN: [SA00 0000 0000 0000 0000 0000]

2. STC Pay:
   الرقم: [+966 5XX XXX XXX]

3. بعد الدفع:
   أرسل صورة الإيصال على:
   WhatsApp: [+966 5XX XXX XXX]
   Email: sami.assiri11@gmail.com

---

شروط:
- التفعيل خلال 24 ساعة من استلام الدفع
- استرجاع كامل خلال 7 أيام إذا Pilot
- Setup + تدريب مجاني مع كل باقة

شكراً لثقتكم،
سامي العسيري — Founder, Dealix
https://voxc2.github.io/dealix/
```

---

## Logging in Pipeline Tracker

Once payment received, update `docs/ops/pipeline_tracker.csv`:

```
id=X, ..., payment_status=paid, revenue_sar=[amount], notes=paid via bank transfer on YYYY-MM-DD, invoice INV-001
```

---

## When Moyasar KYC completes

1. Sami sends new activated `sk_live_...` key (in private, not chat)
2. I update Railway env var via GraphQL
3. Redeploy → verify 1 SAR test payment → automate all further customers
4. Retire this manual SOP

---

## SLA Commitments

- Reply to payment confirmation within 30 minutes during business hours
- Activate customer account within 4 hours of payment received
- First onboarding call scheduled within 24 hours

---

## Revenue Recognition (accounting)

For each manual payment:
1. Issue formal invoice PDF with customer details
2. Keep copy in `/invoices/` (local to Sami, not in repo)
3. Bank deposit reference = invoice reference
4. Monthly: reconcile with accountant
5. VAT tracking: accumulate toward ZATCA threshold
