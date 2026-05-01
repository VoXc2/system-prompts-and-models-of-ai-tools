# أسرار GitHub Actions — Dealix

**المسار في GitHub:** Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

الريبو: [VoXc2/system-prompts-and-models-of-ai-tools](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/settings/secrets/actions).

## دخان Staging (يدوي)

| السر | الوصف |
|------|--------|
| `STAGING_BASE_URL` | أصل HTTPS للتطبيق المنشور، بدون شرطة مائلة أخيرة (مثلاً `https://xxx.up.railway.app`) |
| `STAGING_API_KEY` | اختياري؛ إذا فرض التطبيق `X-API-Key` على الطلبات |

Workflow: [`.github/workflows/dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml) — من تبويب **Actions** اختر **Dealix staging smoke** → **Run workflow**.

## Daily Revenue Machine

| السر | الوصف |
|------|--------|
| `DEALIX_API_BASE` | أصل الـ API (مثل `https://host` بدون `/` زائدة) |
| `DEALIX_API_KEY` | مفتاح يُرسل كـ `Authorization: Bearer …` |

Workflow: [`.github/workflows/dealix-daily-revenue-machine.yml`](../../../.github/workflows/dealix-daily-revenue-machine.yml).  
**جدولة cron:** تعمل من **الفرع الافتراضي** للريبو (غالباً `main`)؛ راجع تعليق الملف.

## CI الأساسي

**Dealix API CI** لا يحتاج أسرار للاختبارات الافتراضية (مفاتيح وهمية داخل YAML). لا تضع مفاتيح إنتاج في CI.
