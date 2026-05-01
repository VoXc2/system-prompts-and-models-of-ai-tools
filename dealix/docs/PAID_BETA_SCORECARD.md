# Paid Beta — بطاقة نقاط (Scorecard)

قيّم كل أسبوعين (✓ / ✗) قبل السماح بالانتقال إلى “launch candidate”.

| المؤشر | الهدف | ملاحظات |
|--------|-------|---------|
| حسابات مفعّلة | ≥ 5 عملاء نشطين | تعريف “نشط”: استخدام أسبوعي لمسار أساسي |
| إرسال غير مصرّح | 0 حوادث | أي WhatsApp/Gmail خارج الموافقة = فشل فوري |
| استقرار smoke staging | ≥ 95% نجاح على 14 يوماً | من `smoke_staging` أو مراقبة خارجية |
| دفع ناجح | ≥ 3 معاملات sandbox أو live حسب المرحلة | موثّقة في المحاسبة |
| دعم وتشغيل | Runbook معروف | [`SECURITY_RUNBOOK.md`](SECURITY_RUNBOOK.md) + قناة دعم |
| مراقبة | Sentry + Langfuse فعّالة على staging/prod حسب النشر | [`OBSERVABILITY_ENV.md`](OBSERVABILITY_ENV.md) |
| Evals | `python scripts/run_evals.py` أخضر | [`EVALS_RUNBOOK.md`](EVALS_RUNBOOK.md) |

## قرار

- **متابعة البيتا:** أي عمود حرج ✗
- **Launch candidate:** كل الحرجة ✓ + موافقة إدارة + قانون
