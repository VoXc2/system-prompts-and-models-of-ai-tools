# Customer Success Playbook

> **القاعدة:** كل عميل له cadence محسوب بحسب الـ bundle. كل تدهور في النشاط يولّد at-risk alert تلقائياً.

---

## Cadence Types

```
weekly_check_in
monthly_proof_review
quarterly_business_review
at_risk_alert
renewal_30_day
renewal_7_day
```

---

## Endpoints

```
POST /api/v1/customer-ops/cs/weekly-check-in
POST /api/v1/customer-ops/cs/at-risk-alert
POST /api/v1/customer-ops/cs/success-plan
```

---

## Weekly Check-in Agenda (25 دقيقة)

1. مراجعة آخر Proof Pack (5 دقائق).
2. أبرز فرصة في الـ pipeline (5 دقائق).
3. أبرز خطر في القنوات (5 دقائق).
4. خطة الأسبوع القادم (5 دقائق).
5. أي مساعدة من فريقنا؟ (5 دقائق).

**Talking points** (تتولد آلياً من metrics):
- "اعتمدتم {drafts_approved} رسالة هذا الأسبوع، ووصلكم {replies} رد."
- "تم تجهيز {meetings} اجتماع."
- "تم منع {risks_blocked} مخاطر تلقائياً."
- "Pipeline متأثر بقيمة {pipeline_sar:.0f} ريال."

---

## At-Risk Detection

النظام يحسب `risk_score` (0..100) من:

| العامل | النقاط |
|--------|-------:|
| غير نشط ≥14 يوم | +40 |
| غير نشط ≥7 يوم | +20 |
| ≥10 drafts معلقة | +25 |
| ≥5 drafts معلقة | +10 |
| آخر Proof Pack ≥14 يوم | +30 |

### Severity
- ≥60 → high → إيميل مؤسس + QBR هذا الأسبوع.
- ≥30 → medium → Proof Pack ملخص + ديمو خدمة جديدة.
- <30 → low → weekly check-in عادية.

---

## Cadence per Bundle

### Growth Starter
- Day 1: kick-off call + intake.
- Day 3: review first 3 opportunities + drafts.
- Day 7: deliver Proof Pack v1.
- Day 14: weekly check-in + upsell offer.
- Day 30: monthly proof review + renewal/upgrade decision.

### Executive Growth OS
- Day 1: onboarding + connect channels.
- Day 7: first weekly Proof Pack.
- Day 14: weekly check-in + Founder Shadow Board v1.
- Day 21: monthly proof review.
- Day 30: QBR + annual upgrade conversation.

### Partnership Growth
- Day 1: partner ICP intake.
- Day 5: 20 partners list + 10 outreach drafts.
- Day 10: 5 partner meetings booked.
- Day 14: weekly check-in.
- Day 30: partner scorecard + revenue share setup.

---

## QBR (Quarterly Business Review)

عند 90 يوم من اشتراك Growth OS:
1. مراجعة 3 Proof Packs السابقة.
2. حساب ROI: pipeline_x + closed_won_x.
3. مقارنة مع benchmarks القطاع (من `growth_memory`).
4. اقتراح تجارب الـ quarter القادم.
5. مراجعة الـ pricing tier.

---

## Renewal Flow

### 30-day-out
- إرسال Proof Pack الشهري + رسالة ودية.
- "نلاقيك في QBR لمراجعة العام القادم؟"

### 7-day-out
- إذا لم يجدّد: إيميل من المؤسس + خصم سنوي 15%.
- إذا renewal at risk: at-risk alert تلقائي.

### Renewal day
- إرسال invoice + شكر.
- بدء plan الـ quarter القادم.

---

## Health Score Formula

```
csat (0..10) × 5
+ pipeline_sar / 1000
+ meetings × 8
+ approval_rate × 50
- days_inactive × 2
- drafts_pending × 1
```

```
≥75 = healthy
50–74 = watch
<50 = at-risk
```

---

## ما لا يحدث في CS

- لا "عرض ترقية" قبل تسليم أول Proof Pack.
- لا spam check-ins (max 1 في الأسبوع).
- لا تخطي الـ at-risk alert إذا تجاوز high.
- لا تعديل cadence بدون موافقة العميل.
