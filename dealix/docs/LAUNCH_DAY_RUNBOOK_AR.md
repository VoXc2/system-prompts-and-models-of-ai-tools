# دليل يوم التدشين — Dealix (فهرس تشغيلي)

> وثيقة **فهرس**؛ التفاصيل الطويلة في الملفات المرتبطة. نفّذ بالترتيب تقريباً من الأعلى للأسفل.

**بعد أي تسريب لمفتاح:** [`SECURITY_SECRET_ROTATION_CHECKLIST.md`](SECURITY_SECRET_ROTATION_CHECKLIST.md).  
**تسجيل نتائج التشغيل:** [`LAUNCH_DAY_VERIFICATION_LOG.md`](LAUNCH_DAY_VERIFICATION_LOG.md).  
**SOP يومي للإيراد:** [`ops/SOP_REVENUE_ENGINE_DAILY.md`](ops/SOP_REVENUE_ENGINE_DAILY.md).  
**تتبع الإطلاق العام:** [`PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md`](PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md).  
**بوابات البيتا (قائمة واحدة):** [`BETA_PRIVATE_GATES_CHECKLIST.md`](BETA_PRIVATE_GATES_CHECKLIST.md).  
**أسرار Actions:** [`ops/GITHUB_ACTIONS_ENV_SETUP.md`](ops/GITHUB_ACTIONS_ENV_SETUP.md).

## 0) قبل 24–48 ساعة

- [ ] اعتماد التسمية: راجع [`LAUNCH_SCOPE_AND_NAMING.md`](LAUNCH_SCOPE_AND_NAMING.md) (افتراضياً **Paid Private Beta**).
- [ ] تأكد أن فرع الإصدار مدمج والـ CI أخضر (انظر قسم «Staging و CI» أدناه).
- [ ] جهّز قناة حوادث (Slack/WhatsApp داخلي) ومسؤول on-call.

## 1) صباح يوم التدشين — تحقق تقني سريع (30–60 دقيقة)

| الخطوة | الإجراء | مرجع |
|--------|---------|------|
| 1 | من مجلد `dealix`: `python -m compileall api auto_client_acquisition db` | [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md) |
| 2 | `python -m pytest -q` (أو حسب CI) | نفس المرجع |
| 3 | `python scripts/print_routes.py` — لا تكرار مسارات | نفس المرجع |
| 4 | `python scripts/smoke_inprocess.py` | نفس المرجع |
| 5 | **Staging:** `STAGING_BASE_URL=...` وإن لزم `STAGING_API_KEY=...` ثم `python scripts/smoke_staging.py` | [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md) |
| 6 | **الإنتاج:** `API_KEYS` مضبوطة (لا تعتمد على وضع «بدون مفاتيح») | [`api/security/api_key.py`](../api/security/api_key.py) |

**Rollback:** إن فشل smoke أو staging، أوقف زيادة التعرّض (إيقاف إعلان، إرجاع نشر، أو تعطيل مفتاح API مؤقتاً) حسب [`docs/ops/DEPLOY_NOW.md`](ops/DEPLOY_NOW.md) إن وُجد.

## 2) البوابة القانونية والامتثال (قبل أول عميل إنتاج)

- [ ] سياسة خصوصية وشروط استخدام **منشورة** وروابطها في العقود/البريد.
- [ ] DPA pilot موقّع أو مسار توقيع جاهز: [`DPA_PILOT_TEMPLATE.md`](DPA_PILOT_TEMPLATE.md).
- [ ] اختبر على **staging** مسارات PDPL (تصدير/حذف/قمع) حسب [`PRIVACY_PDPL_READINESS.md`](PRIVACY_PDPL_READINESS.md)، [`DATA_MAP.md`](DATA_MAP.md)، [`SECURITY_PDPL_CHECKLIST.md`](SECURITY_PDPL_CHECKLIST.md).

## 3) الفوترة

- [ ] Sandbox ثم live حسب [`BILLING_RUNBOOK.md`](BILLING_RUNBOOK.md).
- [ ] Webhooks مراقَبة؛ فشل الدفع لا يُترك بلا تصعيد.

## 4) واتساب (إن وُجد إنتاج)

- [ ] لا إرسال حي بدون opt-in وبوابات: [`WHATSAPP_OPERATOR_FLOW.md`](WHATSAPP_OPERATOR_FLOW.md).
- [ ] القطع الإنتاجي: [`WHATSAPP_PRODUCTION_CUTOVER.md`](WHATSAPP_PRODUCTION_CUTOVER.md).
- [ ] في البيتا: `WHATSAPP_ALLOW_LIVE_SEND` وفق [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md).

## 5) البيتا الخاصة — تشغيل العملاء

- [ ] 5–10 عملاء، قطاع محدود، أسبوع 1–2 حسب [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md).
- [ ] بعد الجولة: [`PAID_BETA_SCORECARD.md`](PAID_BETA_SCORECARD.md) ثم [`PUBLIC_LAUNCH_GO_NO_GO.md`](PUBLIC_LAUNCH_GO_NO_GO.md) للإطلاق العام.

## 6) GTM وسريان المبيعات

- [`GTM_PLAYBOOK.md`](GTM_PLAYBOOK.md)، [`business/FOUNDER_LAUNCH_KIT.md`](business/FOUNDER_LAUNCH_KIT.md).
- تمييز منتج لاحقاً: [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md)، [`DEALIX_100_PERCENT_LAUNCH_PLAN.md`](DEALIX_100_PERCENT_LAUNCH_PLAN.md) (§31).

## 7) بعد يوم التدشين (48 ساعة)

- [ ] راجع السجلات والمراقبة: [`OBSERVABILITY_ENV.md`](OBSERVABILITY_ENV.md).
- [ ] حدث [`LAUNCH_READINESS_REPORT.md`](LAUNCH_READINESS_REPORT.md) أو أعد توليده عند توفر أرقام إنتاج.
- [ ] اجتماع قصير: ما انكسر، ما تعلّمنا، ما نغيّر في الأسبوع القادم.

---

**قائمة الإطلاق العام الكاملة:** [`PUBLIC_LAUNCH_CHECKLIST.md`](PUBLIC_LAUNCH_CHECKLIST.md).
