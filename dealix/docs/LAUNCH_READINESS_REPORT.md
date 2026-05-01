# تقرير جاهزية إطلاق Dealix

- **آخر تحديث للوثيقة:** 2026-05-01
- **الدرجة الإجمالية (تقدير منتج/تقني):** 58 / 100 — *لم تتغير الأرقام تلقائياً؛ راجع المجالات أدناه بعد كل إغلاق بوابة.*

## حزمة التدشين في الريبو (مكتملة توثيقياً)

تم تجميع مسار **يوم التدشين** و**نطاق التسمية** في:

- [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md) — فهرس خطوات (CI، staging، امتثال، فوترة، واتساب، بيتا).
- [`LAUNCH_SCOPE_AND_NAMING.md`](LAUNCH_SCOPE_AND_NAMING.md) — Paid Private Beta vs Public Launch.
- [`SECURITY_SECRET_ROTATION_CHECKLIST.md`](SECURITY_SECRET_ROTATION_CHECKLIST.md) — إجراءات تدوير المفاتيح بعد التسريب.
- [`PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md`](PUBLIC_LAUNCH_GO_NO_GO_TRACKER.md) — متتبع أسبوعي للإطلاق العام.

**ما يبقى خارج الريبو:** توقيع DPA، نشر صفحات قانونية على النطاق العام، ضبط secrets في السحابة، عملاء دافعون، واستقرار إنتاج 14 يوماً لـ Go/No-Go العام ([`PUBLIC_LAUNCH_GO_NO_GO.md`](PUBLIC_LAUNCH_GO_NO_GO.md)).

## ملخص تنفيذي

هذا التقرير يعتمد على مخطط المنتج والكود؛ ربطه بمقاييس CI والإنتاج يحسّن الدقة. لإعادة التقدير: أغلق البنود في [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md) ثم عدّل الدرجات يدوياً أو عبر سكربت داخلي.

## تفاصيل المجالات

### الواجهات الخلفية وواجهة البرمجة (Backend / API)
- **الدرجة:** 78
- **الحالة:** almost_ready
- **الأولوية:** P1 — **المسؤول:** engineering
- **النواقص:**
  - Load tests
  - Auth hardening for multi-tenant
- **الخطوات التالية:**
  - Add smoke tests for new routers
  - Document rate limits

### الواجهة والتجربة (Frontend / UI)
- **الدرجة:** 52
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** product
- **النواقص:**
  - Next.js app optional
  - Command center UI
- **الخطوات التالية:**
  - Polish landing + mobile QA
  - Wire API examples

### قاعدة البيانات وـ pgvector (Supabase / Database)
- **الدرجة:** 60
- **الحالة:** needs_work
- **الأولوية:** P0 — **المسؤول:** engineering
- **النواقص:**
  - Embeddings pipeline
  - RLS policy tests
- **الخطوات التالية:**
  - Run migration on staging
  - Service role only server-side

### ذاكرة المشروع والفهرسة (Project Intelligence)
- **الدرجة:** 68
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** engineering
- **النواقص:**
  - Semantic search live
  - Chunk metadata redaction
- **الخطوات التالية:**
  - Run scripts/index_project_memory.py
  - Add nightly index job

### المشغّل الشخصي الاستراتيجي (Personal Operator)
- **الدرجة:** 72
- **الحالة:** almost_ready
- **الأولوية:** P0 — **المسؤول:** product
- **النواقص:**
  - Persistent memory backend
  - WhatsApp send adapter
- **الخطوات التالية:**
  - Ship daily brief + opportunities APIs
  - Approval UX

### تدفق واتساب والأزرار (WhatsApp flow)
- **الدرجة:** 48
- **الحالة:** needs_work
- **الأولوية:** P0 — **المسؤول:** engineering
- **النواقص:**
  - Cloud API credentials
  - Webhook verification
- **الخطوات التالية:**
  - Implement two-step buttons
  - Opt-in ledger

### البريد والتقويم (Gmail / Calendar)
- **الدرجة:** 40
- **الحالة:** blocked
- **الأولوية:** P1 — **المسؤول:** engineering
- **النواقص:**
  - OAuth apps
  - Draft-only enforcement in prod
- **الخطوات التالية:**
  - Use integrations module drafts
  - Approval audit trail

### الوكلاء والحوكمة (AI / Agents / Guardrails)
- **الدرجة:** 55
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** engineering
- **النواقص:**
  - Langfuse eval sets
  - OpenAI Agents SDK trace
- **الخطوات التالية:**
  - Trace tool calls
  - Block outbound without approval

### المراقبة والتتبع (Observability)
- **الدرجة:** 58
- **الحالة:** needs_work
- **الأولوية:** P2 — **المسؤول:** engineering
- **النواقص:**
  - Dashboards
  - SLOs
- **الخطوات التالية:**
  - Ensure Sentry DSN in staging
  - OTel sampling

### الأمن والامتثال (Security / PDPL)
- **الدرجة:** 62
- **الحالة:** needs_work
- **الأولوية:** P0 — **المسؤول:** security
- **النواقص:**
  - DPA templates
  - Retention automation
- **الخطوات التالية:**
  - Complete SECURITY_PDPL_CHECKLIST
  - Export/delete runbook

### الفوترة والتسعير (Billing / Pricing)
- **الدرجة:** 50
- **الحالة:** needs_work
- **الأولوية:** P2 — **المسؤول:** business
- **النواقص:**
  - Live payment provider (راجع [`BILLING_RUNBOOK.md`](BILLING_RUNBOOK.md) — Moyasar أو ما يعتمده المنتج)
  - Tax
- **الخطوات التالية:**
  - Define beta pricing
  - Invoice flow

### تجربة الإدماج (Onboarding)
- **الدرجة:** 45
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** product
- **النواقص:**
  - Self-serve checklist
  - In-product tours
- **الخطوات التالية:**
  - First-run wizard
  - Sample data pack

### الوصول للسوق والمبيعات (GTM / Sales)
- **الدرجة:** 55
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** gtm
- **النواقص:**
  - ICP one-pager
  - Pilot agreement
- **الخطوات التالية:**
  - 10-founder list
  - Case study template

### الاختبارات والتكامل المستمر (Testing / CI)
- **الدرجة:** 55
- **الحالة:** needs_work
- **الأولوية:** P1 — **المسؤول:** engineering
- **النواقص:**
  - Flaky tests
  - Coverage gates
- **الخطوات التالية:**
  - Stabilize integration suite
  - Add personal operator tests
- **ملاحظة:** أوامر التحقق الموحّدة في [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md) و[`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md).

### التوثيق (Documentation)
- **الدرجة:** 75
- **الحالة:** almost_ready
- **الأولوية:** P2 — **المسؤول:** product
- **النواقص:**
  - API reference polish
- **الخطوات التالية:**
  - Keep launch docs updated
  - Arabic exec summaries
- **محدّث:** فهارس التدشين (`LAUNCH_DAY_*`, `LAUNCH_SCOPE_*`) مضافة.

## معايير البيتا الخاصة

- واتساب: أزرار موافقة + سجل موافقة
- لا إرسال بارد تلقائي
- اختبارات أساسية خضراء على staging

## معايير الإطلاق العام

- PDPL: سياسات واضحة + طلب حذف/تصدير
- مراقبة وفوترة وجاهزية أمنية
