# Billing — فهرسة التشغيل (Dealix)

## أين التفاصيل

| الموضوع | الملف |
|---------|--------|
| Moyasar API، sandbox، webhooks | [`BILLING_MOYASAR_RUNBOOK.md`](BILLING_MOYASAR_RUNBOOK.md) |
| الانتقال إلى live | [`MOYASAR_LIVE_CUTOVER.md`](MOYASAR_LIVE_CUTOVER.md) |
| سياسة الاسترداد (مسودة) | [`REFUND_POLICY.md`](REFUND_POLICY.md) |
| الجاهزية للفوترة الإلكترونية / ZATCA | [`INVOICING_ZATCA_READINESS.md`](INVOICING_ZATCA_READINESS.md) |

## نقاط أمان

- المبالغ بالـ **هللات** في الكود (`amount_halalas`).
- أسرار Moyasar و`MOYASAR_WEBHOOK_SECRET` في Secret Manager فقط.
- لا charge حقيقي من الريبو أو من CI.

## نقاط الكود

- Checkout: [`api/routers/pricing.py`](../api/routers/pricing.py) (`POST /api/v1/checkout`)
- Webhook: `POST /api/v1/webhooks/moyasar` — تحقق `secret_token` عبر [`dealix/payments/moyasar.py`](../dealix/payments/moyasar.py)
