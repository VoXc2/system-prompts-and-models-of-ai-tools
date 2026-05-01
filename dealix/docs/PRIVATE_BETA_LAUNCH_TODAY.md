# Private Beta — «اليوم» (تشغيل وبيع)

قائمة تشغيل قبل أول عميل بيتا. تفاصيل تقنية إضافية: [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md). ديمو ١٢ دقيقة: [`DEMO_SCRIPT_12_MINUTES.md`](DEMO_SCRIPT_12_MINUTES.md). رسائل أول ٢٠: [`FIRST_20_OUTREACH_MESSAGES.md`](FIRST_20_OUTREACH_MESSAGES.md).

## ما ندشّنه اليوم

- **Private Beta** (ليس إطلاقاً عاماً): عرض Pilot + قيمة واضحة + موافقات.
- **أربعة عروض أولى:** تشخيص مجاني، ذكاء قوائم، سباق ١٠ فرص، Growth OS Pilot — انظر [`landing/services.html`](../landing/services.html).
- **نسختان للصفحات الحرجة:** [`landing/private-beta-en.html`](../landing/private-beta-en.html)، [`landing/services-en.html`](../landing/services-en.html)، [`landing/command-center-en.html`](../landing/command-center-en.html) — روابط «English» من الصفحات العربية المقابلة. خريطة كاملة: [`FRONTEND_AND_API_MAP.md`](FRONTEND_AND_API_MAP.md).
- **Autonomous Revenue Company OS:** مرجع الفئة والطبقات — [`AUTONOMOUS_REVENUE_COMPANY_OS.md`](AUTONOMOUS_REVENUE_COMPANY_OS.md)؛ واجهة تشغيل تجريبية: `GET /api/v1/operator/bundles`، `POST /api/v1/operator/chat/message`؛ طبقة أحداث وبطاقات: `GET /api/v1/revenue-os/company-os/command-feed/demo`.

## ما لا ندشّنه اليوم

- إرسال واتساب جماعي بارد، Gmail إرسال تلقائي، إدراج تقويم حي بدون موافقة، شحن بطاقات داخل المنتج، scraping LinkedIn.

## بيئة

- [ ] Staging يعمل (`GET /health`).
- [ ] `WHATSAPP_ALLOW_LIVE_SEND=false` (افتراضي) ما لم يُوثَّق خلاف ذلك.
- [ ] أسرار Moyasar / Google / Meta **غير** مكشوفة في الريبو أو اللوجات.

## API سريعة للتحقق

- [ ] `GET /api/v1/growth-operator/missions`
- [ ] `GET /api/v1/platform/inbox/feed`
- [ ] `GET /api/v1/platform/proof/overview`
- [ ] `POST /api/v1/platform/events/ingest` مع `source: trusted_simulation`
- [ ] `GET /api/v1/security-curator/demo`
- [ ] `GET /api/v1/services/catalog`
- [ ] `GET /api/v1/launch/go-no-go` و `GET /api/v1/launch/scorecard`
- [ ] `GET /api/v1/revenue-launch/offer` و `GET /api/v1/revenue-launch/offer?lang=en` (تسميات إنجليزية إضافية بجانب العربية)

## Go / No-Go (آلي demo)

شغّل `GET /api/v1/launch/go-no-go` بعد `pytest` و`print_routes`. تحذير staging متوقع حتى يُفعّل `STAGING_BASE_URL` في `smoke_staging.py`.

## تحقق آلي (مرجع الجلسة)

من مجلد `dealix`: `python -m pytest -q --no-cov`، ثم `python scripts/smoke_inprocess.py`، ثم `python scripts/launch_readiness_check.py`. بعد نشر staging: `python scripts/smoke_staging.py --base-url https://<host>`. سجّل النتائج في [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md).

## عملية بشرية

- [ ] اتفاق pilot موقّع (نطاق، PDPL، قنوات مسموحة).
- [ ] مسؤول مراجعة لكل «إرسال» أو «دفع» خارجي.
- [ ] قناة دعم للعميل (واتساب أو إيميل داخلي).

## بعد الجلسة الأولى

- صدّر ملاحظات إلى `growth-curator` و`meeting-intelligence` كتحسين لمسودات الأسبوع التالي.

## الصفحات (عرض)

- [`landing/private-beta.html`](../landing/private-beta.html)
- [`landing/list-intelligence.html`](../landing/list-intelligence.html)
- [`landing/growth-os.html`](../landing/growth-os.html)

## الإطلاق التجاري الأوسع

انظر [`COMMERCIAL_LAUNCH_MASTER_PLAN.md`](COMMERCIAL_LAUNCH_MASTER_PLAN.md).
