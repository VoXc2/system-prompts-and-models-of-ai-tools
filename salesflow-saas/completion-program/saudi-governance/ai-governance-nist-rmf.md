# AI Governance Profile — NIST AI RMF Mapping

> **Version:** 1.0 — 2026-04-16
> **Framework:** NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0)
> **Supplementary:** OWASP LLM Top 10, Saudi PDPL, NCA ECC 2-2024
> **Authority:** Compliance Lead + AI Lead

---

## NIST AI RMF Core Functions

### GOVERN

> Policies, processes, and accountability structures for AI risk management.

| Sub-function | Requirement | Dealix Control | Status | Owner |
|-------------|------------|---------------|--------|-------|
| GOV-1.1 | AI risk policies established | `AGENTS.md` policy classes A/B/C; agent role registry | 🟡 Partial | AI Lead |
| GOV-1.2 | Accountability defined for AI outcomes | Agent role registry (Observer/Recommender/Executor) | 🟡 Partial | AI Lead |
| GOV-1.3 | Senior leadership oversight of AI risk | Executive Room dashboard (planned) | ❌ Gap | Product Lead |
| GOV-2.1 | Diverse teams involved in AI design | Multi-role review in AGENTS.md | 🟡 Partial | All Leads |
| GOV-3.1 | AI risk identified in organisational risk register | Risk register schema (this release) | 🔶 Pilot | Compliance Lead |
| GOV-4.1 | AI risk management integrated into enterprise risk | NCA ECC readiness register + risk_register_json | 🟡 Partial | Security Lead |
| GOV-5.1 | Policies for AI transparency and explainability | Evidence pack + provenance/confidence scores | 🟡 Partial | AI Lead |
| GOV-5.2 | Policies for AI fairness and bias | Not yet implemented | ❌ Gap | AI Lead |
| GOV-6.1 | Policies for AI supply chain risk | OWASP LLM checklist (planned) | ❌ Gap | AI Lead + Security Lead |

### MAP

> Identify AI risks in context.

| Sub-function | Requirement | Dealix Control | Status | Owner |
|-------------|------------|---------------|--------|-------|
| MAP-1.1 | AI system purpose and context documented | MASTER-BLUEPRINT.mdc; agent-role-registry.md | ✅ Done | Platform Architect |
| MAP-1.5 | Organisational risk tolerance defined | Risk thresholds in agent_sensitivity.rego | 🟡 Partial | Security Lead |
| MAP-2.1 | Scientific and domain knowledge informing AI | Sector KB (pgvector) + KnowledgeService | 🔶 Pilot | AI Lead |
| MAP-2.2 | Practitioner team skills assessed | Not formally documented | ❌ Gap | Team Lead |
| MAP-3.1 | AI risks identified and documented | Risk register schema; NCA ECC gap register | 🟡 Partial | Compliance Lead |
| MAP-3.5 | Likelihood and impact of harms assessed | Risk register `likelihood` + `impact` fields | 🔶 Pilot | Compliance Lead |
| MAP-5.1 | Practices for AI system testing documented | `generate-tests.md` claude command; eval plan | 🟡 Partial | AI Lead |
| MAP-5.2 | AI system risks evaluated | Tool verification ledger (planned) | ❌ Gap | AI Lead |

### MEASURE

> Analyse, assess, and benchmark AI risks.

| Sub-function | Requirement | Dealix Control | Status | Owner |
|-------------|------------|---------------|--------|-------|
| MEA-1.1 | Metrics for AI risk identified | Confidence/provenance/freshness scores | 🔶 Pilot | AI Lead |
| MEA-2.1 | Evaluations of AI system | Offline eval datasets (planned) | ❌ Gap | AI Lead |
| MEA-2.2 | Evaluations of AI data | Great Expectations data quality gates (planned) | ❌ Gap | Data Engineer |
| MEA-2.3 | AI system performance monitored | OTel traces/metrics (planned) | ❌ Gap | Platform Engineer |
| MEA-2.5 | Privacy risks of AI system evaluated | PDPL classification matrix (this release) | 🟡 Partial | Compliance Lead |
| MEA-2.6 | Security risks of AI system evaluated | OWASP LLM Top 10 checklist (planned) | ❌ Gap | Security Lead |
| MEA-3.1 | Bias testing performed | Not implemented | ❌ Gap | AI Lead |
| MEA-4.1 | AI risk metrics tracked over time | Contradiction dashboard (planned) | ❌ Gap | AI Lead |

### MANAGE

> Prioritise and address AI risks.

| Sub-function | Requirement | Dealix Control | Status | Owner |
|-------------|------------|---------------|--------|-------|
| MAN-1.1 | Risks mitigated or accepted | Risk register + OPA policy enforcement | 🟡 Partial | Security Lead |
| MAN-1.3 | Incident response for AI failures | Tool verification ledger + contradiction dashboard | ❌ Gap | AI Lead |
| MAN-2.2 | Mechanisms to sustain and improve | Evidence pack generator + offline evals | ❌ Gap | AI Lead |
| MAN-2.4 | Data quality maintained | Great Expectations (planned) | ❌ Gap | Data Engineer |
| MAN-3.1 | AI incidents tracked and remediated | Contradiction dashboard + policy violations board | ❌ Gap | AI Lead + Platform |
| MAN-4.1 | Risk management plans updated | Quarterly review of this register | 🟡 Partial | Compliance Lead |
| MAN-4.2 | Decommissioning AI systems safely | Agent deprecation runbook (planned) | ❌ Gap | AI Lead |

---

## OWASP LLM Top 10 — Per-Release Checklist Template

File: `saudi-governance/owasp-llm-checklist.md`

| # | Vulnerability | Check | Pass Criteria | Severity | Gate |
|---|--------------|-------|--------------|---------|------|
| LLM01 | Prompt Injection | Red-team test: inject instructions in user input; verify agent does not execute | Agent ignores injected instructions in 100 % of test cases | CRITICAL | Release blocker |
| LLM02 | Insecure Output Handling | Code review: agent outputs validated against schema before any system action | All Executor outputs validated by `execution_intent.schema.json` | HIGH | Release blocker |
| LLM03 | Training Data Poisoning | Review KB data sources; no user-controlled content in KB without review | KB ingestion pipeline has human review gate | HIGH | Release blocker |
| LLM04 | Model Denial of Service | Load test: 1000 concurrent agent requests; latency within SLA | p95 < 5 s; no OOM; no cascade failure | MEDIUM | Release warning |
| LLM05 | Supply Chain Vulnerabilities | Dependency scan (Trivy + Dependabot); no CRITICAL CVEs in LLM SDK | Zero CRITICAL CVEs unpatched | HIGH | Release blocker |
| LLM06 | Sensitive Information Disclosure | Code review: no raw personal data in agent prompt; KB chunks anonymised | Automated scan: no national ID / phone / email patterns in prompts | CRITICAL | Release blocker |
| LLM07 | Insecure Plugin Design | Verify all tool calls go through `BaseConnector` facade + OPA check | `rg 'requests.get\|httpx.get'` returns zero direct HTTP calls in agent code | HIGH | Release blocker |
| LLM08 | Excessive Agency | Verify Executor agents require approval_packet_id for HIGH/CRITICAL actions | OPA test: high-sensitivity action without packet returns 403 | CRITICAL | Release blocker |
| LLM09 | Overreliance | HITL gates present for all critical decisions; confidence scores displayed | HITL interrupt in LangGraph for all Executor paths above threshold | HIGH | Release blocker |
| LLM10 | Model Theft | API rate limiting + authentication on all LLM-proxied endpoints | No unauthenticated LLM access; Keycloak token required | MEDIUM | Release warning |

---

## Saudi-Specific AI Governance Additions

| Control | Requirement Source | Dealix Implementation |
|---------|------------------|----------------------|
| AI decisions affecting individuals must be explainable | PDPL Art. 20 (automated decisions) | Evidence pack + memo bilingual (AR/EN) |
| AI used for profiling must have legal basis | PDPL Art. 25 | Consent record required before lead profiling |
| AI systems in critical sectors require SDAIA assessment | SDAIA AI Ethics Principles | Register with SDAIA if deployed in health/finance |
| Data used for AI training must comply with PDPL | PDPL Art. 26 | No personal data used for model fine-tuning without consent |
| AI system risk classification | SDAIA AI Ethics Principles (2024) | Dealix classified as "High-impact AI" → enhanced oversight required |
