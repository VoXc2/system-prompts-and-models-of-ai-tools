# Dealix Definition of Done — Enterprise Readiness Gates

**الإصدار:** 1.0  
**التاريخ:** 2026-04-16  
**المرجع:** [`COMPLETION_PROGRAM.md`](./COMPLETION_PROGRAM.md)

---

## الغرض

لا يُعتبر Dealix "جاهزاً للشركات" حتى تجتاز كل بوابة من البوابات أدناه. كل بوابة لها معيار قابل للقياس ودليل إنجاز مطلوب. الادعاء بدون evidence = عدم اجتياز.

---

## البوابات الثمانية

### Gate 1: Structured & Evidence-Backed Decisions

> كل business-critical recommendation تخرج structured + evidence-backed.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| Schema Enforcement | 100% من critical agent outputs تطابق JSON Schema | Integration tests + production log sample |
| Evidence Pack Generation | كل توصية حرجة تحمل evidence pack | Evidence pack viewer يعرض ≥20 حزمة حقيقية |
| Decision Memo Quality | Memos مقروءة ودقيقة بالعربية والإنجليزية | مراجعة native speaker + accuracy check |
| Confidence Scoring | كل قرار يحمل `confidence_score` | Score distribution analysis على ≥100 قرار |
| Provenance Tracking | كل قرار يحمل `provenance_source` | Audit query يُرجع مصدر كل قرار |

**المسار:** WS-2  
**التبعيات:** WS-1.5 (Action Metadata Standard)

---

### Gate 2: Deterministic Durable Workflows

> كل long-running commitment يمر عبر deterministic durable workflow.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| Workflow Classification | 100% من workflows مصنّفة | Workflow Inventory مكتمل |
| Durable Runtime | Workflows > 15 min تعمل في Temporal | ≥1 Temporal workflow حي في staging |
| Crash Resilience | Workflow يتحمل worker restart | Test: kill worker mid-workflow → workflow يستأنف |
| Compensation | فشل خطوة يُشغّل compensation | Test: inject failure → compensation يعمل |
| Idempotency | لا تنفيذ مكرر | Test: replay request → نفس النتيجة بدون duplicate |

**المسار:** WS-3  
**التبعيات:** WS-1.1 (Architecture Register)

---

### Gate 3: Action Metadata on Sensitive Operations

> كل action حساس يحمل Approval / Reversibility / Sensitivity metadata.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| Metadata Coverage | 100% من sensitive actions تحمل `ActionMetadata` | Code coverage scan + runtime validation |
| Approval Enforcement | أي action بـ `approval_required=true` يحتاج موافقة | Test: execute without approval → blocked |
| Reversibility Flag | كل action يوضح هل هو reversible | Schema validation test |
| Sensitivity Classification | كل action مصنّف: `low` / `medium` / `high` / `critical` | Classification matrix مكتملة |
| Audit Trail | كل sensitive action مسجّل مع metadata | Audit query يُرجع metadata كاملة |

**المسار:** WS-1.5, WS-4  
**التبعيات:** WS-4.1 (Policy Inventory)

---

### Gate 4: Versioned Connectors with Resilience

> كل connector versioned وله retry/idempotency/audit mapping.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| Facade Pattern | كل vendor API يُستدعى عبر ConnectorFacade | Code review: zero direct vendor calls |
| Version Tags | كل connector يحمل version | `get_version()` returns valid semver |
| Retry Policy | كل connector له retry with backoff | Test: simulate failure → retry works |
| Idempotency | كل write operation idempotent | Test: replay → no duplicate side effects |
| Audit Log | كل connector call مسجّل | Audit query per connector |
| Timeout Policy | كل connector له timeout مُعرَّف | Config file with timeout per connector |

**المسار:** WS-5  
**التبعيات:** WS-1.2 (Planes Lock)

---

### Gate 5: Enterprise Release Pipeline

> كل release له rulesets + approvals + OIDC + provenance.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| Branch Rulesets | `main` + `release/*` محميّة بـ rulesets | GitHub settings screenshot/API response |
| CODEOWNERS | كل مسار له مالك | CODEOWNERS file committed + working |
| Required Checks | CI checks مطلوبة قبل merge | PR blocked on check failure (screenshot) |
| Environment Promotion | dev → staging → canary → prod with approvals | Deployment log showing promotion chain |
| OIDC | لا long-lived secrets في CI | GitHub Actions workflow using OIDC |
| Artifact Signing | كل release artifact موقّع | Signature verification successful |
| Audit Streaming | Audit logs تتدفق لـ SIEM | Dashboard showing ingested events |

**المسار:** WS-6  
**التبعيات:** None (يمكن البدء فوراً)

---

### Gate 6: Full Observability with Correlation

> كل traceable surface لديه OTel telemetry وcorrelation IDs.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| OTel Integration | Traces + metrics + logs via OTel SDK | Dashboard showing traces |
| Correlation IDs | كل طلب يحمل `trace_id` + `correlation_id` | Log sample showing ID propagation |
| Agent Tracing | كل agent invocation لها trace | Trace visualization per agent call |
| Eval Datasets | كل وكيل له ≥10 test cases | Dataset files in repo |
| Regression Review | كل release يُراجع للتراجعات | Release notes include regression check |
| Red-Team Coverage | Agent/tool surfaces tested | Red-team report per release |

**المسار:** WS-6.3, WS-7.6, WS-2.2  
**التبعيات:** WS-1.1 (Architecture Register)

---

### Gate 7: Security Review & Red-Team

> كل enterprise deployment له security review و red-team coverage for LLM/application surfaces.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| OWASP LLM Top 10 Review | كل إصدار يُراجع | Signed checklist per release |
| Prompt Injection Testing | All agent prompts tested | Test results report |
| Data Leakage Testing | No PII in logs/outputs | Scan results report |
| Excessive Agency Testing | Agents respect permission boundaries | Test: attempt out-of-scope action → blocked |
| Insecure Output Testing | All outputs sanitized | Output validation test results |
| Security Scan | Bandit + Trivy per release | CI scan results passing |

**المسار:** WS-7.6  
**التبعيات:** WS-4.2 (OPA Policies), WS-4.6 (Tool Verification)

---

### Gate 8: Saudi Compliance Operationalization

> كل Saudi-sensitive workflow له PDPL/NCA-aware control mapping.

| المعيار | القياس | الدليل المطلوب |
|---------|--------|---------------|
| PDPL Data Classification | كل حقل PII مصنّف | Classification matrix document |
| Processing Register | سجل معالجة per PDPL Art. 29 | Register document ready for SDAIA |
| Consent Enforcement | لا outbound message بدون consent | Test: send without consent → blocked |
| Data Residency | Cross-border transfer blocked without consent | Test: attempt transfer → blocked |
| NCA ECC Assessment | كل ECC control مُقيَّم | Gaps register with remediation plan |
| AI Governance | ملف حوكمة per agent type | NIST AI RMF mapping document |
| DPO Appointed | مسؤول حماية بيانات مُعيَّن | Appointment letter |

**المسار:** WS-7  
**التبعيات:** WS-4.2 (OPA for enforcement), WS-7.1 (Classification)

---

## مصفوفة البوابات

| Gate | المسار الرئيسي | الحالة | التبعية الحرجة |
|------|---------------|--------|---------------|
| Gate 1: Structured Decisions | WS-2 | 🔴 Not Started | WS-1.5 |
| Gate 2: Durable Workflows | WS-3 | 🔴 Not Started | WS-1.1 |
| Gate 3: Action Metadata | WS-1 + WS-4 | 🔴 Not Started | WS-4.1 |
| Gate 4: Versioned Connectors | WS-5 | 🔴 Not Started | WS-1.2 |
| Gate 5: Release Pipeline | WS-6 | 🟡 Partial (CI exists) | None |
| Gate 6: Observability | WS-6 + WS-2 | 🟠 Current (basic) | WS-1.1 |
| Gate 7: Security Review | WS-7 | 🔴 Not Started | WS-4.2, WS-4.6 |
| Gate 8: Saudi Compliance | WS-7 | 🟡 Partial (PDPL code exists) | WS-4.2, WS-7.1 |

---

## قواعد البوابات

1. **لا ادعاء بدون دليل** — كل بوابة تتطلب evidence محدد ومسجّل
2. **لا استثناءات بدون ADR** — إذا لم تُجتز بوابة، يُوثّق السبب في Architecture Decision Record
3. **مراجعة ربع سنوية** — كل بوابة تُراجع كل ربع حتى اجتيازها
4. **لا إطلاق مؤسسي بدون Gate 3 + Gate 5 + Gate 8** — الحد الأدنى للإطلاق المؤسسي في السعودية
5. **Gate 5 يمكن البدء فوراً** — لا تبعيات، أعلى ROI مبكر

---

*هذا الملف هو الحكم النهائي على جاهزية Dealix. يُحدَّث مع كل sprint ويُعرض في مراجعة البرنامج.*
