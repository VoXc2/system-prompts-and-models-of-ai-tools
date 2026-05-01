# قائمة التدشين التجاري العام — Dealix

**للتنقل السريع أثناء التدشين:** [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md).

## قانوني

- [ ] سياسة خصوصية منشورة
- [ ] شروط استخدام
- [ ] DPA للشركات
- [ ] إجراءات PDPL (تصدير/حذف/قمع) موثقة ومُختبرة

## منتج

- [ ] صفحة تسعير عامة متسقة مع `pricing.py` و`PRICING_STRATEGY.md`
- [ ] Onboarding self-serve أو مبيعات داخلية قابلة للتكرار
- [ ] حدود استخدام واضحة (rate limits، quotas)

## فوترة

- [ ] Moyasar live + webhooks مراقَبة
- [ ] فواتير واسترداد محددة

## تشغيل

- [ ] SLOs (uptime، زمن استجابة API)
- [ ] on-call + runbooks (`docs/ops/DEPLOY_NOW.md` وملفات `docs/ops/`؛ الأرشيف: `docs/archive/runbook_lowercase_DEPRECATED.md`)
- [ ] نسخ احتياطي واختبار استعادة

## GTM

- [ ] مسار «أول 100» من `docs/GTM_PLAYBOOK.md`
- [ ] شراكات وكالة إن انطبقت

## معيار «جاهز للإطلاق العام»

- [ ] تجربة pilot ناجحة متكررة
- [ ] CI أخضر على `main`
- [ ] مراجعة أمنية خارجية (موصى بها)
