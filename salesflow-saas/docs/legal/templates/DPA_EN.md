# Data Processing Agreement (DPA) — Dealix (Template)

> **DISCLAIMER**: Template only. Must be reviewed by qualified Saudi counsel before execution.
> **Version**: 1.0 DRAFT

---

## Parties

**Data Controller**: [Customer Legal Entity] ("Customer")
**Data Processor**: [Dealix Legal Entity] ("Dealix")

**Effective Date**: [DATE]

---

## 1. Subject Matter

This DPA governs processing of Personal Data by Dealix on behalf of Customer in connection with the Service defined in the Master Services Agreement / Terms of Service.

---

## 2. Duration

For the duration of the Service subscription + retention periods specified in the Privacy Policy.

---

## 3. Nature and Purpose of Processing

Dealix processes Personal Data to:
- Execute customer-initiated workflows (partner intake, dossier, approvals)
- Generate evidence packs and audit trails
- Provide reporting and executive surfaces
- Operate security, billing, and customer support functions

---

## 4. Categories of Data Subjects

- Customer's employees and authorized users
- Customer's customers, partners, prospects (as entered into the Service)
- Customer's vendors and counterparties

---

## 5. Categories of Personal Data

- Contact information (name, email, phone)
- Professional information (title, company, role)
- Commercial information (deal values, terms — pseudonymized where possible)
- Authentication credentials (hashed)
- Usage logs and audit trails

**Special Categories**: Dealix does NOT process special category data (health, religion, etc.) unless explicitly agreed in writing with additional safeguards.

---

## 6. Processor Obligations

Dealix shall:
1. Process Personal Data only on documented Customer instructions
2. Ensure persons authorized to process are under confidentiality
3. Implement appropriate technical and organizational measures (see Annex II)
4. Not engage sub-processors without Customer prior authorization
5. Assist Customer in responding to Data Subject requests
6. Notify Customer of Personal Data breach within 72 hours of awareness
7. Delete or return Personal Data at end of Service

---

## 7. Sub-Processors

Current authorized sub-processors listed in Annex III. Changes notified 30 days in advance; Customer may object.

Example sub-processors:
- AWS (me-south-1 Bahrain) — infrastructure
- Resend / Postmark — transactional email
- Groq / OpenAI / Anthropic — AI inference (with data controls)
- Stripe / Moyasar — payment processing

---

## 8. International Transfers

Primary processing: AWS me-south-1 (Bahrain).

Transfers outside GCC:
- Only to sub-processors with documented equivalent protections
- Subject to Standard Contractual Clauses or PDPL-compliant transfer mechanisms
- LLM inference: input data tokenized per vendor DPA (e.g., OpenAI zero-retention tier, Anthropic enterprise)

---

## 9. Data Subject Rights

Dealix will assist Customer in responding to requests for:
- Access
- Rectification
- Erasure
- Restriction
- Portability
- Objection
- Withdrawal of consent

Response time: 10 business days from Customer instruction.

---

## 10. Audits

Customer may audit Dealix compliance once per 12-month period with 30 days notice. Audits limited to:
- Policies and procedures
- Third-party audit reports (SOC 2, ISO 27001, etc.) in lieu of on-site audit
- Aggregated security evidence

---

## 11. Liability

Liability for data processing breaches limited per main Terms of Service §11.

---

## 12. Governing Law

Same as main Terms of Service.

---

## Annexes

### Annex I — Processing Details
- Data subjects, categories, purposes (listed above)

### Annex II — Technical and Organizational Measures
1. **Encryption**: TLS 1.3 in transit, AES-256 at rest
2. **Access Control**: RBAC + MFA for staff, JWT for API
3. **Isolation**: PostgreSQL Row-Level Security per tenant
4. **Logging**: Audit logs retained 7 years, immutable
5. **Backup**: PITR with 30-day retention, cross-region DR
6. **Monitoring**: OpenTelemetry, Sentry, 24/7 alerting
7. **Training**: Annual security awareness for all staff
8. **Incident Response**: Documented runbook, 72h breach notification
9. **Physical Security**: AWS data center (SOC 2 Type II, ISO 27001)

### Annex III — Sub-Processors
[Maintained at trust.dealix.sa/subprocessors]
