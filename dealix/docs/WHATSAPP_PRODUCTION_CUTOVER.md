# WhatsApp — انتقال إلى الإنتاج (Production cutover)

## قبل التفعيل

1. تطبيق Meta موثّق؛ رقم هاتف الأعمال؛ سياسة الأعمال مفعّلة.
2. **Webhook:** إكمال التحقق GET؛ `WHATSAPP_VERIFY_TOKEN` في أسرار السيرفر فقط.
3. **`WHATSAPP_APP_SECRET`:** مُعرَّف في staging/production حتى يُفرَض التحقق من `X-Hub-Signature-256` على كل `POST` (انظر [`api/routers/webhooks.py`](../api/routers/webhooks.py)).
4. **`WHATSAPP_ALLOW_LIVE_SEND`:** يبقى `false` حتى اكتمال opt-in والمراجعة القانونية؛ ثم تفعيل صريح فقط لبيئة محددة.

## الإرسال

- مسار Meta الرسمي: [`integrations/whatsapp.py`](../integrations/whatsapp.py) — يحترم `whatsapp_allow_live_send`.
- مسارات المزودين الآخرين: [`whatsapp_multi_provider.py`](../auto_client_acquisition/email/whatsapp_multi_provider.py) — نفس البوابة عبر الإعدادات.

## تشغيل

1. رفع الإصدار إلى staging؛ اختبار webhook بتوقيع صحيح؛ مراقبة Sentry.
2. Pilot داخلي 3–5 مستخدمين؛ كل رسالة بموافقة بشرية.
3. موافقة للانتقال إلى production؛ تفعيل `WHATSAPP_ALLOW_LIVE_SEND=true` في secrets الإنتاج فقط إن لزم.

## Rollback

- تعطيل الإرسال: `WHATSAPP_ALLOW_LIVE_SEND=false`.
- تعطيل webhook من لوحة Meta أو إرجاع التطبيق لنسخة سابقة.

انظر أيضاً: [`WHATSAPP_OPERATOR_FLOW.md`](WHATSAPP_OPERATOR_FLOW.md).
