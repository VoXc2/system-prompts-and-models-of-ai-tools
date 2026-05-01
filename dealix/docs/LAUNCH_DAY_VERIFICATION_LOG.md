# سجل تنفيذ دليل يوم التدشين — Dealix

استخدم هذا الملف لتسجيل **نتائج فعلية** بعد كل جولة (محلي / staging / إنتاج). لا تلصق أسراراً هنا.

## آخر تشغيل محلي (آلي من الريبو)

| الخطوة | الأمر | النتيجة | التاريخ |
|--------|--------|---------|---------|
| compileall | `python -m compileall api auto_client_acquisition integrations db core -q` | OK | 2026-05-01 |
| pytest | `python -m pytest -q --no-cov` | 526 passed, 6 skipped | 2026-05-01 |
| print_routes | `python scripts/print_routes.py` | ROUTE_CHECK_OK no duplicate method+path | 2026-05-01 |
| smoke_inprocess | `python scripts/smoke_inprocess.py` | SMOKE_INPROCESS_OK | 2026-05-01 |

## Staging (يتطلب `STAGING_BASE_URL`)

| الخطوة | الأمر | النتيجة | التاريخ |
|--------|--------|---------|---------|
| smoke_staging | `STAGING_BASE_URL=https://... STAGING_API_KEY=... python scripts/smoke_staging.py` | *(نفّذ على خادمك؛ سجّل SMOKE_STAGING_OK هنا)* | |

يشمل الـ smoke الآن مسارات `innovation` (growth-missions، command-feed demo) بالإضافة للمسارات الأساسية.

راجع [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md).

## ملاحظات

- إذا فشل endpoint بسبب `401`، عيّن `STAGING_API_KEY` ليطابق `API_KEYS` في الخادم.
