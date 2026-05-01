# بوابات إغلاق Paid Private Beta — قائمة مرجعية

استخدم هذه القائمة قبل أول عميل إنتاج أو إرسال حي. التفاصيل في الملفات المرتبطة.

## أمن وأسرار

- [ ] لا مفاتيح في الكود أو المحادثات؛ كل القيم في Railway / GitHub Secrets فقط.
- [ ] بعد أي تسريب: [`SECURITY_SECRET_ROTATION_CHECKLIST.md`](SECURITY_SECRET_ROTATION_CHECKLIST.md).
- [ ] `API_KEYS` مفعّل على الإنتاج/staging المقفل — [`api/security/api_key.py`](../api/security/api_key.py).

## تقنية ونشر

- [ ] فرع النشر `ai-company` (أو السياسة المعتمدة) — [`docs/ops/GITHUB_AI_COMPANY_TRACK.md`](ops/GITHUB_AI_COMPANY_TRACK.md).
- [ ] Railway: Root `dealix`، `DATABASE_URL`، `APP_SECRET_KEY`, `APP_URL`, `CORS_ORIGINS` — [`docs/ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md).
- [ ] `smoke_staging` ناجح — [`LAUNCH_DAY_VERIFICATION_LOG.md`](LAUNCH_DAY_VERIFICATION_LOG.md).

## قانون وخصوصية (PDPL)

- [ ] شروط + خصوصية منشورة.
- [ ] DPA pilot جاهز أو موقّع — [`DPA_PILOT_TEMPLATE.md`](DPA_PILOT_TEMPLATE.md).
- [ ] PDPL: [`SECURITY_PDPL_CHECKLIST.md`](SECURITY_PDPL_CHECKLIST.md)، [`PRIVACY_PDPL_READINESS.md`](PRIVACY_PDPL_READINESS.md)، [`DATA_MAP.md`](DATA_MAP.md).

## فوترة

- [ ] Moyasar **sandbox** للبيتا حتى الموافقة على live — [`BILLING_RUNBOOK.md`](BILLING_RUNBOOK.md).
- [ ] `MOYASAR_WEBHOOK_SECRET` مضبوط عند تفعيل الويبهوك.

## واتساب

- [ ] `WHATSAPP_ALLOW_LIVE_SEND=false` ما لم يُوافَق مع opt-in — [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md)، [`WHATSAPP_OPERATOR_FLOW.md`](WHATSAPP_OPERATOR_FLOW.md).

## تشغيل وتجاري

- [ ] SOP يومي — [`docs/ops/SOP_REVENUE_ENGINE_DAILY.md`](ops/SOP_REVENUE_ENGINE_DAILY.md).
- [ ] إغلاق أول عملاء — [`docs/business/CLOSE_FIRST_CUSTOMERS_14D.md`](business/CLOSE_FIRST_CUSTOMERS_14D.md).

## GitHub Actions (اختياري لكن موصى به)

- [ ] أسرار `STAGING_BASE_URL` / `STAGING_API_KEY` — [`docs/ops/GITHUB_ACTIONS_ENV_SETUP.md`](ops/GITHUB_ACTIONS_ENV_SETUP.md).
- [ ] لاحقاً `DEALIX_API_BASE` / `DEALIX_API_KEY` لآلة الإيراد اليومية.
