# Dealix Current-vs-Target Architecture Register — سجل الحالة الحالية مقابل الهدف

**Version**: 1.0  
**Date**: 2026-04-16  
**Status**: active  
**Last Audit**: 2026-04-16 (automated codebase scan)  

---

## Status Legend

| Status | Symbol | Definition |
|--------|--------|------------|
| **Production** | 🟢 | Running in prod or prod-equivalent; tested; monitored |
| **Partial** | 🟡 | Code exists and is functional but incomplete, not fully tested, or lacks enterprise features |
| **Scaffold** | 🟠 | File/class exists with structure but contains placeholder/mock logic |
| **Target** | 🔴 | Documented in architecture but no implementation exists |
| **N/A** | ⚪ | Not applicable to current phase |

---

## 1. Decision Plane Subsystems

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| LLM Provider Abstraction | `services/llm/provider.py` | 🟡 Partial | Groq + OpenAI providers; `LLMRouter` class | Missing: structured outputs, response format enforcement, provider health checks |
| Model Routing | `services/model_router.py` | 🟡 Partial | Task→model routing logic | Missing: cost tracking, latency SLOs, automatic fallback metrics |
| Lead Orchestrator | `ai/orchestrator.py` | 🟡 Partial | State machine for lead lifecycle | Missing: typed outputs, evidence packs, structured decision schemas |
| Agent Router | `ai/agent_router.py` | 🟡 Partial | Intent→agent mapping | Missing: provenance tracking, confidence scoring |
| Agent Executor | `ai/agent_executor.py` | 🟡 Partial | Single agent step execution | Missing: structured output enforcement, evidence generation |
| Decision Memo Compiler | — | 🔴 Target | Not implemented | Full implementation needed: bilingual memos with evidence |
| Evidence Pack Generator | — | 🔴 Target | Not implemented | Full implementation needed: citations, freshness, confidence |
| Provenance Scoring | — | 🔴 Target | Not implemented | Full implementation needed: source tracking, freshness, confidence scores |
| Structured Output Schemas | — | 🔴 Target | Not implemented | Pydantic models for all 5 decision outputs needed |

---

## 2. Execution Plane Subsystems

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| Celery Workers | `workers/celery_app.py` + 6 task modules | 🟢 Production | Beat schedule, 7 task types, Riyadh TZ | Adequate for short-lived tasks |
| Durable Task Flow (OpenClaw) | `openclaw/durable_flow.py` | 🟡 Partial | Checkpoint state machine | Only 2 flows implemented |
| Prospecting Flow | `flows/prospecting_durable_flow.py` | 🟡 Partial | Multi-channel prospecting with checkpoints | Needs compensation, idempotency |
| Self-Improvement Flow | `flows/self_improvement_flow.py` | 🟡 Partial | 6-phase checkpointed flow | Needs production hardening |
| OpenClaw Gateway | `openclaw/gateway.py` | 🟡 Partial | Policy → observability → task router | Needs OTel integration, structured logging |
| OpenClaw Hooks | `openclaw/hooks.py` | 🟡 Partial | `before_agent_reply` governance | Needs tool verification ledger integration |
| Temporal Runtime | — | 🔴 Target | Not implemented | Full implementation needed |
| Compensation Framework | — | 🔴 Target | Not implemented | Saga pattern with rollback needed |
| Idempotency Framework | — | 🔴 Target | Not implemented | Per-workflow dedup needed |
| Workflow Versioning | — | 🔴 Target | Not implemented | Temporal worker versioning needed |

---

## 3. Trust Plane Subsystems

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| JWT Authentication | `services/auth_service.py` + `middleware/internal_api.py` | 🟢 Production | JWT creation, validation, tenant extraction | Adequate baseline; needs SSO upgrade |
| Policy Classification | `openclaw/policy.py` | 🟡 Partial | Safe vs approval-gated classification | Needs centralization to OPA; too many scattered policies |
| Security Gate | `services/security_gate.py` | 🟡 Partial | Binary security decisions | Needs integration with centralized policy engine |
| Approval Bridge | `openclaw/approval_bridge.py` | 🟡 Partial | Central policy gate for OpenClaw | Needs OpenFGA for fine-grained decisions |
| Skill Governance | `services/skill_governance.py` | 🟡 Partial | Skill admission/review | Isolated from central policy |
| Outbound Governance | `services/outbound_governance.py` | 🟡 Partial | Outbound messaging rules | Isolated from central policy |
| Tool Verification | `services/tool_verification.py` | 🟡 Partial | Pre-execution tool verification | Advisory only; needs mandatory evidence chain |
| Tool Receipts | `services/tool_receipts.py` | 🟡 Partial | Post-exec receipts, trust analytics | Missing: actual_execution, side_effects, contradiction_status |
| Autopilot Policy | `services/autopilot.py` | 🟡 Partial | Budgets, approvals, autonomy limits | Needs integration with central policy |
| OPA Policy Engine | — | 🔴 Target | Not implemented | Centralized policy evaluation needed |
| OpenFGA Authorization | — | 🔴 Target | Not implemented | Authorization graph needed |
| Vault Secrets | — | 🔴 Target | Not implemented | Dynamic secrets, audit logging needed |
| Keycloak Identity/SSO | — | 🔴 Target | Not implemented | SSO, service identity needed |
| Contradiction Dashboard | — | 🔴 Target | Not implemented | UI for intended vs actual deltas needed |

---

## 4. Data Plane Subsystems

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| PostgreSQL (Operational DB) | `database.py` + 31 model files | 🟢 Production | Async SQLAlchemy, multi-tenant, Alembic migrations | Solid foundation |
| pgvector (Semantic Memory) | `services/knowledge_service.py` + `models/knowledge.py` | 🟡 Partial | Knowledge articles, sector assets | Needs quality checks, lineage tracking |
| Memory Engine | `services/memory_engine.py` | 🟡 Partial | Pluggable adapters (Redis/file) + evaluator | Needs persistence guarantees, versioning |
| WhatsApp Integration | `integrations/whatsapp.py` + `openclaw/plugins/whatsapp_plugin.py` | 🟡 Partial | Meta Cloud API send + webhook receive | Needs connector facade, versioning, circuit breaker |
| Email Integration | `integrations/email_sender.py` | 🟡 Partial | SMTP/API wrapper | Needs connector facade |
| SMS Integration | `integrations/sms.py` | 🟡 Partial | Provider wrapper | Needs connector facade |
| Stripe Integration | `services/stripe_service.py` + `openclaw/plugins/stripe_plugin.py` | 🟡 Partial | Payment intents, billing | Needs connector facade, idempotency |
| Salesforce Integration | `services/salesforce_agentforce.py` + `openclaw/plugins/salesforce_agentforce_plugin.py` | 🟠 Scaffold | Account 360, opportunity sync | Needs real Salesforce API testing; connector facade |
| Voice Integration | `services/voice_service.py` + `openclaw/plugins/voice_plugin.py` | 🟠 Scaffold | Call trigger | Needs real telephony provider testing |
| Contract Intelligence | `services/contract_intelligence_service.py` + `openclaw/plugins/contract_intelligence_plugin.py` | 🟠 Scaffold | Contract analysis facade | Needs DocuSign/Adobe Sign real integration |
| E-Sign Service | `services/esign_service.py` | 🟠 Scaffold | Mock envelope send | Needs real provider integration |
| LinkedIn Integration | `services/linkedin_service.py` | 🟠 Scaffold | API wrapper | Needs real API testing; connector facade |
| CRM Sync | `services/crm_sync_service.py` | 🟠 Scaffold | Sync abstraction | Needs real CRM testing |
| Airbyte Ingestion | — | 🔴 Target | Not implemented | Connector-based ingestion needed |
| Schema Registry | — | 🔴 Target | Not implemented | Event schema validation needed |
| Data Quality (Great Expectations) | — | 🔴 Target | Not implemented | Quality checks on critical datasets needed |
| Event Contracts (AsyncAPI) | — | 🔴 Target | Not implemented | Documented async event schemas needed |
| Semantic Metrics Layer | — | 🔴 Target | Not implemented | Business metric definitions needed |
| Data Lineage/Catalog | — | 🔴 Target | Not implemented | Single catalog needed |

---

## 5. Operating Plane Subsystems

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| CI Pipeline | `.github/workflows/dealix-ci.yml` | 🟢 Production | pytest + lint + build + Playwright E2E | Solid baseline |
| Repo Hygiene | `salesflow-saas/.github/workflows/repo-hygiene.yml` | 🟢 Production | Required files check, secret blocking | Solid baseline |
| Docker Compose (Local Dev) | `docker-compose.yml` | 🟢 Production | Postgres, Redis, backend, Celery, frontend, nginx | Works for local dev |
| Observability Service | `services/observability.py` | 🟡 Partial | Workflow metrics, anomaly alerts | Needs OTel, trace_id, correlation_id |
| Shannon Security Scanner | `services/shannon_security.py` | 🟡 Partial | Entropy/security scanning reports | Needs integration with release gate |
| Go-Live Matrix | `services/go_live_matrix.py` | 🟡 Partial | Checklist definitions, scoring | Needs operationalization as CI gate |
| GitHub Rulesets | — | 🔴 Target | Not implemented | Branch protection rulesets needed |
| CODEOWNERS | — | 🔴 Target | Not implemented | Ownership file needed |
| GitHub Environments | — | 🔴 Target | Not implemented | dev/staging/canary/prod environments needed |
| OIDC Federation | — | 🔴 Target | Not implemented | GitHub → cloud provider OIDC needed |
| Artifact Attestations | — | 🔴 Target | Not implemented | SLSA provenance needed |
| Audit Log Streaming | — | 🔴 Target | Not implemented | SIEM/warehouse streaming needed |
| OTel Instrumentation | — | 🔴 Target | Not implemented | Traces/metrics/logs needed |
| Eval Datasets | — | 🔴 Target | Not implemented | Offline agent eval needed |
| Red-Team Coverage | — | 🔴 Target | Not implemented | OWASP LLM testing needed |

---

## 6. Agent System

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| Base Agent Framework | `agents/base_agent.py` | 🟡 Partial | Message bus, priorities, base class | Needs `role` enum (Observer/Recommender/Executor) |
| Memory Layer | `agents/memory_layer.py` | 🟡 Partial | Agent memory utilities | Needs Mem0/Letta integration per blueprint |
| Master Agent (CEO) | `agents/master_agent.py` | 🟠 Scaffold | Daily autonomous routine | Needs production hardening, structured outputs |
| Master LangGraph | `agents/master_langgraph.py` | 🟠 Scaffold | Optional LangGraph orchestration | Needs checkpointing, HITL interrupts |
| Infrastructure Agents | `agents/infrastructure/core.py` | 🟡 Partial | CRM, analytics, report, security, scheduler | 5 agents; need structured outputs |
| Prospector Agent | `agents/discovery/prospector_agent.py` | 🟡 Partial | Strategic prospecting | Needs evidence packs |
| Prospecting Crew | `agents/discovery/prospecting_crew.py` | 🟡 Partial | Crew coordination | Needs supervision, structured outputs |
| Lead Engine Agent | `agents/discovery/lead_engine.py` | 🟡 Partial | Lead engine | Needs structured outputs |
| Enrichment Agents | `agents/discovery/enrichment.py` | 🟡 Partial | Data enrichment | Needs connector facades |
| Qualifier Agents | `agents/qualification/qualifiers.py` | 🟡 Partial | Scorer, intent detector | Needs structured outputs, evidence |
| Channel Engagement | `agents/engagement/channels.py` | 🟡 Partial | WhatsApp, LinkedIn, content, onboarding, intel | Needs connector facades |
| Multi-Channel Engagement | `agents/engagement/multi_channel.py` | 🟡 Partial | Email, voice, forecast, conversation intel | Needs connector facades |
| Closer Agents | `agents/revenue/closers.py` | 🟡 Partial | Closer, pricing, market intel | Needs structured outputs, evidence packs |
| Manus Orchestrator | `services/agents/manus_orchestrator.py` | 🟡 Partial | Multi-agent orchestration | Needs integration with decision schemas |

---

## 7. Business Services

| Subsystem | Module(s) | Status | Evidence | Gap to Production |
|-----------|----------|--------|----------|-------------------|
| Lead Management | `services/lead_service.py` + `api/v1/leads.py` | 🟢 Production | CRUD, pipeline transitions | Core flow works |
| Deal Management | `services/deal_service.py` + `api/v1/deals.py` | 🟢 Production | Lifecycle management | Core flow works |
| PDPL Compliance | `services/pdpl/consent_manager.py` + `services/pdpl/data_rights.py` | 🟡 Partial | Consent grant/revoke/check, DSAR flows | Needs PDPL classification matrix, NCA mapping |
| Analytics | `services/analytics_service.py` | 🟡 Partial | Tenant KPIs | Needs semantic metrics, OTel |
| Executive ROI | `services/executive_roi_service.py` | 🟡 Partial | ROI snapshot dicts | Needs real data pipeline |
| CPQ (Quote Engine) | `services/cpq/quote_engine.py` | 🟡 Partial | VAT, multi-currency | Needs production testing |
| CPQ (Proposals) | `services/cpq/proposal_generator.py` | 🟡 Partial | AR/EN proposal sections | Needs production testing |
| Sequence Engine | `services/sequence_engine.py` | 🟡 Partial | Multi-channel sequences | Needs connector facades |
| Affiliate System | `services/affiliate_service.py` + `workers/affiliate_tasks.py` | 🟡 Partial | Program operations + async jobs | Needs commission reconciliation |
| Strategic Deals (15 modules) | `services/strategic_deals/*` | 🟠 Scaffold | 15 modules: deal room, negotiator, twin, taxonomy, etc. | Most are structured scaffolds; need real data + testing |
| Arabic NLP | `services/ai/arabic_nlp.py` | 🟡 Partial | Intent, entities, sentiment | Needs Saudi dialect eval datasets |
| Lead Scoring | `services/ai/lead_scoring.py` | 🟡 Partial | Composite scoring | Needs calibration with real data |
| Forecasting | `services/ai/forecasting.py` | 🟡 Partial | Deal/period forecasting | Needs real data validation |
| Conversation Intelligence | `services/ai/conversation_intelligence.py` | 🟡 Partial | Buying/risk signals | Needs eval datasets |
| Sales Agent (WhatsApp) | `services/ai/sales_agent.py` | 🟡 Partial | Stateful dialogue | Needs production hardening |
| Autonomous Core | `services/autonomous_core.py` | 🟠 Scaffold | Self-improving core with mock stores | Needs real implementation |
| Auto Pipeline | `services/auto_pipeline.py` | 🟠 Scaffold | In-memory stores, mock AI brain | Needs real implementation |
| Signal Selling | `services/signal_selling_service.py` | 🟠 Scaffold | Signal-based recommendations | Needs real signal sources |
| Signal Intelligence | `services/signal_intelligence.py` | 🟠 Scaffold | Ingestion, watchlists | Needs real signal sources |
| Predictive Revenue | `services/predictive_revenue_service.py` | 🟠 Scaffold | Revenue prediction helpers | Needs real data + model |
| ZATCA Compliance | `services/zatca_compliance.py` | 🟡 Partial | Invoice + AML checkers | Needs ZATCA API integration testing |

---

## Summary Statistics

| Status | Count | Percentage |
|--------|-------|------------|
| 🟢 Production | 10 | 11% |
| 🟡 Partial | 43 | 48% |
| 🟠 Scaffold | 12 | 13% |
| 🔴 Target | 25 | 28% |
| **Total** | **90** | **100%** |

### Key Takeaway

**48% of subsystems are partially implemented** — the largest category. This confirms the diagnosis: substantial code exists, but enterprise-grade completion requires hardening the partial implementations and building the 28% target subsystems that form the trust, execution, and operating infrastructure.

---

## Acceptance Gates per Status Transition

| Transition | Gate |
|------------|------|
| Scaffold → Partial | Code compiles; basic unit tests pass; no mock data in critical paths |
| Partial → Pilot | Integration tests pass; works with real (staging) data; structured outputs enforced |
| Pilot → Production | Load tested; OTel instrumented; security reviewed; eval datasets green; PDPL controls verified |
