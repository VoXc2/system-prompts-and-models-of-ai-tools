# NCA ECC 2-2024 Readiness Gap Register

> **Version:** 1.0 — 2026-04-16
> **Regulation:** NCA Essential Cybersecurity Controls (ECC) version 2-2024
> **Authority:** CISO / Security Lead — reviewed at each quarterly security review.
> **Status Key:** ✅ Compliant · 🟡 Partial · ❌ Gap · N/A Not Applicable

---

## Control Domains

### Domain 1 — Cybersecurity Governance

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-1-1 | Cybersecurity Policy | 🟡 Partial | Policy exists informally in AGENTS.md / SECURITY.md; not a formal ISO-27001-style document | Security Lead | Sprint 2 | Audit finding if not formalised |
| ECC-1-2 | Cybersecurity Roles & Responsibilities | 🟡 Partial | Roles exist in AGENTS.md; not mapped to formal RACI | Security Lead | Sprint 2 | Confusion in incident response |
| ECC-1-3 | Cybersecurity Risk Management | ❌ Gap | No formal risk register; risks implicit in docs | Security Lead | Sprint 3 | No baseline → unmanaged exposure |
| ECC-1-4 | Cybersecurity Compliance | 🟡 Partial | PDPL checklist exists; NCA ECC not formally mapped until this document | Security Lead | Sprint 2 | Regulatory exposure |
| ECC-1-5 | Third-Party Cybersecurity | ❌ Gap | No vendor security assessment process | Security Lead | Sprint 4 | Third-party breach propagation |

### Domain 2 — Asset Management

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-2-1 | Asset Inventory | ❌ Gap | No formal IT/data asset inventory; code has models but no catalogued asset register | Platform Engineer | Sprint 3 | Unknown attack surface |
| ECC-2-2 | Asset Classification | 🟡 Partial | PDPL matrix covers data; system assets not classified | Security Lead | Sprint 3 | Misconfigured asset exposure |
| ECC-2-3 | Asset Handling | ❌ Gap | No formal data handling procedures for physical media | Platform Engineer | Sprint 4 | Physical data leak |

### Domain 3 — Identity & Access Management

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-3-1 | Identity Management | 🟡 Partial | Custom JWT; no centralised IAM | Platform Engineer | Sprint 4 (Keycloak) | Credential sprawl |
| ECC-3-2 | Access Control | 🟡 Partial | Role-based in code; no OPA/OpenFGA yet | Security Lead | Sprint 3 | Over-privilege |
| ECC-3-3 | Privileged Access Management | ❌ Gap | No PAM tool; admin access not logged separately | Security Lead | Sprint 4 | Admin account compromise |
| ECC-3-4 | Authentication | 🟡 Partial | Password + JWT; no MFA enforced | Platform Engineer | Sprint 4 | Account takeover |
| ECC-3-5 | Access Review | ❌ Gap | No periodic access review process | Security Lead | Sprint 5 | Privilege accumulation |

### Domain 4 — Information Security

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-4-1 | Data Protection | 🟡 Partial | Postgres encryption at rest (cloud provider); transit TLS; no field-level encryption for Sensitive-Personal | Backend Lead | Sprint 3 | Sensitive data exposure in DB dump |
| ECC-4-2 | Cryptography | 🟡 Partial | TLS 1.2+ in use; no formal cryptographic standard document | Security Lead | Sprint 3 | Weak algorithm usage |
| ECC-4-3 | Backup & Recovery | 🟡 Partial | Cloud-managed backups; no tested recovery runbook | Platform Engineer | Sprint 3 | Data loss on incident |
| ECC-4-4 | Secure Development | 🟡 Partial | GitHub Actions CI; no SAST/DAST pipeline | Platform Engineer | Sprint 3 | Vulnerability in production |
| ECC-4-5 | Vulnerability Management | ❌ Gap | No formal vulnerability scanning schedule | Security Lead | Sprint 3 | Unpatched critical CVEs |

### Domain 5 — Third-Party & Cloud Security

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-5-1 | Cloud Security | 🟡 Partial | Cloud provider used; no cloud security baseline documented | Platform Engineer | Sprint 3 | Misconfigured cloud resource |
| ECC-5-2 | API Security | 🟡 Partial | FastAPI with auth; no API gateway / WAF | Platform Engineer | Sprint 4 | API abuse / injection |
| ECC-5-3 | Third-Party Risk | ❌ Gap | No vendor assessment; OpenAI, Twilio, DocuSign used without formal DPAs reviewed | Compliance Lead | Sprint 3 | Vendor data breach |

### Domain 6 — Human Resources Security

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-6-1 | Security Awareness | ❌ Gap | No formal security awareness training programme | Security Lead | Sprint 4 | Phishing / social engineering |
| ECC-6-2 | Background Checks | N/A | Startup phase; implement at hiring scale | — | — | — |

### Domain 7 — Physical Security

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-7-1 | Physical Access Control | N/A | Cloud-only; no physical data centre | — | — | — |
| ECC-7-2 | Physical Media | N/A | No physical media handling | — | — | — |

### Domain 8 — Security Operations

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-8-1 | Security Monitoring | ❌ Gap | No SIEM; no centralised log aggregation beyond app logs | Security Lead | Sprint 3 (OTel) / Sprint 4 (SIEM) | Attack not detected |
| ECC-8-2 | Incident Management | 🟡 Partial | Runbook exists; no formal incident response plan | Security Lead | Sprint 3 | Slow breach response |
| ECC-8-3 | Threat Intelligence | ❌ Gap | No threat intel feed subscribed | Security Lead | Sprint 5 | Unknown emerging threats |
| ECC-8-4 | Audit Logging | 🟡 Partial | App logs in place; no structured audit log → SIEM | Security Lead | Sprint 3–4 | Forensics gap in breach |

### Domain 9 — Cybersecurity Resilience

| Control ID | Control Name | Status | Gap Description | Owner | Target Sprint | Risk |
|-----------|-------------|--------|----------------|-------|--------------|------|
| ECC-9-1 | Business Continuity | ❌ Gap | No formal BCP | Platform Engineer | Sprint 5 | Extended outage → SLA breach |
| ECC-9-2 | Disaster Recovery | 🟡 Partial | Cloud backups; no tested DR runbook | Platform Engineer | Sprint 4 | Recovery failure |
| ECC-9-3 | Data Backup | 🟡 Partial | Cloud-managed; not validated | Platform Engineer | Sprint 3 | Backup corruption undetected |

---

## Summary Dashboard

| Domain | Compliant | Partial | Gap | N/A | Total Controls |
|--------|-----------|---------|-----|-----|---------------|
| 1 — Governance | 0 | 3 | 2 | 0 | 5 |
| 2 — Asset Management | 0 | 1 | 2 | 0 | 3 |
| 3 — IAM | 0 | 3 | 2 | 0 | 5 |
| 4 — Information Security | 0 | 4 | 1 | 0 | 5 |
| 5 — Third-Party & Cloud | 0 | 2 | 1 | 0 | 3 |
| 6 — HR Security | 0 | 0 | 1 | 1 | 2 |
| 7 — Physical | 0 | 0 | 0 | 2 | 2 |
| 8 — Security Operations | 0 | 2 | 2 | 0 | 4 |
| 9 — Resilience | 0 | 2 | 1 | 0 | 3 |
| **TOTAL** | **0** | **17** | **12** | **3** | **32** |

**Overall Posture: 🔴 HIGH RISK — 12 gaps must be closed before enterprise client onboarding.**

---

## Priority Remediation Plan

### Immediate (Sprint 2–3) — Blocking for Enterprise Sales

1. Formalise cybersecurity policy document (ECC-1-1)
2. Deploy OTel + centralised audit log streaming (ECC-8-1, ECC-8-4)
3. Add SAST (Bandit/Semgrep) to CI pipeline (ECC-4-4)
4. Review and sign DPAs with OpenAI, Twilio, DocuSign (ECC-5-3)
5. Enable Vault for secret management + audit log (ECC-3-3 partial)
6. Enable MFA for all team members on GitHub + cloud console (ECC-3-4)

### Short-term (Sprint 3–4) — Required for Tier-1 Enterprise

1. Deploy OPA + OpenFGA (ECC-3-2)
2. Formal vulnerability scanning (Trivy for containers, Dependabot for deps) (ECC-4-5)
3. Incident response plan document (ECC-8-2)
4. Tested backup recovery runbook (ECC-4-3, ECC-9-3)
5. Cloud security baseline documented (CIS Benchmark subset) (ECC-5-1)

### Medium-term (Sprint 4–6) — Required for Regulated Sectors

1. Keycloak SSO + MFA (ECC-3-1, ECC-3-4)
2. PAM for admin access (ECC-3-3)
3. API gateway / WAF (ECC-5-2)
4. Security awareness training programme (ECC-6-1)
5. Business Continuity Plan (ECC-9-1)
6. Third-party risk assessment process (ECC-1-5, ECC-5-3)
