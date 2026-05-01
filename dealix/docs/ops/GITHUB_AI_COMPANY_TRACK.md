# مسار GitHub «AI Company» — Dealix (`ai-company`)

**الاسم التسويقي:** AI Company (Dealix / AI Company Saudi في الإعدادات).  
**اسم الفرع في Git:** `ai-company` (بدون مسافات؛ متوافق مع Git وRailway).

## ماذا يفعل هذا المسار

- **Railway + Git:** اضبط خدمة Dealix لتنشر من الفرع **`ai-company`** (أو افتح PR منه إلى `main` حسب سياستك).
- **CI:** Workflow جذر الريبو [`dealix-api-ci.yml`](../../../.github/workflows/dealix-api-ci.yml) يعمل على دفع أو PR إلى `main` أو **`ai-company`** أو `dealix-v3-autonomous-revenue-os` عند تغيّر مسارات `dealix/**`.
- **دخان Staging:** [`dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml) — يدوي؛ أسرار `STAGING_BASE_URL` واختياري `STAGING_API_KEY`.
- **Daily Revenue Machine:** [`dealix-daily-revenue-machine.yml`](../../../.github/workflows/dealix-daily-revenue-machine.yml) — يحتاج `DEALIX_API_BASE` و `DEALIX_API_KEY`. جدولة GitHub تعمل من **الفرع الافتراضي** للريبو (غالباً `main`)؛ راجع تعليق الملف.

## خطوات عندك (مرة)

1. أنشئ الفرع من آخر `main` (أو من فرعك الحالي):
   ```bash
   git checkout main
   git pull
   git checkout -b ai-company
   ```
2. تأكد أن مجلد **`dealix/`** مضاف ومُدفع إلى GitHub (غير متجاهل في `.gitignore` الجذر).
3. ادفع الفرع:
   ```bash
   git push -u origin ai-company
   ```
4. في **Railway:** Settings → Deploy → **Branch** = `ai-company`، و **Root Directory** = `dealix`.
5. في **Cursor Cloud Agents** (إن استخدمته): اضبط المستودع/الفرع الافتراضي إلى `ai-company` إن أردت أن يكون هذا خط الإصدار الرئيسي للوكيل.

## تنبيه مهم (مونوريبو)

GitHub **لا** يشغّل workflows من `dealix/.github/workflows/` كمصدر رسمي؛ النسخ **الفعّالة** تحت [`.github/workflows/`](../../../.github/workflows/) في جذر  
`system-prompts-and-models-of-ai-tools`. نُحتفظ بنسخ داخل `dealix/.github` كمرجع أو للتطوير المحلي — راجع [README](../../.github/workflows/README.md) في ذلك المجلد.

## الريبو العام

[https://github.com/VoXc2/system-prompts-and-models-of-ai-tools](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools)

## Railway (خطوات اللوحة)

[`RAILWAY_AI_COMPANY_BIND.md`](RAILWAY_AI_COMPANY_BIND.md)

## أسرار GitHub Actions

[`GITHUB_ACTIONS_ENV_SETUP.md`](GITHUB_ACTIONS_ENV_SETUP.md)
