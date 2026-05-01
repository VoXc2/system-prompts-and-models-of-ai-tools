# Staging — من Railway إلى `PAID_BETA_READY` (أوامر جاهزة)

**الشرط:** خدمة Dealix منشورة على URL عام (مثلاً Railway)، `Service Root = dealix`، و:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Healthcheck على `/health` يعيد `200`.

**لا تضع شرطة مائلة أخيرة** على `STAGING_BASE_URL` إن أمكن.

---

## 1) من جذر حزمة `dealix`

### PowerShell (Windows)

```powershell
$env:STAGING_BASE_URL = "https://YOUR-STAGING-HOST"
python scripts/smoke_staging.py --base-url $env:STAGING_BASE_URL
python scripts/launch_readiness_check.py --base-url $env:STAGING_BASE_URL
```

### bash

```bash
export STAGING_BASE_URL="https://YOUR-STAGING-HOST"
python scripts/smoke_staging.py --base-url "$STAGING_BASE_URL"
python scripts/launch_readiness_check.py --base-url "$STAGING_BASE_URL"
```

إذا فرض الـ staging مفتاح API:

```bash
export STAGING_API_KEY="your-staging-key"
```

(يُرسل كـ `X-API-Key` — انظر [`scripts/smoke_staging.py`](../../scripts/smoke_staging.py).)

---

## 2) علامة النجاح

```text
smoke_staging.py → exit 0
launch_readiness_check.py → VERDICT: PAID_BETA_READY و exit 0
```

إذا `NO_GO`: راجع مخرجات السكربت (مسارات، landing، `WHATSAPP_ALLOW_LIVE_SEND`, كتالوج الخدمات) قبل أي بيع.

---

## 3) Railway (تلخيص)

| إعداد | القيمة |
|--------|--------|
| Branch | `ai-company` |
| Root | `dealix` |
| Start | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Health | `/health` |
| متغيرات أولية | `APP_ENV=staging`, `WHATSAPP_ALLOW_LIVE_SEND=false` + مفاتيح اختبار حسب القوالب |

تفاصيل إضافية: [`RAILWAY_AI_COMPANY_BIND.md`](RAILWAY_AI_COMPANY_BIND.md) و[`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md).
