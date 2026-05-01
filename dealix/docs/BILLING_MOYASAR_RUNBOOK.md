# الفوترة — Moyasar (Dealix)

## أين الكود؟

- `api/routers/pricing.py` — خطط، `amount_halalas`، `POST /api/v1/checkout`، webhook Moyasar.

## المبدأ

- **لا مفتاح سري في الريبو**؛ `MoyasarClient` يقرأ من متغيرات بيئة في وقت التشغيل (انظر `dealix.payments`).
- المبالغ بالـ **هللة** (SAR × 100) داخل `PLANS`.

## خطط حالية (تقريب استراتيجية التسعير)

| مفتاح | اسم | amount_halalas |
|-------|-----|----------------|
| starter | Starter | 99900 → 999 SAR |
| growth | Growth | 299900 → 2999 SAR |
| scale | Scale | 799900 → 7999 SAR |
| pilot_1sar | Pilot | 100 (اختبار) |

مزامنة التسميات مع `docs/PRICING_STRATEGY.md` عند التسويق العام.

## Checkout «حقيقي»

- `POST /api/v1/checkout` يستدعي مزود الدفع — **لا تشغّله في CI** بدون مفاتيح وهمية/بيئة sandbox.

## Webhook

- `POST /api/v1/webhooks/moyasar` — يتطلب توقيعاً صحيحاً (`verify_webhook`).

## تشغيل محلي آمناً

- بدون مفاتيح Moyasar: استدعاء `list_plans` فقط أو اختبارات الوحدة.
