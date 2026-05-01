# نشر Staging — Dealix API

مسار GitHub الموصى لخط «AI Company» والفرع `ai-company`: [`docs/ops/GITHUB_AI_COMPANY_TRACK.md`](ops/GITHUB_AI_COMPANY_TRACK.md).  
ربط Railway خطوة بخطوة: [`docs/ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md).

## منصة موصى بها

**Railway** (أو **Render** كبديل).

## أمر التشغيل

```bash
uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

على Railway غالباً `PORT` يُحقن تلقائياً.

## Healthcheck

- المسار: **`GET /health`**
- يتوقع `200` وJSON فيه `status`.

## متغيرات بيئة (مثال)

- `APP_ENV=staging`
- `DATABASE_URL` / إعدادات DB إن وُجدت
- `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (سيرفر فقط)
- مفاتيح LLM إن لزم للتجارب
- **لا** تضع `MOYASAR_SECRET` أو أسرار في المتغيرات العامة للواجهة

### Growth Control Tower / قنوات (موصى به على staging)

- `WHATSAPP_ALLOW_LIVE_SEND=false` — يبقى معطّلاً حتى اكتمال webhook وopt-in والمراجعة القانونية (انظر [`core/config/settings.py`](../core/config/settings.py)).
- `MOYASAR_MODE=sandbox` (أو اسم متغير معادل عندك) — **تسمية تشغيلية** للفريق؛ مسارات API الحالية تبقى مسودات/تحقق فقط بدون charge حي ما لم تُضف تكامل إنتاجي صراحةً.
- `SENTRY_DSN` — للتقاط أخطاء staging (اختبار عبر `GET /api/v1/admin/sentry-check` حيث يُسمح).
- مفاتيح **Langfuse** إن استخدمت المراقبة: لا تُسجَّل في الريبو؛ ضعها كأسرار Railway فقط.

### بوابة جاهزية الإطلاق (GO / NO-GO)

**CI على الاستضافة:** من GitHub Actions شغّل workflow **Dealix staging smoke** (يدوي) بعد ضبط السر `STAGING_BASE_URL` — يشغّل `smoke_staging.py` ثم `launch_readiness_check.py --base-url` ويتوقع **`PAID_BETA_READY`** عند نجاح كل الفحوص. تفاصيل الفروع: [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md).

بعد ضبط `STAGING_BASE_URL` (أو تمرير `--base-url`):

```bash
python scripts/launch_readiness_check.py --base-url "https://YOUR-STAGING-URL"
```

توقّع **`VERDICT: PAID_BETA_READY`** وexit code `0` عندما تمر كل فحوصات الشبكة نفسها التي يمرّرها السكربت محلياً (`customer-ops`، `services/catalog`، `launch/private-beta/offer`، `security-curator/demo`، إلخ). للتحقق المحلي فقط بدون URL: `python scripts/launch_readiness_check.py` → **`GO_PRIVATE_BETA`**.

### Smoke — مسارات إضافية للتحقق يدوياً

بعد `GET /health` و`smoke_staging.py`، يُنصح بالتحقق من وجود:

- `GET /api/v1/platform/service-catalog`
- `GET /api/v1/platform/inbox/feed`
- `GET /api/v1/platform/proof/overview`
- `GET /api/v1/intelligence/command-feed` (أو `/command-feed/demo`)
- `POST /api/v1/innovation/opportunities/ten-in-ten` أو alias `POST /api/v1/intelligence/missions/first-10-opportunities`
- `GET /api/v1/services/catalog`، `GET /api/v1/services/verticals`، `GET /api/v1/launch/go-no-go`، `GET /api/v1/launch/scorecard`
- `GET /api/v1/revenue-launch/offer`، `GET /api/v1/revenue-launch/payment/manual-flow` (عروض Pilot ودفع يدوي فقط — انظر [`REVENUE_TODAY_PLAYBOOK.md`](REVENUE_TODAY_PLAYBOOK.md))

خريطة كاملة للمرادفات: [`docs/architecture/API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md).

## Smoke بعد النشر

من جهازك (مسارات GET الحرجة، بدون أسرار في الريبو):

```bash
set STAGING_BASE_URL=https://<staging-host>
python scripts/smoke_staging.py
```

أو:

```bash
python scripts/smoke_local_api.py --base-url https://<staging-host>
```

قالب متغيرات staging (بدون قيم حقيقية): [`.env.staging.example`](../.env.staging.example).

Smoke يدوي من GitHub: `.github/workflows/staging-smoke.yml` بعد ضبط السر `STAGING_BASE_URL`.

## Rollback

- إعادة نشر commit سابق في Railway/Render.
- إبقاء migration منفصلة عن كود التطبيق؛ عند الحاجة تراجع SQL يدوياً.

## ملاحظة

لا يُرفع ملف `railway.toml` هنا حتى لا يتعارض مع إعداد موجود لديك؛ أنشئ الخدمة من لوحة Railway واربط الريبو.
