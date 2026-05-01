# تتبع تنفيذ خطة الإطلاق — Dealix

لا يُعدّل ملف الخطة في `.cursor/plans/`؛ هذا الملف هو مرجع التنفيذ في الريبو.

## Phase 0 — إغلاق PR #125

| البند | الحالة | المرجع |
|-------|--------|---------|
| CI | يُتحقق بعد الدمج | `.github/workflows/ci.yml` |
| Smoke داخل العملية (بدون منفذ) | مضاف | `scripts/smoke_inprocess.py` |
| Smoke على منفذ محلي | اختياري | `uvicorn` + `scripts/smoke_local_api.py` |
| توثيق تثبيت | | `docs/PR125_FINAL_STABILIZATION_REPORT.md` |

## Phase 1 — Staging + Supabase + مراقبة

| البند | الحالة | المرجع |
|-------|--------|---------|
| نشر staging | تشغيلي | `docs/STAGING_DEPLOYMENT.md` |
| Supabase | تشغيلي | `docs/SUPABASE_STAGING_RUNBOOK.md`، الهجرة تحت `supabase/migrations/` |
| Embeddings | مسار موثّق + placeholder | `docs/EMBEDDINGS_PIPELINE.md`، `scripts/embeddings_pipeline_placeholder.py` |
| مراقبة | متغيرات | `docs/OBSERVABILITY_ENV.md`، `docs/AI_OBSERVABILITY_AND_EVALS.md` |

## Phase 2 — Private beta

| البند | الحالة | المرجع |
|-------|--------|---------|
| قائمة تنفيذ | | `docs/PHASE2_PRIVATE_BETA_CHECKLIST.md` |
| GTM | | `docs/GTM_PLAYBOOK.md` |
| واتساب | | `docs/WHATSAPP_OPERATOR_FLOW.md` |
| PDPL | | `docs/SECURITY_PDPL_CHECKLIST.md` |

## Phase 3 — مدفوع + Moyasar

| البند | الحالة | المرجع |
|-------|--------|---------|
| Moyasar | | `docs/BILLING_MOYASAR_RUNBOOK.md`، `docs/MOYASAR_LIVE_CUTOVER.md` |
| DPA pilot | مسودة | `docs/DPA_PILOT_TEMPLATE.md` |
| Onboarding | | `docs/ONBOARDING_FLOW.md` |

## Phase 4 — إطلاق عام

| البند | الحالة | المرجع |
|-------|--------|---------|
| قائمة | | `docs/PUBLIC_LAUNCH_CHECKLIST.md` |
