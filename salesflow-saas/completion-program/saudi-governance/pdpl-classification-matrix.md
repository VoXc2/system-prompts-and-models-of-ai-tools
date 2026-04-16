# PDPL Data Classification Matrix

> **Version:** 1.0 — 2026-04-16
> **Regulation:** Saudi Personal Data Protection Law (PDPL) + Implementing Regulations (SDAIA)
> **Authority:** Compliance Lead — must be reviewed by legal counsel before production deployment.
> **Update Frequency:** Review quarterly and after any new data collection or processing change.

---

## Classification Tiers

| Tier | Definition | PDPL Category | Examples in Dealix |
|------|-----------|--------------|-------------------|
| **Public** | Information intentionally made public | Not personal data | Company names, public sector info, published pricing |
| **Internal** | Business data with no personal identifier | Not personal data | Aggregated sales metrics, anonymised analytics |
| **Confidential** | Business-sensitive, non-personal | Not personal data | Deal terms, strategy documents, API keys |
| **Personal** | Any data that identifies or can identify a natural person | Personal data (PDPL Art. 1) | Full name, national ID (هوية), email, phone, address |
| **Sensitive-Personal** | PDPL Art. 23 special categories | Sensitive personal data | Health data, biometric, criminal records, religious/political views, financial data in some contexts |

---

## Data Types in Dealix — Classification Table

| Data Type | Storage Location | Classification | Legal Basis for Processing | Retention Period | Cross-border Transfer Allowed? | Notes |
|-----------|----------------|---------------|--------------------------|-----------------|-------------------------------|-------|
| Company name | Postgres `companies.name` | Public | Legitimate interest / Contract | Duration of relationship + 5 years | Yes (no restriction) | B2B entity, not personal |
| Contact full name | Postgres `contacts.full_name` | Personal | Consent / Contract | Duration of relationship + 3 years | Only with transfer mechanism | PDPL Art. 5 |
| Contact email | Postgres `contacts.email` | Personal | Consent / Contract | Duration of relationship + 3 years | Only with transfer mechanism | |
| Contact phone (WhatsApp) | Postgres `contacts.phone` | Personal | Consent / Contract | Duration of relationship + 3 years | Only with transfer mechanism | |
| National ID (هوية وطنية) | Not stored (collected only for KYC if required) | Sensitive-Personal | Legal obligation / Explicit consent | Minimum retention per PDPL | **No** — KSA only | Must be encrypted at rest |
| IP addresses | Logs / OTel telemetry | Personal (pseudonymous) | Legitimate interest | 90 days | Only with transfer mechanism | Anonymise after 90 days |
| WhatsApp conversation logs | Postgres `conversations` | Personal | Consent / Contract | 1 year | **No** — KSA only | End-to-end encryption required |
| Deal financial terms | Postgres `deals.value` | Confidential | Contract | Duration + 7 years (accounting) | Yes (contractual) | If linked to individual: Personal |
| Partner representative data | Postgres `partners.contact_*` | Personal | Contract | Duration + 3 years | Only with transfer mechanism | |
| AI agent decision logs (with user ref) | Postgres `agent_decisions` | Personal | Legitimate interest / Legal obligation | 2 years | **No** — KSA only | Must support DSAR erasure |
| Embedding vectors (pgvector) | pgvector `embeddings` | Confidential / Personal (if personal text embedded) | Consent / Contract | Same as source data | Same as source data | Anonymise if source personal |
| Billing/payment data | External PSP (not stored raw) | Sensitive-Personal | Contract / Legal obligation | Per PSP + 7 years | PSP contract governs | Never store raw card data (PCI-DSS) |
| User authentication tokens | Redis (TTL) | Personal | Contract | Session lifetime (max 24 h) | **No** — KSA only | |
| DSAR (data subject requests) | Postgres `dsar_requests` | Personal | Legal obligation | 3 years | **No** — KSA only | Must respond within 30 days (PDPL Art. 13) |
| Audit logs (with user actions) | Postgres / SIEM | Personal | Legal obligation | 5 years (NCA ECC requirement) | SIEM location must be KSA or adequate | |

---

## Personal Data Processing Register (Summary)

Full register: `pdpl-processing-register.md`

| Processing Activity | Purpose | Legal Basis | Data Types | Retention | Transfer? |
|--------------------|---------|-----------|-----------|-----------|-----------| 
| Sales outreach via WhatsApp | Commercial communication | Consent (opt-in) | Phone, name | 1 year post-opt-out | No |
| CRM record management | Contract management | Contract | Name, email, phone, role | Duration + 3 years | With mechanism |
| AI recommendation generation | Legitimate business interest | Legitimate interest | Anonymised deal context | 2 years | No |
| Partner onboarding | Contract | Contract | Representative personal data | Duration + 3 years | With mechanism |
| Billing and invoicing | Legal obligation | Contract + legal obligation | Billing contact, amounts | 7 years | PSP governs |
| Security and audit logging | Legal obligation (NCA ECC) | Legal obligation | IP, user actions | 5 years | KSA / adequate country only |
| DSAR fulfilment | Legal obligation (PDPL Art. 13) | Legal obligation | All personal data held | 3 years | No |

---

## Consent Management Requirements

Per PDPL Art. 6 + 10:

| Requirement | Implementation | Status |
|------------|---------------|--------|
| Consent must be explicit and unambiguous | Opt-in checkbox, not pre-ticked | 🟡 Partial |
| Consent must be purpose-specific | Separate consent per use case (outreach, analytics, etc.) | 🟡 Partial |
| Consent withdrawal must be as easy as giving it | Opt-out link in every WhatsApp + email communication | 🟡 Partial |
| Consent record must be stored and auditable | `consent_records` table with timestamp, purpose, version | 🟡 Partial |
| Consent for children (under 18) must be from guardian | Age gate on registration | ⬜ Planned |

**OPA policy enforcement:** `pdpl_consent.rego` blocks personal data processing if no valid consent record exists.

---

## Data Subject Rights — Response SLA

| Right | PDPL Article | SLA | Implementation |
|-------|-------------|-----|---------------|
| Right to access | Art. 13 | 30 days | DSAR portal (planned) |
| Right to correction | Art. 14 | 30 days | DSAR portal |
| Right to erasure | Art. 15 | 30 days | Soft-delete + anonymisation pipeline |
| Right to data portability | Art. 16 | 30 days | JSON export endpoint |
| Right to object to processing | Art. 17 | Immediate (for marketing) | Opt-out webhook |

---

## Cross-Border Transfer Mechanisms

PDPL Art. 29 requires one of:

| Mechanism | Use Case in Dealix |
|-----------|-------------------|
| Adequacy decision by SDAIA | Monitor SDAIA list; use if available for target country |
| Standard Contractual Clauses (SCCs) | Primary mechanism for EU-based vendors (e.g. cloud providers) |
| Explicit data subject consent | Last resort; consent must be informed and specific |
| Vital interests | Emergency only |

**OPA `data_residency.rego`** enforces: personal data destined for non-KSA systems must have a `transfer_mechanism` field set.

---

## Data Residency Requirements

| Data Classification | Permitted Processing Locations |
|--------------------|---------------------------------|
| Public | Any |
| Internal / Confidential | Any (business-controlled) |
| Personal | KSA preferred; non-KSA only with transfer mechanism |
| Sensitive-Personal | **KSA only** — no cross-border without SDAIA approval |

**Infrastructure:** All production Postgres, Redis, pgvector, and Temporal instances must be in KSA region (AWS ap-east-1/me-south-1 or equivalent). SIEM streaming to non-KSA must use SCCs.
