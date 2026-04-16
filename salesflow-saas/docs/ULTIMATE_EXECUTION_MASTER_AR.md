# وثيقة التنفيذ السيادي الشاملة — Dealix Sovereign Enterprise Growth OS 2026

**الإصدار:** Sovereign Edition v5.0  
**الحالة:** مرجع تنفيذي حي مرتبط بـ `MASTER-BLUEPRINT.mdc` و`/api/v1/strategy/summary`.

---

## الرؤية النهائية

ليس الهدف أن يصبح Dealix "CRM أذكى"، بل أن يصبح:

**Dealix Sovereign Enterprise Growth OS**

منصة سيادية موحّدة تدير:
- Revenue OS
- Partnership OS
- M&A / CorpDev OS
- Expansion OS
- PMI / PMO OS
- Executive / Board OS

القاعدة التشغيلية:
**AI يستكشف ويحلل ويقترح، الأنظمة تنفذ، والبشر يعتمدون القرارات الحرجة.**

---

## البنية السيادية (5 Planes)

| Plane | الهدف التشغيلي | النواة التقنية |
|-------|-----------------|----------------|
| Decision Plane | signal detection, triage, scenario analysis, memos, recommendations | Responses API + Structured Outputs + Function Calling/MCP + LangGraph interrupts |
| Execution Plane | الالتزامات طويلة الأمد متعددة الأنظمة | LangGraph للـ cognition + Temporal للـ durable commitments |
| Trust Plane | policy, authorization, approval routing, auditability | OPA + OpenFGA + Vault + Keycloak + Tool Verification Ledger |
| Data Plane | مصدر حقيقة + عقود بيانات + جودة + تتبّع | Postgres + pgvector + Airbyte + Great Expectations + CloudEvents/AsyncAPI + OTel |
| Operating Plane | SDLC, release governance, provenance | GitHub rulesets/environments/OIDC/attestations + external audit streaming |

---

## Program Locks (إقفال البرنامج)

يجب تثبيت هذه العناصر داخل النظام كقيود تشغيل رسمية:
- 5 planes
- 6 business tracks
- 3 agent roles
- 3 action classes
- 3 approval classes كحد أدنى
- 4 reversibility classes
- sensitivity model إلزامي
- provenance/freshness/confidence trio إلزامي

---

## الأسطح الإلزامية داخل المنتج (Mandatory Live Surfaces)

- Executive Room
- Approval Center
- Evidence Pack Viewer
- Partner Room
- DD Room
- Risk Board
- Policy Violations Board
- Actual vs Forecast Dashboard
- Revenue Funnel Control Center
- Partnership Scorecards
- M&A Pipeline Board
- Expansion Launch Console
- PMI 30/60/90 Engine
- Tool Verification Ledger
- Connector Health Board
- Release Gate Dashboard
- Saudi Compliance Matrix
- Model Routing Dashboard

أي سطح مفقود = فجوة مباشرة في النسخة المؤسسية الكاملة.

---

## حدود الأتمتة (Automation Boundaries)

### يُؤتمت بالكامل
- intake, enrichment, scoring
- memo drafting, evidence aggregation
- workflow kickoff, reminders, task assignment, SLA tracking
- variance/anomaly detection
- connector syncs, quality checks, telemetry collection

### يُؤتمت مع اعتماد إلزامي
- term sheet sending
- signature request
- strategic partner activation
- market launch
- M&A offer
- discount خارج السياسة
- data sharing عالي الحساسية
- production promotion
- capital commitments

---

## Sovereign Routing Fabric

Policy-based routing lanes:
- coding lane
- executive reasoning lane
- throughput drafting lane
- fallback lane

المقاييس الإلزامية لكل lane:
- latency
- schema adherence
- contradiction rate
- Arabic quality
- cost per successful task

---

## Connector Facade Contract (إلزامي)

كل تكامل خارجي يجب أن يمر عبر facade versioned يحتوي على:
- contract
- version
- retry policy
- timeout policy
- idempotency key
- approval policy
- audit mapping
- telemetry mapping
- rollback/compensation notes

---

## جاهزية السعودية والحوكمة

Matrix إلزامي لكل workflow حساس:
- PDPL controls mapping
- ECC/NCA cyber controls checkpoints
- NIST AI RMF lifecycle coverage
- OWASP LLM Top 10 mitigations

---

## تعريف الجاهزية النهائية (Final Readiness Definition)

لا يُعتبر Dealix جاهزاً مؤسسياً إلا إذا تحقق ما يلي:
- كل قرار business-critical structured + evidence-backed + schema-bound
- كل long-running commitment durable + resumable + crash-tolerant
- كل action حساس يحمل approval/reversibility/sensitivity metadata
- كل connector versioned مع retry/idempotency/audit mapping
- كل release يمر عبر rulesets + environments + OIDC + provenance
- كل surface traceable عبر OTel + correlation IDs
- كل deployment مؤسسي يمر security review وLLM/tool red-team
- كل workflow حساس في السعودية يملك mapping واضح على PDPL/NCA/AI governance

---

## خارطة التنفيذ المرحلية

| المرحلة | الأفق | المخرجات |
|---------|-------|----------|
| Sovereign Foundation | 0–90 يوم | Program Locks + 5 planes bootstrap + Approval/Evidence core |
| Execution Closure | شهر 2–3 | Temporal commitments + connector contracts + contradiction alpha |
| Enterprise Hardening | شهر 4–9 | OpenFGA/OPA rollout + Vault/Keycloak + compliance operationalization |
| Category Dominance | شهر 10–36 | Board OS maturity + M&A/expansion playbooks + regional policy routing |

---

## ربط بالمستودع

| المسار | الغرض |
|--------|--------|
| `MASTER-BLUEPRINT.mdc` | المرجع المعماري الأعلى |
| `backend/app/api/v1/strategy_summary.py` | العقدة الحية للاستراتيجية السيادية |
| `frontend/src/app/strategy/strategy-page-client.tsx` | الواجهة التنفيذية للـ planes والـ locks |
| `backend/app/services/knowledge_service.py` | Dealix-native retrieval |
| `backend/app/ai/orchestrator.py` | orchestration + knowledge hooks |
| `docs/INTEGRATION_MASTER_AR.md` | مرجع التكاملات والإطلاق التشغيلي |

---

*هذه الوثيقة تحوّل الرؤية من خطاب استراتيجي إلى spec تشغيل سيادي قابل للتطبيق والتدقيق.*
