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
