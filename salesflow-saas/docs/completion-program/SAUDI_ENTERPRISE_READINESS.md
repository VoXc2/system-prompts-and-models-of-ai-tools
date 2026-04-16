# Saudi Enterprise Readiness Matrix — مصفوفة الجاهزية المؤسسية السعودية

**Version**: 1.0  
**Date**: 2026-04-16  
**Status**: active  
**Owner**: Compliance Lead + Security Lead  
**Regulatory References**: PDPL (نظام حماية البيانات الشخصية), NCA ECC-2:2024, NIST AI RMF, OWASP LLM Top 10, SDAIA  

---

## Part A: PDPL Data Classification Matrix (مصفوفة تصنيف البيانات)

### Classification Levels

| Level | Arabic | Definition | Handling |
|-------|--------|------------|----------|
| **Public** | عام | Published marketing/product info | No restrictions |
| **Internal** | داخلي | Operational data, non-personal | Access control, no external sharing without review |
| **Confidential** | سري | Personal data, financial data, contracts | Encryption, audit trail, consent required, PDPL scope |
| **Restricted** | مقيد | Sensitive personal data (health, financial, biometric), AI model weights | Maximum protection, explicit consent, DPO oversight, NCA reporting |

### Data Field Classification Register

| Data Category | Example Fields | Classification | Processing Purpose | Lawful Basis | Retention | Residency |
|--------------|---------------|----------------|-------------------|-------------|-----------|-----------|
| **Lead PII** | name, email, phone, company | Confidential | Sales qualification | Consent (Art. 6) | Active + 24 months | Saudi/GCC |
| **Deal Financial** | deal_value, commission, payment_amount | Confidential | Revenue management | Contract performance | Active + 7 years (ZATCA) | Saudi/GCC |
| **Consent Records** | consent_purpose, consent_channel, timestamp | Confidential | PDPL compliance | Legal obligation | Perpetual (audit) | Saudi/GCC |
| **AI Conversation Logs** | messages, intent, sentiment | Confidential | Service improvement | Legitimate interest + consent | Active + 12 months | Saudi/GCC |
| **Authentication Data** | password_hash, JWT tokens, session_id | Restricted | Access control | Contract performance | Session duration | Saudi/GCC |
| **Tenant Config** | settings, feature_flags, branding | Internal | Platform operation | Contract performance | Active + 90 days | Saudi/GCC |
| **Analytics Aggregates** | KPIs, forecasts, scores | Internal | Business intelligence | Legitimate interest | 36 months rolling | Saudi/GCC |
| **Marketing Content** | proposals, presentations, collateral | Internal | GTM operations | Legitimate interest | Indefinite | Any |
| **Audit Logs** | action, actor, timestamp, resource | Confidential | Compliance + security | Legal obligation | 7 years | Saudi/GCC |
| **Agent Outputs** | decisions, memos, evidence packs | Confidential | Business operations | Contract performance | Active + 24 months | Saudi/GCC |
| **WhatsApp Messages** | inbound/outbound messages, media | Confidential | Sales communication | Consent | Active + 12 months | Saudi/GCC |
| **Employee/Agent Identity** | agent_role, permissions, service_id | Internal | Platform operation | Contract performance | Active + 90 days | Saudi/GCC |

### Data Subject Rights Implementation Map

| Right | PDPL Article | Implementation | Module | Status |
|-------|-------------|----------------|--------|--------|
| Right to be informed | Art. 12 | Privacy policy (AR/EN), consent forms | `docs/legal/privacy-policy-ar.md` | 🟡 Partial |
| Right of access | Art. 13 | JSON export of all personal data | `services/pdpl/data_rights.py` | 🟡 Partial |
| Right to correction | Art. 14 | Update with audit trail | `services/pdpl/data_rights.py` | 🟡 Partial |
| Right to deletion | Art. 15 | Soft-delete → 30-day hard-delete | `services/pdpl/data_rights.py` | 🟡 Partial |
| Right to restrict processing | Art. 16 | Flag and enforce across all services | `services/pdpl/consent_manager.py` | 🟡 Partial |
| Right to data portability | Art. 17 | Machine-readable export | Not implemented | 🔴 Target |
| Right to object | Art. 18 | Opt-out from automated processing | Not implemented | 🔴 Target |
| Right re: automated decisions | Art. 19 | Human review of AI decisions | `openclaw/policy.py` (Class B/C) | 🟡 Partial |

---

## Part B: NCA ECC-2:2024 Readiness Matrix (مصفوفة الجاهزية لضوابط الأمن السيبراني)

### ECC Domain Mapping

| ECC Domain | Sub-Domain | Dealix Current State | Gap | Remediation Plan | Priority |
|-----------|-----------|---------------------|-----|-----------------|----------|
| **1. Cybersecurity Governance** | 1-1: Cybersecurity Strategy | MASTER-BLUEPRINT defines security posture | No formal cybersecurity strategy document | Create standalone cybersecurity strategy aligned with blueprint | P1 |
| | 1-2: Cybersecurity Management | AGENTS.md policy classes (A/B/C) | Not mapped to NCA format | Translate policy classes to NCA-compatible format | P2 |
| | 1-3: Cybersecurity Policies | `memory/security/pdpl-checklist.md` | Checklist format, not policy format | Convert to formal policy documents | P2 |
| | 1-4: Cybersecurity Roles | Hermes profiles define roles | No dedicated security role beyond Hermes | Define CISO/DPO responsibilities; assign to team | P1 |
| **2. Cybersecurity Defense** | 2-1: Asset Management | Docker Compose + model files | No formal asset inventory | Create asset register from code inventory | P2 |
| | 2-2: Identity & Access | JWT auth + tenant isolation | Single auth mechanism; no MFA; no SSO | Implement Keycloak (WS-4.5); add MFA | P1 |
| | 2-3: Information Protection | Encryption in transit (TLS) | No encryption at rest documented; no DLP | Add TDE or app-level encryption; DLP scanning | P1 |
| | 2-4: Network Security | Nginx reverse proxy | No WAF; no network segmentation documented | Add WAF; document network architecture | P2 |
| | 2-5: Application Security | Input validation via Pydantic | No SAST/DAST pipeline; no dependency scanning | Add security scanning to CI (WS-6) | P1 |
| | 2-6: Security Monitoring | `shannon_security.py` scanner | No SIEM; no real-time alerting | Add SIEM (WS-6.7); real-time alerts | P1 |
| **3. Cybersecurity Resilience** | 3-1: Business Continuity | Docker Compose for dev | No BCP/DR plan | Create BCP; define RPO/RTO | P1 |
| | 3-2: Disaster Recovery | No DR documented | No DR site or failover | Define DR strategy; test failover | P2 |
| | 3-3: Incident Management | No incident process | No incident response plan | Create incident response runbook | P1 |
| **4. Third-Party Security** | 4-1: Third-Party Management | OpenClaw plugins for 6 vendors | No vendor security assessment process | Create vendor security questionnaire; assess critical vendors | P2 |
| | 4-2: Cloud Security | Docker-based deployment | No cloud security baseline | Define cloud security policy aligned with CSP controls | P2 |

---

## Part C: NIST AI RMF Mapping (إطار إدارة مخاطر الذكاء الاصطناعي)

### NIST AI RMF Functions → Dealix Controls

| Function | Category | NIST Requirement | Dealix Current Control | Gap | Target Control |
|----------|---------|-----------------|----------------------|-----|---------------|
| **GOVERN** | Policies | AI governance policies defined | AGENTS.md policy classes; MASTER-BLUEPRINT principles | Not AI-specific; mixed with general policy | Dedicated AI governance policy document |
| | Accountability | Clear accountability for AI decisions | Hermes profiles; `approval_bridge.py` | No AI-specific accountability chain | Role-based AI accountability with DPO oversight |
| | Transparency | AI decision transparency | `tool_receipts.py` captures post-hoc | No proactive transparency; no explainability | Evidence packs (WS-2.3); Decision memos (WS-2.4) |
| **MAP** | Context | AI system context documented | MASTER-BLUEPRINT agent descriptions | No formal AI system inventory | AI system register: purpose, data, risks per agent |
| | Risk identification | AI-specific risks catalogued | Not catalogued | No AI risk register | AI risk register per NIST AI RMF categories |
| | Stakeholder impact | Impact on data subjects assessed | PDPL checklist | No AI-specific DPIA | AI impact assessment per agent type |
| **MEASURE** | Performance | AI performance metrics | `lead_scoring.py`, `forecasting.py` | No systematic evaluation | Offline eval datasets (WS-6.9); quality metrics |
| | Bias testing | Bias and fairness evaluation | Not implemented | No bias testing | Arabic/Saudi-specific bias testing suite |
| | Robustness | Adversarial testing | Not implemented | No adversarial testing | Red-team coverage (WS-6.10); prompt injection tests |
| **MANAGE** | Risk mitigation | AI risk mitigation controls | `security_gate.py`; `openclaw/hooks.py` | Scattered; not systematic | OPA policy packs (WS-4.2); verification ledger (WS-4.6) |
| | Monitoring | AI system monitoring | `observability.py` | No AI-specific monitoring | OTel for LLM calls (WS-6.8); drift detection |
| | Incident response | AI incident handling | No AI incident process | No AI-specific incident response | AI incident response runbook; contradiction dashboard (WS-4.7) |

---

## Part D: OWASP LLM Top 10 Controls (2025) — ضوابط أمان النماذج اللغوية

| # | OWASP Risk | Dealix Exposure | Current Mitigation | Gap | Target Control | Release Gate |
|---|-----------|----------------|-------------------|-----|---------------|-------------|
| LLM01 | Prompt Injection | All agent prompts | System prompts in code | No input sanitization for indirect injection | Prompt shield + input validation layer | Required |
| LLM02 | Insecure Output Handling | Agent → tool → external system | `tool_verification.py` (advisory) | No mandatory output validation | Structured Outputs (WS-2.2) + verification ledger (WS-4.6) | Required |
| LLM03 | Training Data Poisoning | pgvector knowledge base | `knowledge_service.py` access control | No ingestion validation | Content validation pipeline; source provenance | Recommended |
| LLM04 | Model Denial of Service | LLM API calls | Rate limiting in `model_router.py` | No per-tenant LLM budget enforcement | Token budget per tenant; circuit breaker per provider | Required |
| LLM05 | Supply Chain Vulnerabilities | LLM providers (Groq, OpenAI) | Multi-provider fallback | No provider security assessment | Vendor security questionnaire; API key rotation via Vault | Recommended |
| LLM06 | Sensitive Information Disclosure | Agent context includes tenant data | Tenant isolation at DB level | No prompt-level data leakage prevention | Prompt sanitization; PII redaction in LLM context | Required |
| LLM07 | Insecure Plugin Design | 6 OpenClaw plugins | `openclaw/policy.py` action classification | Plugins can call external APIs without granular authorization | OpenFGA per-plugin authorization (WS-4.3) | Required |
| LLM08 | Excessive Agency | Agents can trigger external actions | `before_agent_reply` hook; Class B/C gating | Not all actions gated; no mandatory evidence | Tool verification ledger mandatory (WS-4.6) | Required |
| LLM09 | Overreliance | Users trust agent recommendations | Evidence links in some outputs | No confidence display; no uncertainty communication | Confidence scores (WS-2.5); uncertainty indicators in UI | Recommended |
| LLM10 | Model Theft | Model routing configuration | Config in code (not secrets) | Prompt templates in plain text | Vault for sensitive prompts; access logging | Recommended |

---

## Part E: Data Residency & Cross-Border Transfer Controls (ضوابط إقامة البيانات)

### Residency Rules

| Data Type | Required Residency | Transfer Allowed To | Conditions |
|-----------|-------------------|--------------------|-----------| 
| Personal data (Saudi nationals) | Saudi Arabia | GCC with adequate protection | Written consent + contractual safeguards |
| Financial/ZATCA data | Saudi Arabia | None | No cross-border transfer |
| AI conversation logs | Saudi/GCC | None without consent | Purpose limitation applies |
| Aggregated analytics | Saudi/GCC | Any (anonymized only) | Must be truly anonymized per PDPL |
| Authentication credentials | Saudi/GCC | None | Security requirement |
| Audit logs | Saudi Arabia | None | Regulatory retention requirement |

### Policy Engine Integration

These rules must be enforced as **runtime policy** in the policy engine (OPA), not just documentation:

```
# Target OPA policy structure (pseudocode)
package dealix.data_residency

default allow_transfer = false

allow_transfer {
    input.data_classification == "public"
}

allow_transfer {
    input.data_classification == "internal"
    input.destination_region in {"SA", "AE", "BH", "KW", "OM", "QA"}
}

allow_transfer {
    input.data_classification in {"confidential", "restricted"}
    input.destination_region in {"SA", "AE", "BH", "KW", "OM", "QA"}
    input.consent_granted == true
    input.safeguards_documented == true
}
```

---

## Part F: Implementation Roadmap

| Phase | Focus | Deliverables | Target |
|-------|-------|-------------|--------|
| **Phase 1** | Data audit | Complete data field classification; processing register | WS-7.1, 7.2 |
| **Phase 2** | Policy enforcement | Residency flags in policy engine; OPA rules | WS-7.3, WS-4.2 |
| **Phase 3** | NCA alignment | ECC gap register; remediation plan | WS-7.4 |
| **Phase 4** | AI governance | NIST AI RMF mapping; bias/adversarial testing | WS-7.5 |
| **Phase 5** | Release integration | OWASP LLM checklist per release; red-team report | WS-7.6, WS-6.10 |
| **Phase 6** | Certification prep | SDAIA registration; external audit engagement | Post WS-7 |

---

## Regulatory Update Log

| Date | Regulation | Update | Impact on Dealix |
|------|-----------|--------|-----------------|
| 2024-09 | NCA ECC-2:2024 | Updated Essential Cybersecurity Controls | Requires fresh gap analysis |
| 2024-03 | PDPL | Implementing regulations published | Consent and DSAR requirements clarified |
| 2023-09 | PDPL | Entered into force | All personal data processing must comply |
| 2024-01 | NIST AI RMF | v1.0 widely adopted | Framework for AI governance mapping |
| 2025-11 | OWASP LLM Top 10 | 2025 edition | Updated risk categories for LLM applications |

---

## Navigation

| Document | Purpose |
|----------|---------|
| [COMPLETION_PROGRAM.md](./COMPLETION_PROGRAM.md) | Master program with 5 planes and 8 gaps |
| [EXECUTION_MATRIX.md](./EXECUTION_MATRIX.md) | Full workstream matrix with WS-7 details |
| [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Enterprise readiness checklist (Section 6: Saudi) |
| [PDPL Checklist](../../memory/security/pdpl-checklist.md) | Original PDPL pre-launch checklist |
| [Privacy Policy AR](../legal/privacy-policy-ar.md) | Arabic privacy policy |
| [Data Protection AR](../legal/data-protection-ar.md) | Arabic data protection notice |
