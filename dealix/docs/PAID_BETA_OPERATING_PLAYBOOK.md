# Paid Beta Operating Playbook

> **القاعدة:** الجاهزية التقنية لا تعني دخل. هذا الـ playbook يحوّل GO_PRIVATE_BETA إلى أول 499 ريال خلال 7 أيام.

---

## 1. الحالة الحالية

```
✅ Tests: 949 passed, 2 skipped
✅ CI green
✅ Service Tower + Service Excellence + Targeting OS + Customer Ops جاهزة
✅ Positioning Lock مفعّل
✅ Landing pages متوافقة مع POSITIONING_LOCK
🟡 Staging: ينتظر النشر الفعلي
🟡 First payment: ينتظر أول عميل
```

**الحالة:** `GO_PRIVATE_BETA` محلياً. الانتقال لـ `PAID_BETA_READY` يحتاج Staging شغّال + أول Pilot مدفوع.

---

## 2. الانتقال من Private Beta إلى Paid Beta

### Gate الانتقال (لا تتجاوزه)

```text
✅ Staging /health = 200
✅ Service catalog يعرض 4+ خدمات
✅ landing/private-beta.html فيه 499 SAR + CTA
✅ no_secrets scan نظيف
✅ live_sends_disabled = true
✅ Moyasar invoice/payment-link manual flow جاهز
✅ أول 20 prospect معرّفون في Operating Board
```

### Smoke Commands

```bash
export STAGING_BASE_URL="https://YOUR-STAGING-URL"
python scripts/smoke_staging.py --base-url "$STAGING_BASE_URL"
python scripts/launch_readiness_check.py --staging-url "$STAGING_BASE_URL"
python scripts/paid_beta_daily_scorecard.py --as-of today
```

المطلوب: `PAID_BETA_READY`. لو NO-GO → أصلح السبب قبل أي بيع.

---

## 3. خطة 7 أيام للوصول للدخل الأول

### يوم 1 — Staging + Outreach
- نشر staging على Railway.
- تشغيل smoke + readiness checks.
- إرسال 10 رسائل (5 وكالات + 5 شركات).
- 1 منشور LinkedIn (founder voice).

**الهدف:** 2 ردود + 1 ديمو محجوز.

### يوم 2 — Demos
- إرسال 10 رسائل أخرى.
- إجراء أول 1-2 ديمو.
- بدء أول Free Diagnostic لأي عميل اهتم.

**الهدف:** 1 Free Diagnostic موعود.

### يوم 3 — Diagnostic Delivery
- تسليم أول Free Diagnostic خلال 24 ساعة.
- 5 follow-ups.
- إرسال 5 رسائل جديدة.

**الهدف:** 1 Pilot Offer.

### يوم 4 — First Pilot Sale
- محادثة Pilot 499 مع المهتم.
- إنشاء Moyasar invoice manual.
- إرسال payment-link-message.

**الهدف:** 1 invoice paid أو commitment مكتوب.

### يوم 5 — Pilot Delivery Day 1
- استلام intake من العميل.
- تشغيل First 10 Opportunities Sprint workflow.
- 10 opportunities + 10 رسائل عربية.

**الهدف:** Approval Pack مرسل للعميل.

### يوم 6 — Pilot Delivery Day 2
- متابعة الموافقات.
- تشغيل follow-up sequence.
- أول 1-2 رد إيجابي.

**الهدف:** اعتماد ≥3 رسائل + Proof Pack v1.

### يوم 7 — Proof + Upsell
- تسليم Proof Pack.
- جلسة مراجعة 30 دقيقة.
- اقتراح ترقية لـ Growth OS Pilot.

**الهدف:** Case study أو Pilot ثانٍ.

---

## 4. أهداف الأسبوع

| Metric | Target |
|--------|-------:|
| Messages sent | 50–70 |
| Positive replies | 5–10 |
| Demos booked | 3–5 |
| Pilots offered | 2–3 |
| Payments requested | 1–2 |
| Payments received | 1+ |
| Proof packs delivered | 1+ |

---

## 5. القواعد التشغيلية اليومية (لا تتنازل عنها)

1. **لا live WhatsApp send** بدون env flag + اعتماد بشري.
2. **لا live Gmail send** بدون env flag + اعتماد بشري.
3. **لا Calendar insert** بدون اعتماد.
4. **لا Moyasar charge** من API — invoice/payment-link manual فقط.
5. **لا scraping LinkedIn** ولا auto-DM — Lead Gen Forms + manual فقط.
6. **لا cold WhatsApp** بدون opt-in — PDPL hard-block.
7. **كل رسالة** تمر `safety_eval` + `saudi_tone_eval` قبل الإرسال.
8. **كل فعل** يُسجّل في Action Ledger.

---

## 6. Daily Cadence

### الصباح (60 دقيقة)
- شغّل `paid_beta_daily_scorecard.py`.
- راجع الـ Operating Board.
- اعتمد drafts اليوم (10–15 دقيقة).
- 5 follow-ups.

### الظهر (90 دقيقة)
- 1–2 ديمو.
- 10 رسائل جديدة (segments متنوعة).

### العصر (60 دقيقة)
- تسليم deliverable لعميل واحد.
- إجابة support tickets (إن وجد).

### آخر اليوم (30 دقيقة)
- تحديث Operating Board.
- تشغيل scorecard مرة أخرى.
- خطة الغد.

---

## 7. ما لا تضيفه هذا الأسبوع

- لا ميزات تقنية جديدة.
- لا layers معمارية.
- لا modules جديدة.
- لا بريق landing.

**التركيز كله:** عميل واحد يدفع 499 ريال.

---

## 8. شروط الانتقال إلى Public Launch

لا انتقال قبل:
```
5–10 pilots
2+ paid customers
0 unsafe sends
weekly proof packs delivered
support flow يعمل
funnel واضح من lead → demo → pilot → paid
14 يوم staging stable
billing live (Moyasar API webhook)
terms + privacy + DPA
```

---

## 9. Endpoints المهمة في Paid Beta

```
GET  /api/v1/launch/private-beta/offer
POST /api/v1/launch/go-no-go
GET  /api/v1/launch/scorecard/demo
GET  /api/v1/operator/bundles
POST /api/v1/operator/chat/message
POST /api/v1/customer-ops/onboarding/checklist
POST /api/v1/customer-ops/connectors/summary
POST /api/v1/revenue-launch/payment/invoice-instructions
POST /api/v1/revenue-launch/proof-pack/template
GET  /api/v1/service-excellence/review/all
```

---

## 10. القرار النهائي

```
لا تنتظر "كمال المنتج". المنتج كامل تقنياً.
أنت تنتظر "أول إيراد".
الإيراد يأتي من 50 رسالة يدوية + 5 ديمو + 1 invoice.
ابدأ.
```
