# الانتقال من Moyasar Sandbox إلى Live

1. أكمل الاختبارات في `docs/BILLING_MOYASAR_RUNBOOK.md` (webhook، حالات فشل، idempotency).
2. أنشئ مفاتيح **production** في لوحة Moyasar فقط على بيئة الإنتاج (Railway/Render secrets).
3. غيّر `MOYASAR_PUBLISHABLE_KEY` و`MOYASAR_SECRET_KEY` (أو الأسماء المعتمدة في الكود) دفعة واحدة مع نافذة صيانة قصيرة إن لزم.
4. راقب أول 48 ساعة: معدل رفض، تكرار webhook، سجلات التدقيق.

لا تُخزّن مفاتيح live في git أو في متصفح العميل.
