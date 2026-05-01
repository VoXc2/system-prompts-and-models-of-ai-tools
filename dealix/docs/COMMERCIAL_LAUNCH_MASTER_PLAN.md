# الخطة الرئيسية للتدشين التجاري — Dealix

**تنفيذ يوم التدشين:** [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md) — **نطاق التسمية (بيتا vs عام):** [`LAUNCH_SCOPE_AND_NAMING.md`](LAUNCH_SCOPE_AND_NAMING.md).  
**تتبع Go/No-Go:** [`PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md`](PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md) — **تدوير أسرار بعد تسريب:** [`SECURITY_SECRET_ROTATION_CHECKLIST.md`](SECURITY_SECRET_ROTATION_CHECKLIST.md).

## المراحل

1. **Post-merge verification** — [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md)
2. **Staging** — [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md) + `scripts/smoke_staging.py`
3. **Compliance baseline** — [`DATA_MAP.md`](DATA_MAP.md)، [`PRIVACY_PDPL_READINESS.md`](PRIVACY_PDPL_READINESS.md)، DPA pilot
4. **Observability + evals** — [`OBSERVABILITY_ENV.md`](OBSERVABILITY_ENV.md)، [`EVALS_RUNBOOK.md`](EVALS_RUNBOOK.md)
5. **WhatsApp beta** — [`WHATSAPP_OPERATOR_FLOW.md`](WHATSAPP_OPERATOR_FLOW.md)، [`WHATSAPP_PRODUCTION_CUTOVER.md`](WHATSAPP_PRODUCTION_CUTOVER.md)
6. **Billing** — [`BILLING_RUNBOOK.md`](BILLING_RUNBOOK.md)
7. **Private beta** — [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md)
8. **Paid beta metrics** — [`PAID_BETA_SCORECARD.md`](PAID_BETA_SCORECARD.md)
9. **Go / No-Go عام** — [`PUBLIC_LAUNCH_GO_NO_GO.md`](PUBLIC_LAUNCH_GO_NO_GO.md)

## قاعدة التسمية

حتى تتحقق مدفوعات واستقرار وتشغيل: الإطلاق هو **Paid Private Beta** أو **Launch Candidate** وليس “Public Launch” كاملاً.

بعد الاستقرار التشغيلي للبيتا: راجع [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md) كطبقة تمييز منتجي/تسويقي (Growth Factory + مسارات `/api/v1/innovation/*` التجريبية) مقابل ما يبقى تنفيذاً عميقاً على بيانات العملاء.
