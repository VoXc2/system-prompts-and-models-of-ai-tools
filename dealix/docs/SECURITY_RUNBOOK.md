# Security runbook — Dealix

## حادث تسريب سر (API key / PAT / webhook secret)

1. **إبطال فوري** للمفتاح في منصة المصدر (GitHub / Meta / Moyasar / Supabase).
2. تدوير الاستبدال في Railway/Render secrets ثم إعادة النشر.
3. مراجعة سجلات الوصول من وقت التسريب المحتمل.
4. توثيق الخط الزمني في تذكرة داخلية؛ إخطار العملاء إذا تأثرت بياناتهم (مع المستشار).

مرجع PAT: [`SECURITY_INCIDENT_PAT_EXPOSURE.md`](SECURITY_INCIDENT_PAT_EXPOSURE.md).

## تصعيد

- **P1 — إرسال غير مصرّح به أو دفع خاطئ:** إيقاف flags (`WHATSAPP_ALLOW_LIVE_SEND=false`)، تعطيل webhook إن لزم، اتصال المالك.
- **P2 — تعطل مراقبة أو DB:** اتبع [`docs/ops/DEPLOY_NOW.md`](ops/DEPLOY_NOW.md) وخطط الرجوع في [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md).

## مراجعة دورية

- فحص أن `.env` غير مرفوع؛ تشغيل فحص أنماط أسرار على PRs.
- مراجعة قائمة المشركين على السرّيات في السحابة.

## مسؤوليات

حدّد اسمًا لمالك الأمان التشغيلي ولقناة الطوارئ (بريد/Slack).
