# Dealix — Pilot Agreement Template

> **NOTICE**: Draft. Not a legal document. Must be reviewed and adapted by counsel (FD002) before execution.

---

## Parties

- **Provider**: Dealix (exact entity name per FD001 decision) ("Dealix")
- **Customer**: [Company legal name] ("Customer")

## Effective Date

[YYYY-MM-DD]

## Pilot Term

90 days from the Effective Date. May be extended by mutual written agreement.

---

## 1. Scope

Dealix will provide Customer with access to the Dealix Enterprise Growth OS, including:
- Core platform (Deals, Approvals, Evidence, Executive Room)
- Saudi Compliance module (PDPL consent tracking, ZATCA invoicing, optional SDAIA/NCA reporting)
- Up to [N] named users
- Standard onboarding and weekly 30-minute feedback session

**Excluded** from pilot scope: custom development, dedicated infrastructure, on-premises deployment, custom SLAs above standard.

## 2. Commercial Terms

### Design-partner pilots (first 3 customers)
- Fee: **zero** during Pilot Term in exchange for obligations in §6.
- Credit: **6 months** free on post-pilot Business tier if renewal executed.

### Paid pilots (customers 4+)
- Fee: **1,500 USD** payable upfront (= 50% of Business tier 3-month value).
- Credit: Pilot fee fully applied to year-1 subscription if renewed within 30 days of pilot end.

## 3. Success Criteria

Per pilot, Dealix and Customer will sign a Success Criteria document (see `pilot_template/success_criteria.md`) **before Kickoff**. Default criteria:
- 90%+ Golden Path completion rate across Customer's first 10 partner/deal flows
- At least 3 Customer-approved Evidence Packs generated
- At least 1 Executive Weekly Pack delivered and acted upon
- NPS ≥30 at Pilot end
- No P0 incidents attributable to Dealix

## 4. Data

- Data residency: me-south-1 (AWS Bahrain) by default. KSA region available on request.
- All Customer data remains Customer-owned.
- Dealix may use aggregated, de-identified telemetry to improve the platform.
- Dealix will NOT use Customer data to train external LLMs.
- DPA (Data Processing Agreement) signed alongside this pilot — see `docs/legal/templates/DPA_EN.md`.

## 5. Privacy & Compliance (KSA-specific)

- Dealix processes Personal Data in accordance with the PDPL.
- Customer is the Data Controller; Dealix is the Data Processor.
- Dealix maintains appropriate safeguards (PostgreSQL RLS, encryption at rest + transit, audit logging).
- Sub-processor list disclosed at `docs/trust/subprocessors.md` (TBD — Wave E).

## 6. Customer Obligations (design-partner pilots only)

In exchange for fee-free pilot, Customer agrees to:
1. Designate a named executive sponsor (CFO/COO/GM).
2. Attend weekly 30-minute feedback session for 90 days.
3. Permit Dealix to record sessions for internal research.
4. Upon successful pilot, permit Dealix to:
   - Publish Customer's name and logo as a reference.
   - Record a ≤30-minute case study interview.
   - Invite Customer to speak at first Dealix community event.
5. Provide timely feedback on friction, bugs, and requested features.

## 7. Support & SLA

- Business-hours support (Sunday–Thursday 09:00–17:00 AST).
- Best-effort response target: 4 hours for P1, 1 business day for P2.
- Pilots do NOT include 24/7 or weekend pager rotation.

## 8. Intellectual Property

- Dealix retains all IP in the platform.
- Customer retains all IP in Customer's data and business processes.
- Any jointly developed configuration becomes jointly owned; subject to standard non-exclusive license to each party.

## 9. Confidentiality

Each party shall protect the other's Confidential Information with the same care as its own, and for no less than 3 years after Pilot end.

## 10. Termination

- Either party may terminate with 30 days' written notice.
- Customer data export available for 60 days post-termination in JSON + CSV formats.
- Design-partner credits forfeited if Customer terminates without cause within first 60 days.

## 11. Limitation of Liability

Pilot is provided "as is." Dealix's total liability is capped at the Pilot Fee (or 1,500 USD where no fee paid). Neither party liable for indirect, incidental, or consequential damages.

## 12. Governing Law

[Per FD001 selection: KSA law if MISA LLC; DIFC law if DIFC; Delaware law if C-Corp]

## 13. Dispute Resolution

Good-faith negotiation for 30 days. Then binding arbitration in [per FD001].

---

## Signatures

**Dealix**
Name: ________________ Title: ________________ Date: ________________ Signature: ________________

**Customer**
Name: ________________ Title: ________________ Date: ________________ Signature: ________________
