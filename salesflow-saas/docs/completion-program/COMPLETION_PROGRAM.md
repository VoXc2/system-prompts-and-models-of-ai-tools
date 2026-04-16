# Dealix Completion Program — من الوثائق إلى التشغيل المؤسسي

**الإصدار:** 1.0  
**التاريخ:** 2026-04-16  
**الحالة:** معتمد — قيد التنفيذ  
**المالك:** Dealix Engineering & Architecture

---

## الغرض

هذا البرنامج يحوّل Dealix من:

> **وثائق قوية + رؤية Tier-1**

إلى:

> **Decision Fabric + Execution Fabric + Trust Fabric + Enterprise Delivery Fabric تعمل فعلياً في الإنتاج.**

لا مزيد من التوسع في الشعارات. البرنامج يغلق الفجوة بين الدستور المرجعي والقدرة التشغيلية الفعلية.

---

## الأساس الذي نبني عليه

### ما أُنجز (الطبقة المرجعية)

| المكون | الحالة |
|--------|--------|
| MASTER-BLUEPRINT.mdc | ✅ مصدر حقيقة معماري |
| ULTIMATE_EXECUTION_MASTER_AR.md | ✅ وثيقة تنفيذ استراتيجية |
| AGENTS.md + CLAUDE.md | ✅ سياسات وحوكمة التطوير |
| Module Map (50+ خدمة) | ✅ خريطة مكونات كاملة |
| Agent Registry (19 وكيل) | ✅ سجل وكلاء مفصّل |
| PDPL Checklist | ✅ قائمة امتثال |
| ADRs (Multi-tenant, WhatsApp-first) | ✅ قرارات معمارية موثّقة |
| Runbooks (6 وثائق) | ✅ أدلة تشغيلية |
| CI Pipeline (backend + frontend + E2E) | ✅ عامل |

### ما ينقص (الفجوة التشغيلية)

التطبيق التشغيلي الكامل لهذه الطبقات داخل النظام نفسه، مع evidence حقيقي على مستوى:
- Workflows, Approvals, Telemetry
- Security, Connectors, Enterprise Release Gates
- Saudi Compliance Operationalization

---

## البنية النهائية: 5 طبقات تشغيلية

```
┌─────────────────────────────────────────────────────┐
│                 5. Operating Plane                    │
│    GitHub Rulesets · CODEOWNERS · Environments        │
│    OIDC · Attestations · Release Gates                │
├─────────────────────────────────────────────────────┤
│                 4. Data Plane                         │
│    Postgres · pgvector · Connector Facades            │
│    Event Envelopes · Schema Registry · Quality Gates  │
├─────────────────────────────────────────────────────┤
│                 3. Trust Plane                        │
│    OPA Policies · OpenFGA Auth · Vault Secrets        │
│    Keycloak SSO · Tool Verification · Audit Ledger    │
├─────────────────────────────────────────────────────┤
│                 2. Execution Plane                    │
│    Temporal (durable) · Celery (short-lived)          │
│    Compensation · Idempotency · Workflow Versioning   │
├─────────────────────────────────────────────────────┤
│                 1. Decision Plane                     │
│    Structured Outputs · Evidence Packs · Risk Registry│
│    Approval Packets · LangGraph HITL · Provenance     │
└─────────────────────────────────────────────────────┘
```

---

## المسارات الثمانية

### WS-1: Productization & Architecture Closure

**الهدف:** إزالة الغموض المعماري بالكامل.

| المخرج | الوصف |
|--------|-------|
| Current-vs-Target Register | لكل subsystem: Current / Partial / Pilot / Production |
| 5 Planes Lock | قفل رسمي على الطبقات الخمس |
| 6 Business Tracks Lock | قفل رسمي على المسارات الستة |
| Agent Roles Lock | Observer / Recommender / Executor per agent |
| Action Metadata Lock | Approval / Reversibility / Sensitivity / Provenance / Freshness |

**التقنية المرجعية:** Architecture Decision Records, C4 Model

---

### WS-2: Decision Plane Hardening

**الهدف:** كل output وكيل يصبح schema-bound, auditable, typed, resumable.

| المخرج | الوصف |
|--------|-------|
| Unified Decision Schemas | `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json` |
| Structured Outputs Mandate | منع free-text operational output للتدفقات الحرجة |
| Evidence Pack Generator | مولّد حزم الأدلة التلقائي |
| Decision Memo Compiler | مُجمّع مذكرات القرار ثنائي اللغة |
| Provenance/Freshness/Confidence Scores | تعريف ونشر درجات المصدر والحداثة والثقة |

**التقنية المرجعية:** OpenAI Structured Outputs, Responses API, LangGraph stateful loops

---

### WS-3: Execution Plane Hardening

**الهدف:** أول deterministic workflow enterprise-grade حي.

| المخرج | الوصف |
|--------|-------|
| Workflow Inventory | جرد كل workflows وتصنيفها: short-lived / medium-lived / long-lived durable |
| Temporal Pilot | pilot واحد: partner approval flow أو DD room flow |
| Compensation Policies | سياسات التعويض عند الفشل |
| Idempotency Keys | مفاتيح عدم التكرار لكل عملية |
| Workflow Versioning Strategy | استراتيجية إصدار workflows |

**التقنية المرجعية:** Temporal, Celery (short-lived retention), LangGraph

**قاعدة التصنيف:**
> كل workflow أكثر من 15 دقيقة أو يعبر أكثر من نظامين أو يحتاج compensation = يهاجر إلى Temporal queue.

---

### WS-4: Trust Fabric Hardening

**الهدف:** كل فعل حساس يمر عبر trust fabric موحّد.

| المخرج | الوصف |
|--------|-------|
| Policy Inventory | جرد كل السياسات المبعثرة في الكود |
| OPA Policy Packs | حزم سياسات OPA |
| OpenFGA Model Draft | نموذج تفويض دقيق |
| Vault Integration Plan | خطة تكامل HashiCorp Vault |
| Keycloak SSO Plan | خطة SSO وهوية الخدمات |
| Tool Verification Ledger v1 | سجل التحقق من الأدوات |
| Contradiction Dashboard | لوحة تناقضات الوكلاء |

**التقنية المرجعية:** OPA, OpenFGA, HashiCorp Vault, Keycloak

---

### WS-5: Data & Connector Fabric

**الهدف:** no raw vendor chaos.

| المخرج | الوصف |
|--------|-------|
| Connector Facade Standard | معيار واجهات الموصلات |
| Connector Versioning | إصدار لكل connector |
| Retry/Timeout/Idempotency Policies | سياسات إعادة المحاولة والانتظار |
| Event Envelope Standard | معيار مغلفات الأحداث (CloudEvents) |
| Schema Registry Discipline | انضباط سجل المخططات |
| Semantic Metrics Dictionary | قاموس المقاييس الدلالية |
| Quality Checks | فحوصات جودة على datasets الحرجة |

**التقنية المرجعية:** AsyncAPI, CloudEvents, OpenTelemetry, Great Expectations

---

### WS-6: Enterprise Delivery Fabric

**الهدف:** release system جاهز للمؤسسات، لا مجرد CI ناجح.

| المخرج | الوصف |
|--------|-------|
| GitHub Rulesets | قواعد حماية الفروع |
| CODEOWNERS | ملف ملكية الكود |
| Required Checks | فحوصات مطلوبة |
| Protected Release Branches | فروع إصدار محمية |
| Environments | dev / staging / canary / prod |
| OIDC Federation | اتحاد هوية OIDC |
| Artifact Attestations | شهادات المخرجات |
| External Audit Log Streaming | تدفق سجلات التدقيق الخارجية |

**التقنية المرجعية:** GitHub Actions, OIDC, Sigstore, SLSA

---

### WS-7: Saudi Enterprise Readiness

**الهدف:** Dealix يصبح قابلاً للتسويق جدياً في السعودية والخليج للشركات الحساسة.

| المخرج | الوصف |
|--------|-------|
| PDPL Data Classification Matrix | مصفوفة تصنيف البيانات |
| Personal Data Processing Register | سجل معالجة البيانات الشخصية |
| Residency/Transfer Control Flags | أعلام التحكم في الإقامة والنقل |
| NCA ECC Readiness Gaps Register | سجل فجوات جاهزية ECC |
| AI Governance Profile (NIST AI RMF) | ملف حوكمة الذكاء الاصطناعي |
| OWASP LLM Controls Checklist | قائمة تحقق ضوابط OWASP LLM لكل إصدار |

**التقنية المرجعية:** PDPL, NCA ECC 2-2024, NIST AI RMF, OWASP LLM Top 10

---

### WS-8: Executive & Customer Readiness

**الهدف:** الإدارة ترى نظاماً تشغيلياً، لا backend abstractions فقط.

| المخرج | الوصف |
|--------|-------|
| Executive Room (حي) | غرفة تنفيذية حية |
| Board-Ready Memo View | عرض مذكرات جاهزة لمجلس الإدارة |
| Evidence Pack View | عرض حزم الأدلة |
| Approval Center | مركز الموافقات |
| Policy Violations Board | لوحة مخالفات السياسات |
| Partner Scorecards | بطاقات أداء الشركاء |
| Actual vs Forecast | الفعلي مقابل المتوقع |
| Risk Heatmaps | خرائط حرارية للمخاطر |
| Next-Best-Action Dashboard | لوحة الإجراء الأمثل التالي |

---

## ترتيب الأولويات

```
1. Control/Trust ──────────── قبل المزيد من الوكلاء
2. Execution ──────────────── قبل المزيد من الاستقلالية
3. Connector facades ──────── قبل المزيد من استدعاءات الأدوات
4. Semantic metrics ───────── قبل المزيد من لوحات العرض
5. Saudi governance ───────── قبل الإطلاق المؤسسي
6. Executive room ─────────── قبل التوسع الخارجي
```

---

## Definition of Done — Enterprise Grade

لا يُعتبر Dealix "جاهزاً للشركات" إلا إذا تحقق:

- [ ] كل business-critical recommendation تخرج structured + evidence-backed
- [ ] كل long-running commitment يمر عبر deterministic durable workflow
- [ ] كل action حساس يحمل Approval / Reversibility / Sensitivity metadata
- [ ] كل connector versioned وله retry/idempotency/audit mapping
- [ ] كل release له rulesets + approvals + OIDC + provenance
- [ ] كل traceable surface لديه OTel telemetry وcorrelation IDs
- [ ] كل enterprise deployment له security review و red-team coverage
- [ ] كل Saudi-sensitive workflow له PDPL/NCA-aware control mapping

---

## الملفات المرافقة

| الملف | الغرض |
|-------|-------|
| [`EXECUTION_MATRIX.md`](./EXECUTION_MATRIX.md) | المصفوفة التنفيذية الكاملة: Workstream → Deliverables → Owner → Evidence Gate → Exit Criteria → Dependencies → Risk → SLA |
| [`CURRENT_VS_TARGET_ARCHITECTURE.md`](./CURRENT_VS_TARGET_ARCHITECTURE.md) | سجل معماري: Current / Partial / Pilot / Production لكل نظام فرعي |
| [`GAP_ANALYSIS.md`](./GAP_ANALYSIS.md) | تحليل الفجوات الثمانية مع خطط الإغلاق |
| [`DEFINITION_OF_DONE.md`](./DEFINITION_OF_DONE.md) | بوابات الجاهزية المؤسسية التفصيلية |

---

*هذا البرنامج ليس إعادة اختراع للخطة، بل برنامج إغلاق شامل يترجم الدستور إلى تشغيل.*
