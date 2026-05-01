# خريطة الواجهة (Landing) وواجهة البرج والتحكم — Dealix

> الغرض: يعرف المشغّل أو الشريك التقني **أي صفحة HTML تغذيها أي مسارات API**، دون البحث في الريبو. المسارات المرجعية الكاملة: [`architecture/API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md).

## مبدأ البنية

| الطبقة | الموقع | الدور |
|--------|--------|--------|
| واجهة تسويق / عرض | [`landing/*.html`](../landing/) | HTML ثابت، غالباً `lang="ar"` و`dir="rtl"`. نسخ إنجليزية مختصرة: `*-en.html`. |
| برج النمو (Growth Control Tower) | طبقات `auto_client_acquisition` + مسارات `/api/v1/platform/*`، `/api/v1/intelligence/*`، `/api/v1/growth-operator/*`، `/api/v1/services/*`، `/api/v1/targeting/*` | قرار، Inbox، مهام، خدمات، استهداف — **بدون SPA واحد** في الريبو. |
| لوحة إيرادات (عرض) | [`command_center`](../api/routers/command_center.py) `GET /api/v1/command-center/*` | تغذية لوحة الإيرادات؛ صفحة [`command-center.html`](../landing/command-center.html) توثّق المسار `snapshot` كنموذج. |
| نظام v3 | [`v3`](../api/routers/v3.py) `/api/v1/v3/*` | طبقة «Revenue OS» تجريبية: وكلاء، امتثال، رادار، ذاكرة. |
| إطلاق البيتا والتحصيل | [`launch_ops`](../api/routers/launch_ops.py)، [`revenue_launch`](../api/routers/revenue_launch.py) | عروض، go/no-go، دفع يدوي، Proof — انظر [`REVENUE_TODAY_PLAYBOOK.md`](REVENUE_TODAY_PLAYBOOK.md). |

## جدول: صفحة → مسارات API ذات صلة

| صفحة (landing) | لغة | مسارات API (أمثلة) | ملاحظة |
|----------------|-----|----------------------|--------|
| [`index.html`](../landing/index.html) | ar | `/health`، روابط عامة | بوابة الموقع. |
| [`private-beta.html`](../landing/private-beta.html) | ar | `GET /api/v1/launch/private-beta/offer`، `GET /api/v1/revenue-launch/offer`، `GET /api/v1/growth-operator/missions`، `POST /api/v1/operator/chat/message`، `GET /api/v1/revenue-os/company-os/command-feed/demo` | تدشين Pilot + **Company OS**؛ [`private-beta-en.html`](../landing/private-beta-en.html) للإنجليزية. |
| [`private-beta-en.html`](../landing/private-beta-en.html) | en | نفس المسارات أعلاه | نسخة مختصرة LTR. |
| [`services.html`](../landing/services.html) | ar | `GET /api/v1/services/catalog`، `POST /api/v1/services/recommend` | برج الخدمات؛ [`services-en.html`](../landing/services-en.html). |
| [`services-en.html`](../landing/services-en.html) | en | نفس المسارات | |
| [`command-center.html`](../landing/command-center.html) | ar (محتوى مختلط في العناوين) | `GET /api/v1/command-center/snapshot?customer_id=...`، باقي مسارات [`command_center.py`](../api/routers/command_center.py) | عرض تسويقي؛ [`command-center-en.html`](../landing/command-center-en.html) مركز روابط EN. |
| [`command-center-en.html`](../landing/command-center-en.html) | en | نفس `command-center` + `GET /api/v1/v3/command-center/snapshot` إن وُجد في smoke | |
| [`free-diagnostic.html`](../landing/free-diagnostic.html) | ar | `POST /api/v1/targeting/free-diagnostic` | |
| [`first-10-opportunities.html`](../landing/first-10-opportunities.html) | ar | `POST /api/v1/intelligence/missions/first-10-opportunities` أو `POST /api/v1/innovation/opportunities/ten-in-ten` | انظر aliases. |
| [`list-intelligence.html`](../landing/list-intelligence.html) | ar | `POST /api/v1/targeting/uploaded-list/analyze` | |
| [`growth-os.html`](../landing/growth-os.html) | ar | `GET /api/v1/services/catalog`، مسارات Growth OS في الخدمات | |
| [`agency-partner.html`](../landing/agency-partner.html) | ar | `GET /api/v1/services/contracts/templates` | |
| [`launch-readiness.html`](../landing/launch-readiness.html) | ar | `GET /api/v1/launch/go-no-go`، `scripts/launch_readiness_check.py` | |

## لغة الـ API التجريبية

- **`GET /api/v1/revenue-launch/offer?lang=en`**: يضيف حقول `title_en` / `summary_en` (وأمثلة مشابهة) **إلى جانب** الحقول العربية `_ar` — لا يزيل الحقول العربية.

## تشغيل محلي للتحقق

من مجلد `dealix`:

```bash
python scripts/smoke_inprocess.py
python scripts/launch_readiness_check.py
```

Staging (يتطلب `STAGING_BASE_URL`):

```bash
python scripts/smoke_staging.py --base-url https://<your-staging-host>
```

## وثائق مرتبطة

- [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md)
- [`PRIVATE_BETA_LAUNCH_TODAY.md`](PRIVATE_BETA_LAUNCH_TODAY.md)
- [`DEALIX_100_PERCENT_LAUNCH_PLAN.md`](DEALIX_100_PERCENT_LAUNCH_PLAN.md)
- [`AUTONOMOUS_REVENUE_COMPANY_OS.md`](AUTONOMOUS_REVENUE_COMPANY_OS.md) — فئة المنتج والمسارات `/api/v1/operator/*` و`/api/v1/revenue-os/company-os/*`
