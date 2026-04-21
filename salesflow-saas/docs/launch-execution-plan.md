# Dealix Launch Execution Plan (PR16 + PR17)

## Objective
تشغيل إطلاق Dealix بشكل مُحكَم بعد دمج مساري:
1. **PR #16 — Local AI Integration**
2. **PR #17 — Launch Readiness Kit**

> **Dependency Rule:** لا يتم دمج أو تطبيق PR #17 قبل PR #16 لأن الجاهزية التشغيلية في #17 تعتمد على توفر البنية المحلية للنماذج.

## Phase 0 — Governance & Access
- تأكيد صلاحيات الدمج على مستودع **VoXc2/dealix**.
- تعيين مسؤول نهائي لكل مسار: Product / Eng / Ops / Sales.
- تجميد تغييرات غير مرتبطة بالإطلاق لمدة 48 ساعة قبل go-live.

## Phase 1 — Merge Sequence (Mandatory)
1. مراجعة PR #16 (checks + review + conflict-free merge).
2. بعد نجاح #16 على `main`: مراجعة PR #17 ثم دمجه.
3. توثيق SHA لكل دمج في سجل الإطلاق.

### Merge Log Template
- PR #16 merge commit: `________`
- PR #17 merge commit: `________`
- merged by: `________`
- datetime (UTC): `________`

## Phase 2 — Environment Sync
على السيرفر:

```bash
git fetch --all
git checkout main
git pull --ff-only
```

ثم تشغيل خدمات المنظومة حسب بيئة النشر:
- Backend API
- Worker/Celery
- Redis
- Database migrations (إن وجدت)
- Frontend build/restart

## Phase 3 — Local AI Readiness (PR #16)

### Critical checks
- صحة إعدادات Ollama endpoint.
- صحة routing بين provider المحلي والبديل fallback.
- نجاح health checks للنماذج المحلية.
- اختبار timeout/retry عند الضغط.

### Pass criteria
- Latency مقبولة ضمن SLA الداخلي.
- No hard failures في مسار inference المحلي.
- Fallback يعمل تلقائياً عند تعطل النموذج المحلي.

## Phase 4 — Launch Readiness Enablement (PR #17)

### Activate launch kit docs/process
- QA acceptance checklist
- Operations runbook
- Sales launch kit
- Metrics dashboard cadence

### Cross-team dry run
- سيناريو onboarding عميل جديد.
- سيناريو lead → opportunity → follow-up.
- سيناريو failure + rollback.

## Phase 5 — Validation Gates (Go/No-Go)

### Engineering Gate
- API smoke tests pass
- worker queues stable
- error rate ضمن الحدود

### Product/QA Gate
- الرحلات الأساسية تعمل AR/EN
- لا blockers من درجة P0/P1

### Operations Gate
- Monitoring + alerting شغال
- Incident channel فعال
- Backup/restore موثق ومجرب

### Sales Gate
- Scripts جاهزة
- objection handling جاهز
- pricing/packaging موحد

## Phase 6 — Go-Live Execution Window
1. إعلان بدء نافذة الإطلاق (T0).
2. مراقبة لصيقة أول 30 دقيقة.
3. مراجعة حالة كل 15 دقيقة خلال أول ساعتين.
4. قرار الاستمرار أو rollback حسب المعايير.

## Rollback Policy
يتم rollback فوراً إذا تحقق أحد التالي:
- نسبة أخطاء حرجة تتجاوز الحد المتفق (>X%).
- تعطل متكرر في AI path يمنع التشغيل التجاري.
- فقدان وظيفة أساسية في onboarding/sales flow.

Rollback خطوات:
1. الرجوع لآخر release tag مستقر.
2. إعادة تشغيل الخدمات.
3. التحقق من smoke tests.
4. نشر تقرير حادث خلال 60 دقيقة.

## 30/60/90-Day Tactical Plan

### Day 0–30
- Stabilization + bug burn-down
- تحسين جودة مخرجات AI
- توحيد playbooks بين الفرق

### Day 31–60
- تحسين conversion rate في قمع المبيعات
- tuning للنماذج المحلية (cost/latency/quality)
- رفع أتمتة العمليات التشغيلية

### Day 61–90
- scale strategy حسب القطاعات
- تحسين unit economics
- وضع roadmap التوسّع الإقليمي

## Weekly Operating Cadence
- Weekly launch review (Exec + Product + Eng + Sales)
- مراجعة KPIs + incidents + action items
- Owner + due date لكل بند تحسين

## Definition of Done (Full Completion)
- [ ] PR #16 merged to main and deployed
- [ ] PR #17 merged to main and deployed
- [ ] All launch gates passed
- [ ] Monitoring/alerting confirmed
- [ ] Sales + Ops enablement completed
- [ ] 30/60/90 plan approved with owners
