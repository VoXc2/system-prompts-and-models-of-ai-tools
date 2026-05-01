# ربط Railway — مسار AI Company (`ai-company`)

نفّذ في [لوحة Railway](https://railway.app) بعد أن يكون الفرع [`ai-company`](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/tree/ai-company) مرفوعاً على GitHub.

## 1) المشروع والخدمة

1. **New Project** → **Deploy from GitHub** → اختر `VoXc2/system-prompts-and-models-of-ai-tools`.
2. أنشئ خدمة **Web** (أو عدّل الخدمة الحالية) لتشغيل Dealix API.

## 2) إعدادات النشر (إلزامي)

| الحقل | القيمة |
|--------|--------|
| **Branch** | `ai-company` |
| **Root Directory** | `dealix` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}` |

مرجع: [`STAGING_DEPLOYMENT.md`](../STAGING_DEPLOYMENT.md).

## 3) قاعدة البيانات

1. أضف **PostgreSQL** من Railway أو استخدم `DATABASE_URL` خارجي.
2. اربط متغير **`DATABASE_URL`** بخدمة التطبيق (غالباً يُحقن تلقائياً عند الربط).

## 4) متغيرات البيئة

- انسخ **الأسماء** من [`.env.staging.example`](../../.env.staging.example) (staging) أو [`.env.example`](../../.env.example) (production لاحقاً).
- لا تُرفع `.env` إلى Git.
- تأكد من: `APP_SECRET_KEY`, `APP_URL`, `APP_ENV`, `CORS_ORIGINS`, `MOYASAR_*`، و`DAILY_EMAIL_LIMIT` (وليس `EMAIL_DAILY_LIMIT`)، و`WHATSAPP_ALLOW_LIVE_SEND=false` للبيتا حتى الموافقة.

## 5) التحقق بعد النشر

1. المتصفح: `https://<your-host>/health` → 200.
2. محلياً: `STAGING_BASE_URL=https://<host>` ثم `python scripts/smoke_staging.py` من مجلد `dealix`.
3. GitHub Actions: شغّل يدوياً **Dealix staging smoke** بعد ضبط أسرار `STAGING_BASE_URL` / `STAGING_API_KEY` — انظر [`GITHUB_ACTIONS_ENV_SETUP.md`](GITHUB_ACTIONS_ENV_SETUP.md).

## 6) مسار Git الكامل

[`GITHUB_AI_COMPANY_TRACK.md`](GITHUB_AI_COMPANY_TRACK.md)
