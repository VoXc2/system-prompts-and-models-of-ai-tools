# بوابات A–D — مرجع سريع للإنسان

التفاصيل الكاملة في [`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md). هذا الملف للتشيك السريع فقط.

---

## A — حماية GitHub

- [ ] قاعدة فرع على **`ai-company`** (أو الفرع المحمي المعتمد).
- [ ] يتطلب PR قبل الدمج.
- [ ] يتطلب checks خضراء كما تظهر في واجهة GitHub: عادة `pytest`، `smoke_inprocess`، `launch_readiness` من workflow Dealix API CI.
- [ ] منع force push وحذف الفرع المحمي.

مرجع: [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md)

---

## B — Railway Staging

- [ ] مشروع Railway من GitHub → الفرع المعتمد للنشر.
- [ ] **Service Root:** `dealix`
- [ ] **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] **Healthcheck:** `/health`
- [ ] متغيرات آمنة: `APP_ENV=staging`، `WHATSAPP_ALLOW_LIVE_SEND=false`، `MOYASAR_MODE=sandbox` (حسب سياسة شركتك).

مرجع: [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md) · [`RAILWAY_AI_COMPANY_BIND.md`](RAILWAY_AI_COMPANY_BIND.md)

---

## C — تحقق من جهازك

من مجلد `dealix` (بعد ضبط `STAGING_BASE_URL` بدون `/` زائدة في النهاية):

```powershell
$env:STAGING_BASE_URL="https://YOUR-STAGING-HOST"
py -3 scripts/smoke_staging.py --base-url $env:STAGING_BASE_URL
py -3 scripts/launch_readiness_check.py --base-url $env:STAGING_BASE_URL
```

- [ ] `smoke_staging.py` → exit 0
- [ ] `launch_readiness_check.py` → **VERDICT: PAID_BETA_READY** و exit 0

---

## D — GitHub Actions

- [ ] Secret في الريبو: **`STAGING_BASE_URL`**
- [ ] تشغيل workflow **Dealix staging smoke** يدوياً مرة على الأقل للتحقق.

مرجع: [`STAGING_WORKFLOW_GITHUB.md`](STAGING_WORKFLOW_GITHUB.md) · الملف: [`.github/workflows/dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml)
