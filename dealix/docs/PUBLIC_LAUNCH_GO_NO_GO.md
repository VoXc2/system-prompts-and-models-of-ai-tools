# Public Launch — Go / No-Go

## Go فقط إذا تحققت كل البنود الحرجة

- [ ] استقرار الإنتاج ≥ 14 يوماً بدون حادث P1
- [ ] 5–10 عملاء beta؛ ≥ 3 دافعين فعليين (أو معيار بديل مكتوب في مجلس الإدارة)
- [ ] Terms، Privacy، DPA منشورة ومراجعقة قانونياً
- [ ] [`BILLING_RUNBOOK.md`](BILLING_RUNBOOK.md) مختبر sandbox→live
- [ ] [`WHATSAPP_PRODUCTION_CUTOVER.md`](WHATSAPP_PRODUCTION_CUTOVER.md) مكتمل إذا وُجد WhatsApp إنتاجي
- [ ] نسخ احتياطي واختبار استعادة موثّق
- [ ] [`PUBLIC_LAUNCH_CHECKLIST.md`](PUBLIC_LAUNCH_CHECKLIST.md) مكتمل تقريباً

## No-Go típico

- لا عملية حوادث؛ لا secrets manager؛ لا إثبات فوترة؛ إرسال حي بدون بوابات.

## بعد القرار

- إذا لم يتحقق Go: ابقَ على تسمية **Paid Private Beta** حتى إغلاق الفجوات ([`PAID_BETA_SCORECARD.md`](PAID_BETA_SCORECARD.md)).
