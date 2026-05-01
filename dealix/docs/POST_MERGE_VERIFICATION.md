# Post-merge verification — Dealix

Run this checklist **after** PR #125 is merged into `main` (or when validating the release branch). Record fresh numbers below.

## Preconditions

1. Revoke any exposed GitHub PAT (see [`SECURITY_INCIDENT_PAT_EXPOSURE.md`](SECURITY_INCIDENT_PAT_EXPOSURE.md)).
2. Merge completed **only** from GitHub UI (no `--force` on shared branches).
3. Local checkout updated: `git checkout main && git pull`.

## Commands (reference)

نفّذ من مجلد `dealix` (جذر حزمة التطبيق) بعد `cd dealix`:

```bash
python -m compileall api auto_client_acquisition integrations db core
pytest -q --no-cov
python scripts/print_routes.py
python scripts/smoke_inprocess.py
```

**بوابة الإطلاق:** بعد الدمج، شغّل أيضاً `scripts/smoke_staging.py` على staging مع `STAGING_BASE_URL` — انظر [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md).

**Runbook تنفيذ كامل (GitHub → Railway → PAID_BETA_READY → أول عميل → Proof Pack):** [`PAID_BETA_FULL_RUNBOOK_AR.md`](PAID_BETA_FULL_RUNBOOK_AR.md).

Optional secret-pattern scan (adapt to your environment):

```bash
rg "ghp_|github_pat_|sk_live_" --glob '!htmlcov/**' --glob '!.venv/**'
```

## Growth Control Tower — Wave 0 (baseline)

بعد إضافة مسارات `/api/v1/platform/*` و`/api/v1/intelligence/*` أعد تشغيل نفس الأوامر أعلاه وتأكد من `ROUTE_CHECK_OK`. Staging: [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md) و[`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md).

## Launch Ops + Service Tower (خرائط ثابتة)

- تأكد من: `GET /api/v1/launch/private-beta/offer`، `GET /api/v1/launch/go-no-go`، `GET /api/v1/services/verticals`، `GET /api/v1/services/contracts/templates`.
- `scripts/smoke_staging.py` يتضمن هذه المسارات عند التحقق من staging.

## Frontend map + لغتين (Landing / EN)

- مرجع المشغّل: [`FRONTEND_AND_API_MAP.md`](FRONTEND_AND_API_MAP.md) — يربط `landing/*.html` بمسارات البرج والتحكم.
- صفحات إنجليزية مختصرة: `landing/private-beta-en.html`، `services-en.html`، `command-center-en.html` مع روابط من العربية.
- **Revenue offer i18n:** `GET /api/v1/revenue-launch/offer?lang=en` يضيف `title_en` / `summary_en` (وحقول إنجليزية موازية للقوائم حيث وُجدت) مع الإبقاء على الحقول العربية.

## Last recorded run (workspace snapshot)

### Snapshot A — قبل الدمج (للمرجع)

| Step | Result |
|------|--------|
| Git HEAD | `16e8ba2` on branch `ai-company` (re-run on `main` after merge) |
| compileall | OK (`api`, `auto_client_acquisition`, `db`, `core`) |
| pytest | `652 passed`, `6 skipped`, `0 failed` (`APP_ENV=test`, dummy LLM keys) — 2026-05-01 بعد `launch_readiness` + تكامل الواجهات؛ أعد التشغيل بعد الدمج |

### Snapshot B — على default branch بعد الدمج (الأحدث · 2026-05-01 محلياً)

| Step | Result |
|------|--------|
| Git HEAD | `41ca592` (re-run after merge on your default branch) |
| compileall | OK (`api`, `auto_client_acquisition`, `integrations`, `db`, `core`) |
| pytest | `791 passed`, `6 skipped`, `0 failed` (`APP_ENV=test`, `--no-cov`) — 6 skipped: E2E يحتاج سيرفر على `8001`، مزوّدون اختياريون بدون مفاتيح |
| `print_routes.py` | `ROUTE_CHECK_OK no duplicate method+path` |
| `smoke_inprocess.py` | `SMOKE_INPROCESS_OK` (يشمل `GET /api/v1/revenue-launch/offer` و`GET /api/v1/revenue-launch/offer?lang=en`) |
| `launch_readiness_check.py` | `VERDICT: GO_PRIVATE_BETA`، exit `0` — يفحص محلياً: `/health`، customer-ops (checklist/sla/connectors)، `services/catalog` (حقول التسعير وProof لكل خدمة)، `launch/private-beta/offer`، `security-curator/demo`، ملفات `landing/companies\|marketers\|private-beta.html`، و`WHATSAPP_ALLOW_LIVE_SEND=false`. مع `--base-url` أو `STAGING_BASE_URL`: نفس المسارات عن بُعد → `PAID_BETA_READY` إذا نجحت كلها؛ وإلا `NO_GO`. اختياري: `--secrets` لفحص أنماط تسرّب شائعة. `--json` لمخرجات آلة |
| Secret-pattern scan | `ghp_` / `github_pat_` / `sk_live_` — التطابقات الظاهرة في الريبو هي وثائق تشغيل، أمثلة اختبار، أو regex للكشف؛ ليست بالضرورة تسريباً. راجع `docs/ops/*` دورياً |
| `smoke_staging.py` | يتطلب `STAGING_BASE_URL` — يشمل الآن `…/revenue-launch/offer?lang=en`؛ شغّله على الاستضافة الفعلية قبل أول عميل |
| Frontend + EN + `?lang=en` | وثّق في [`FRONTEND_AND_API_MAP.md`](FRONTEND_AND_API_MAP.md) — أعد `pytest` بعد أي تغيير على `revenue_launch` |

### Verified-from-clone re-run (2026-05-01, sandbox clone of `sync/dealix-full-complete` @ `41ca592`)

| Step | Result |
|------|--------|
| compileall (`api`, `auto_client_acquisition`, `integrations`, `db`, `core`) | OK |
| pytest -q --no-cov (`APP_ENV=test`) | `779 passed`, `6 skipped` — يطابق Snapshot B بـ 12 اختباراً أقل؛ السبب: الـ12 المضافة تأتي من ملفات `tests/test_paid_beta_daily_scorecard.py` المحدّثة محلياً غير المرفوعة |
| `print_routes.py` | `ROUTE_CHECK_OK no duplicate method+path` |
| `smoke_inprocess.py` | `SMOKE_INPROCESS_OK` |
| `launch_readiness_check.py` | `VERDICT: GO_PRIVATE_BETA` |

## CI

Confirm GitHub Actions workflow [`.github/workflows/dealix-api-ci.yml`](../../.github/workflows/dealix-api-ci.yml) is green on the merged commit (jobs: `pytest`, `smoke_inprocess`, `launch_readiness`). لإعداد **branch protection** وأسماء الـ checks: [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md).

### Snapshot C — v1 closure train (2026-05-02, `ai-company` after Layer 13/14 merge)

| Step | Result |
|------|--------|
| Merge PR | [#30](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/pull/30) merged into `ai-company` — merge commit `c95179e` |
| Dealix API CI on PR | `pytest` / `smoke_inprocess` / `launch_readiness` — **pass** (run `25232625374`) |
| Branch protection (`ai-company`) | Verified: required contexts `pytest`, `smoke_inprocess`, `launch_readiness`; PR required; no force-push |
| Local re-run (`APP_ENV=test`, `--no-cov`) | `797 passed`, `6 skipped` on merge tip |
| `print_routes.py` | `ROUTE_CHECK_OK no duplicate method+path` |
| `smoke_inprocess.py` | `SMOKE_INPROCESS_OK` |
| `launch_readiness_check.py` (local) | `GO_PRIVATE_BETA` — لتعيين `PAID_BETA_READY` شغّل نفس السكربت مع `--base-url` على URL staging بعد Railway |

**ملاحظة workflow:** ملف [`.github/workflows/dealix-staging-smoke.yml`](../../.github/workflows/dealix-staging-smoke.yml) قد لا يظهر في `gh workflow list` إذا كان **الفرع الافتراضي للريبو** لا يحتويه؛ GitHub يحمّل تعريفات الـ workflows من الفرع الافتراضي. للـ `workflow_dispatch` من الواجهة أو الـ CLI، إمّا نقل/مزامنة الـ workflow إلى `main` أو تغيير الفرع الافتراضي مؤقتاً — راجع سياسة الفريق.

## Manual follow-ups (not automated)

- ~~Merge Layer 13/14 into `ai-company`~~ — تم عبر PR [#30](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/pull/30).
- **Railway:** انشر من فرع `ai-company`، root `dealix`، حسب [`PAID_BETA_FULL_RUNBOOK_AR.md`](PAID_BETA_FULL_RUNBOOK_AR.md) و[`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md).
- **Secrets + staging smoke:** أضف `STAGING_BASE_URL` في GitHub Actions ثم شغّل smoke يدوياً من الواجهة إن لم يظهر الـ workflow في `gh workflow list`.
- Deploy staging and run [`scripts/smoke_staging.py`](../scripts/smoke_staging.py) with `STAGING_BASE_URL` set.
- **Moyasar + outreach + Proof Pack:** اتبع [`PAID_BETA_FULL_RUNBOOK_AR.md`](PAID_BETA_FULL_RUNBOOK_AR.md) المراحل E–J.
