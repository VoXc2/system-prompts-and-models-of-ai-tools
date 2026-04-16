# Current vs Target Architecture Register

**الإصدار:** 1.0  
**التاريخ:** 2026-04-16  
**المرجع:** [`COMPLETION_PROGRAM.md`](./COMPLETION_PROGRAM.md)

---

## حالات النضج

| الحالة | التعريف | المعيار |
|--------|---------|---------|
| 🔴 **Not Started** | لا يوجد كود ولا تكوين | المكون مذكور في الوثائق فقط |
| 🟠 **Current** | كود موجود يعمل بشكل أساسي | يعمل في dev، لا اختبارات شاملة، لا حوكمة |
| 🟡 **Partial** | كود + اختبارات جزئية + توثيق | يعمل، اختبارات أساسية، لكن لا يلبي معايير enterprise |
| 🔵 **Pilot** | مُجرَّب على سيناريو حقيقي واحد | اختبار end-to-end، مراجعة أمنية أولية، مستخدم حقيقي |
| 🟢 **Production** | جاهز للإنتاج enterprise-grade | اختبارات شاملة، observability، security review، SLA |

---

## 1. Decision Plane

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Agent Output Schemas | 🟠 Current — agents return free-text or loosely typed JSON via model_router | 🟢 Production — all critical agent outputs schema-bound via Structured Outputs | No enforced JSON Schema; output structure varies by agent |
| Evidence Packs | 🔴 Not Started — no evidence pack generation | 🟢 Production — auto-generated evidence packs per decision | Concept documented, zero implementation |
| Decision Memos | 🔴 Not Started — no structured memo output | 🟢 Production — bilingual decision memos from agent outputs | No memo compiler exists |
| Risk Register (per decision) | 🔴 Not Started | 🔵 Pilot — risk scoring per critical decision | No per-decision risk scoring |
| Provenance/Freshness/Confidence | 🔴 Not Started | 🟢 Production — scores on every agent output | No score calculation logic |
| LangGraph HITL Interrupts | 🟠 Current — basic orchestrator exists | 🟢 Production — stateful loops with human-in-the-loop | Orchestrator exists but no interrupt/resume capability |
| Approval Packets | 🟡 Partial — `security_gate.py` + `escalation.py` exist | 🟢 Production — typed approval packets with metadata | Basic escalation logic; no structured approval packet schema |

---

## 2. Execution Plane

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Short-lived Tasks (Celery) | 🟡 Partial — Celery workers functional for agent execution | 🟢 Production — classified, monitored, SLA-bound | Workers exist but no classification or SLA tracking |
| Durable Workflows (Temporal) | 🔴 Not Started | 🟢 Production — critical business flows in Temporal | No Temporal infrastructure or workflows |
| Workflow Inventory | 🔴 Not Started | 🟢 Production — all workflows classified and tracked | No inventory exists |
| Compensation/Saga Patterns | 🔴 Not Started | 🟢 Production — compensation for all multi-system flows | No compensation logic |
| Idempotency | 🟠 Current — some retry logic in agent executor | 🟢 Production — idempotency keys on all critical endpoints | Retry exists but no idempotency key enforcement |
| Workflow Versioning | 🔴 Not Started | 🟢 Production — versioned workflows with backward compat | No versioning strategy |

---

## 3. Trust Plane

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Policy Engine (OPA) | 🔴 Not Started | 🟢 Production — centralized policy decisions | Policies scattered in code conditionals and prompts |
| Authorization (OpenFGA) | 🔴 Not Started | 🟢 Production — fine-grained authorization graph | RBAC via JWT claims; no relationship-based auth |
| Secrets Management (Vault) | 🔴 Not Started — `.env` files | 🟢 Production — dynamic secrets with rotation | Static `.env` files; no rotation; no audit |
| Identity/SSO (Keycloak) | 🔴 Not Started — JWT-only auth | 🟢 Production — SSO, service identity, OIDC | Basic JWT auth; no SSO; no service-to-service identity |
| Tool Verification | 🟡 Partial — `tool_verification.py` + `tool_receipts.py` exist | 🟢 Production — mandatory evidence for every tool action | Verification service exists but not enforced across all tools |
| Security Gate | 🟡 Partial — `security_gate.py` exists | 🟢 Production — gate integrated with OPA policies | Gate exists as code; not connected to policy engine |
| Shannon Security | 🟡 Partial — `shannon_security.py` exists | 🟢 Production — integrated threat detection | Security scanning exists but not integrated with trust fabric |
| Audit Trail | 🟡 Partial — `audit_service.py` exists; `ai_conversations` logging | 🟢 Production — comprehensive audit with correlation IDs | Basic audit logging; no correlation IDs; no centralized query |

---

## 4. Data Plane

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Operational DB (PostgreSQL) | 🟡 Partial — PostgreSQL with SQLAlchemy async | 🟢 Production — monitored, optimized, SLA-bound | Works but no query monitoring, no connection pooling strategy doc |
| Semantic Memory (pgvector) | 🟡 Partial — `KnowledgeService` + pgvector | 🟢 Production — indexed, quality-checked, refreshed | RAG works but no quality checks or freshness tracking |
| WhatsApp Connector | 🟡 Partial — `whatsapp_service.py` + `integrations/whatsapp.py` | 🟢 Production — versioned facade with retry/audit | Direct API calls; no facade pattern; no versioning |
| Email Connector | 🟡 Partial — `email_service.py` + `integrations/email_sender.py` | 🟢 Production — versioned facade with retry/audit | Direct integration; no facade pattern |
| SMS Connector | 🟠 Current — `integrations/sms.py` exists | 🟢 Production — versioned facade with retry/audit | Basic implementation |
| Salesforce Connector | 🟠 Current — `salesforce_agentforce.py` exists | 🟢 Production — versioned facade with sync conflict resolution | Service exists but no versioning or conflict resolution |
| Stripe Connector | 🟠 Current — `stripe_service.py` exists | 🟢 Production — versioned facade with idempotency | Basic integration |
| Event Envelopes | 🔴 Not Started | 🟢 Production — CloudEvents-compatible envelope on all events | No event envelope standard; raw Redis messages |
| Schema Registry | 🔴 Not Started | 🟢 Production — schema versioning for all data contracts | No schema registry |
| Semantic Metrics | 🔴 Not Started | 🟢 Production — defined metric dictionary | No standardized metric definitions |
| Data Quality (Great Expectations) | 🔴 Not Started | 🟢 Production — quality gates in CI | No quality checks |

---

## 5. Operating Plane

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| CI Pipeline | 🟡 Partial — `dealix-ci.yml` runs pytest + lint + build + E2E | 🟢 Production — required checks, security scan, attestations | CI works but no required status checks enforcement |
| CODEOWNERS | 🔴 Not Started | 🟢 Production — every path has owner(s) | No CODEOWNERS file |
| Branch Protection / Rulesets | 🔴 Not Started (repo-level) | 🟢 Production — rulesets on main + release branches | No branch protection configured |
| Environments (dev/staging/canary/prod) | 🔴 Not Started | 🟢 Production — environment promotion pipeline | Docker Compose for dev only; no staging/canary/prod pipeline |
| OIDC Federation | 🔴 Not Started | 🟢 Production — no long-lived secrets in CI | Static secrets in CI |
| Artifact Attestations | 🔴 Not Started | 🟢 Production — signed container images | No signing or provenance |
| Audit Log Streaming | 🔴 Not Started | 🟢 Production — logs to external SIEM | No audit log streaming |
| Observability (OTel) | 🟠 Current — `observability.py` exists | 🟢 Production — OTel traces + metrics + logs with correlation | Basic observability; no OTel integration; no correlation IDs |
| Repo Hygiene | 🟡 Partial — `repo-hygiene.yml` checks for required files | 🟢 Production — comprehensive hygiene checks | Basic file existence checks |

---

## 6. Saudi Enterprise Readiness

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| PDPL Consent Management | 🟡 Partial — `pdpl/consent_manager.py` + `data_rights.py` | 🟢 Production — full PDPL compliance engine | Consent service exists; not fully tested against all PDPL articles |
| PDPL Data Classification | 🔴 Not Started | 🟢 Production — every PII field classified | No classification matrix |
| NCA ECC Compliance | 🔴 Not Started | 🟢 Production — ECC readiness register | PDPL checklist exists; no ECC mapping |
| AI Governance (NIST AI RMF) | 🔴 Not Started | 🟢 Production — governance profile per agent type | No AI governance framework |
| OWASP LLM Security | 🔴 Not Started | 🟢 Production — per-release security checklist | No LLM-specific security checks |
| ZATCA Compliance | 🟠 Current — `zatca_compliance.py` exists | 🟢 Production — e-invoicing compliant | Basic service; needs full testing |
| Data Residency Controls | 🔴 Not Started | 🟢 Production — enforced residency flags | No data residency enforcement |

---

## 7. Agent System

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Agent Registry (19 agents) | 🟡 Partial — documented, Celery-based execution | 🟢 Production — typed I/O, monitored, SLA-bound | Agents work but no runtime SLA tracking |
| Agent Router | 🟡 Partial — `router.py` routes events to agents | 🟢 Production — policy-gated routing | Routing works but no policy integration |
| Agent Executor | 🟡 Partial — retry logic, escalation | 🟢 Production — idempotent, compensatable, audited | Basic retry; no compensation or correlation IDs |
| Multi-Agent Orchestrator | 🟡 Partial — `hermes_orchestrator.py` | 🟢 Production — LangGraph stateful, HITL-capable | Orchestrator exists; not LangGraph-based; no HITL |
| Agent Role Classification | 🔴 Not Started | 🟢 Production — Observer/Recommender/Executor per agent | No role classification |
| Agent Observability | 🟠 Current — logs to `ai_conversations` | 🟢 Production — OTel traces per agent invocation | Basic logging; no tracing |

---

## 8. Business Features

| Subsystem | Current State | Target State | Gap Summary |
|-----------|--------------|--------------|-------------|
| Lead Management | 🟡 Partial — scoring, qualification, pipeline | 🟢 Production — end-to-end with observability | Works; needs monitoring |
| Deal Pipeline | 🟡 Partial — stage tracking, forecasting | 🟢 Production — durable workflows, evidence packs | Works; no durable execution |
| CPQ (Quote/Proposal) | 🟡 Partial — quote engine, proposal generator | 🟢 Production — approval flow, versioned output | Works; no structured approval |
| Strategic Deals | 🟡 Partial — Layer 2 modules built | 🟢 Production — enterprise deal room with governance | Code exists; no governance integration |
| Affiliate System | 🟡 Partial — recruitment, onboarding, commissions | 🟢 Production — fraud detection, compliance, SLA | Works; needs trust fabric |
| Executive Dashboard | 🟠 Current — basic dashboard views | 🟢 Production — executive room with evidence packs | Basic views; no decision-grade dashboards |
| Guarantee System | 🟡 Partial — gold guarantee claims | 🟢 Production — auditable, policy-gated | Works; needs trust integration |

---

## ملخص النضج حسب الطبقة

| Plane | 🔴 Not Started | 🟠 Current | 🟡 Partial | 🔵 Pilot | 🟢 Production |
|-------|---------------|-----------|-----------|---------|--------------|
| Decision | 5 | 1 | 1 | 0 | 0 |
| Execution | 4 | 1 | 1 | 0 | 0 |
| Trust | 3 | 0 | 5 | 0 | 0 |
| Data | 4 | 3 | 4 | 0 | 0 |
| Operating | 5 | 1 | 3 | 0 | 0 |
| Saudi | 5 | 1 | 1 | 0 | 0 |
| **Total** | **26** | **7** | **15** | **0** | **0** |

> **القراءة:** 48 نظام فرعي مُتتبَّع. صفر في Production. 15 في Partial (أساس قوي). 26 لم تبدأ بعد (الفجوة الرئيسية). البرنامج يهدف لنقل الجميع إلى 🟢 Production.

---

*هذا السجل يُحدَّث في نهاية كل sprint. كل تغيير حالة يتطلب evidence gate من المصفوفة التنفيذية.*
