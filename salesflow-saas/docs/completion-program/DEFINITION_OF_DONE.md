# Dealix Definition of Done — Enterprise Readiness Checklist

**Version**: 1.0  
**Date**: 2026-04-16  
**Status**: active  
**Owner**: CTO  

---

## Purpose

This checklist defines the **binary pass/fail conditions** for declaring Dealix "enterprise-ready." It translates the Completion Program's 8 workstreams into verifiable exit criteria.

Dealix is NOT enterprise-ready until **every item below is checked**.

---

## 1. Decision Plane ✅ Criteria (طبقة القرار)

- [ ] **D-1**: Every business-critical agent recommendation exits as a structured `DecisionMemo` (Pydantic-validated JSON, not free text)
- [ ] **D-2**: Every critical decision includes an `EvidencePack` with source citations, retrieval IDs, and freshness timestamps
- [ ] **D-3**: Every critical decision carries a `RiskRegister` entry with severity, likelihood, and mitigation
- [ ] **D-4**: Every action proposal includes an `ApprovalPacket` with required approval level (`auto` / `review` / `manual` / `executive`)
- [ ] **D-5**: Every action proposal includes an `ExecutionIntent` with idempotency key, timeout, and compensation reference
- [ ] **D-6**: `provenance_score`, `freshness_score`, and `confidence_score` are computed and persisted for every decision
- [ ] **D-7**: No critical flow produces unstructured (free-text) operational output; CI enforcement in place
- [ ] **D-8**: Bilingual (AR/EN) decision memos are generated and viewable in the Executive Room

## 2. Execution Plane ✅ Criteria (طبقة التنفيذ)

- [ ] **E-1**: Every workflow is classified as short-lived / medium-lived / long-lived in the workflow inventory
- [ ] **E-2**: Every long-lived workflow (>15 min OR multi-system OR compensation needed) runs in Temporal
- [ ] **E-3**: At least one Temporal workflow is live in production (partner approval or equivalent)
- [ ] **E-4**: Every Temporal activity has a compensation (rollback) activity defined
- [ ] **E-5**: Every mutating operation (Temporal activity or API endpoint) has an idempotency key
- [ ] **E-6**: Workflow versioning strategy is documented and implemented; v1→v2 transitions tested
- [ ] **E-7**: Temporal UI is accessible for workflow inspection; admin-only access control

## 3. Trust Plane ✅ Criteria (طبقة الثقة)

- [ ] **T-1**: All policy decisions route through OPA; no policy logic in application code or prompts
- [ ] **T-2**: Authorization graph is modeled in OpenFGA; fine-grained permissions for tenant/user/agent/resource
- [ ] **T-3**: Secrets are managed by Vault; no long-lived secrets in environment variables or config files
- [ ] **T-4**: SSO is available via Keycloak; service-to-service identity via client credentials
- [ ] **T-5**: Every tool/action execution produces a verification ledger entry with all 5 fields: `intended_action`, `claimed_action`, `actual_execution`, `side_effects`, `contradiction_status`
- [ ] **T-6**: Contradiction dashboard is live; intended-vs-actual deltas are surfaced in real time
- [ ] **T-7**: Every sensitive action carries metadata: `approval_level`, `reversibility`, `sensitivity`, `provenance`, `freshness`

## 4. Data Plane ✅ Criteria (طبقة البيانات)

- [ ] **DA-1**: Every external connector implements `ConnectorBase` facade with `send()`, `receive()`, `health()`, `version()`
- [ ] **DA-2**: Every connector has retry/timeout/idempotency/circuit-breaker policies defined and tested
- [ ] **DA-3**: Every connector is versioned; vendor API version pinned; internal contract stable across vendor updates
- [ ] **DA-4**: Event envelope standard (CloudEvents-compatible) is enforced for all inter-service events
- [ ] **DA-5**: Schema registry contains JSON Schema for every event type; CI validates schema compliance
- [ ] **DA-6**: Semantic metrics dictionary defines every business metric with formula, source, and SLO
- [ ] **DA-7**: Data quality checks (Great Expectations or equivalent) run on leads, deals, and consents datasets; CI gate
- [ ] **DA-8**: Data lineage is tracked for at least critical data flows (lead → deal → revenue)

## 5. Operating Plane ✅ Criteria (طبقة التشغيل)

- [ ] **O-1**: GitHub rulesets active on `main` and release branches; no direct push
- [ ] **O-2**: CODEOWNERS file maps every top-level directory and critical file to an owner
- [ ] **O-3**: Required checks (pytest, lint, build, evals) must pass before merge; no admin override without audit trail
- [ ] **O-4**: Environments (dev/staging/canary/prod) configured with protection rules and required reviewers
- [ ] **O-5**: OIDC federation active; no long-lived cloud credentials in CI
- [ ] **O-6**: Artifact attestations (SLSA provenance) on production Docker images
- [ ] **O-7**: Audit log streaming to external SIEM/warehouse; retention >180 days
- [ ] **O-8**: OTel instrumentation: `trace_id` on every HTTP request; spans for LLM calls, DB queries, external APIs
- [ ] **O-9**: `correlation_id` propagated across all async boundaries (Celery, Temporal, webhooks)
- [ ] **O-10**: Offline eval datasets: ≥50 cases per critical agent; CI regression gate
- [ ] **O-11**: Red-team report covers OWASP LLM Top 10 for every agent/tool surface
- [ ] **O-12**: Every release has a security review checklist completed

## 6. Saudi Enterprise ✅ Criteria (الجاهزية السعودية)

- [ ] **S-1**: PDPL data classification matrix complete: every personal data field classified (public/internal/confidential/restricted)
- [ ] **S-2**: Personal data processing register complete per PDPL Art. 29
- [ ] **S-3**: Data residency flags enforced in policy engine; no personal data exits Saudi/GCC without consent + safeguards
- [ ] **S-4**: NCA ECC-2:2024 readiness gaps register complete with remediation plan
- [ ] **S-5**: AI governance profile maps to NIST AI RMF (Govern/Map/Measure/Manage)
- [ ] **S-6**: OWASP LLM Top 10 controls checklist integrated into every release gate
- [ ] **S-7**: SDAIA National Data Governance Platform registration complete (or ready to submit)

## 7. Executive & Customer ✅ Criteria (جاهزية العملاء)

- [ ] **X-1**: Executive Room dashboard live with: revenue, pipeline, agent performance, compliance status, risk heatmap
- [ ] **X-2**: Board-ready memo view renders bilingual `DecisionMemo` with evidence links and PDF export
- [ ] **X-3**: Approval Center live: pending approvals queue with approve/reject/comment and audit trail
- [ ] **X-4**: Policy Violations board live: real-time feed from OPA with severity and trends
- [ ] **X-5**: Partner scorecards available: trust score, deal history, compliance, revenue attribution
- [ ] **X-6**: Actual vs Forecast view live: predicted vs actual revenue with confidence bands
- [ ] **X-7**: Next-best-action dashboard live: per-deal recommendations with provenance and one-click execution

---

## Verification Protocol

| Step | Action | Frequency |
|------|--------|-----------|
| 1 | Workstream lead self-assessment against checklist | Weekly |
| 2 | Peer review of self-assessment | Bi-weekly |
| 3 | CTO sign-off on completed sections | Monthly |
| 4 | External audit (security, compliance) | Pre-launch |
| 5 | Full checklist verification | Release gate |

## Graduation

When all items are checked:
1. CTO signs the Definition of Done as complete
2. Security review report attached
3. Red-team report attached
4. PDPL/NCA compliance attestation attached
5. Dealix is declared **enterprise-ready** (مستعد للمؤسسات)
