# Targeting & Acquisition OS — Dealix

## الرؤية

طبقة تستهدف **الحسابات (Accounts)** أولاً ثم **لجنة الشراء** ثم **قابلية التواصل**، وتخرج خطط outreach ومسودات فقط — بدون scraping وبدون إرسال حي بدون موافقة. تكمل [`PLATFORM_SERVICES_STRATEGY.md`](PLATFORM_SERVICES_STRATEGY.md) و[`INTELLIGENCE_LAYER_STRATEGY.md`](INTELLIGENCE_LAYER_STRATEGY.md).

## الكود

| مسار | ملف |
|------|-----|
| `auto_client_acquisition/targeting_os/` | سياسات مصدر، contactability، حسابات تجريبية، LinkedIn المتوافق، جدولة، سمعة، تقارير |

## المسارات (`/api/v1/targeting/*`)

- `POST /accounts/recommend` — شركات تجريبية مرتبة بالقطاع/المدينة
- `POST /buying-committee/map` — أدوار قرار مقترحة
- `POST /contacts/evaluate` — `safe` / `needs_review` / `blocked`
- `POST /uploaded-list/analyze` — يمر عبر [`contact_import_preview`](../auto_client_acquisition/platform_services/contact_import_preview.py)
- `POST /outreach/plan` — خطوات بحدود يومية (MVP)
- `GET /daily-autopilot/demo` — بطاقات يومية (≤3 أزرار في العرض)
- `GET /self-growth/demo` — أهداف تشغيل ذاتي لـ Dealix (مسودات فقط)
- `GET /reputation/status` — مثال مقاييس + `should_pause`
- `POST /linkedin/strategy` — Lead Gen أولاً + `do_not_do`
- `GET /services` — عروض خدمات قابلة للبيع
- `POST /free-diagnostic` — 3 فرص + عرض pilot
- `GET /contracts/templates` — مخططات عقود **ليست استشارة قانونية**
- `POST /trust-score` — جسر إلى `compute_trust_score`
- `POST /account-strategy` — استراتيجية مصدر لكل حساب

## LinkedIn — المسموح والممنوع

- **ممنوع:** scraping، auto-DM، auto-connect، أتمتة غير أصيلة (انظر سياسات LinkedIn العامة).
- **مسموح:** Lead Gen Forms، إعلانات، مهام بحث يدوية معتمدة، بيانات العميل وCRM.

## WhatsApp

- لا cold outbound افتراضياً؛ opt-in واضح؛ راجع [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md).

## PDPL والمصادر

كل جهة تحتاج `source` وغرض معالجة؛ القوائم المشتراة أو المكشوفة **محظورة** في المصفوفة. التفاصيل التشغيلية في [`DATA_MAP.md`](DATA_MAP.md) و[`PRIVACY_PDPL_READINESS.md`](PRIVACY_PDPL_READINESS.md).

## الخدمات القابلة للبيع

انظر `GET /targeting/services` و[`service_catalog`](../auto_client_acquisition/platform_services/service_catalog.py) للمحاذاة مع كتالوج المنصة.

## الاختبارات

[`tests/test_targeting_os.py`](../tests/test_targeting_os.py)
