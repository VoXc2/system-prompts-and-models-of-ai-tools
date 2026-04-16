# OWASP LLM Top 10 — Release Gate Checklist

> **Version:** 1.0 — 2026-04-16
> **Authority:** AI Lead — must be signed before every production release.
> **Blocking:** Any HIGH or CRITICAL item left unchecked **blocks the release.**
> **Reference:** OWASP LLM Top 10 (2025 edition) + Dealix-specific controls.

---

## Instructions

Complete this checklist for every production release. Sign with your GitHub handle and the release tag.

```
Release Tag: _______________
Release Date: _______________
AI Lead Signature (GitHub handle): _______________
Security Lead Sign-off: _______________
```

---

## Checklist

### LLM01 — Prompt Injection · CRITICAL · Release Blocker

- [ ] Red-team test run: indirect prompt injection via user-controlled fields (deal name, contact notes, KB content)
- [ ] Verified: agent does not execute injected instructions
- [ ] Input sanitisation applied to all user-facing fields before injection into prompt
- [ ] System prompt integrity check in place (system prompt not overridable by user)

**Evidence:** Attach red-team test report or link to CI artifact.

---

### LLM02 — Insecure Output Handling · HIGH · Release Blocker

- [ ] All Executor-class agent outputs validated against `execution_intent.schema.json` before any system action
- [ ] All Recommender outputs validated against `memo.schema.json`
- [ ] No free-text output from critical agents reaches external systems (CRM, DocuSign, WhatsApp)
- [ ] Schema validation failure triggers alert, not silent pass

**Evidence:** CI schema validation job — green.

---

### LLM03 — Training Data Poisoning · HIGH · Release Blocker

- [ ] No new KB content added from user-controlled sources without human review gate
- [ ] KB ingestion pipeline includes content review step
- [ ] Adversarial content injection scenario tested (injected malicious KB chunk; agent behaviour verified)

**Evidence:** KB ingestion pipeline PR review + test result.

---

### LLM04 — Model Denial of Service · MEDIUM · Release Warning

- [ ] Load test: 500 concurrent agent requests — p95 latency within SLA (< 5 s)
- [ ] No OOM crash under load
- [ ] Rate limiting enforced per tenant (Redis counter / OPA quota policy)
- [ ] Circuit breaker in place for OpenAI API calls

**Evidence:** Load test report (link or attach).

---

### LLM05 — Supply Chain Vulnerabilities · HIGH · Release Blocker

- [ ] `trivy image` scan: zero CRITICAL CVEs in production Docker image
- [ ] Dependabot alerts: zero CRITICAL unpatched
- [ ] OpenAI SDK, LangGraph, Temporal Python SDK — pinned versions verified
- [ ] `pip-audit` clean

**Evidence:** CI Trivy report — green. Dependabot status — clean.

---

### LLM06 — Sensitive Information Disclosure · CRITICAL · Release Blocker

- [ ] Automated scan: no Saudi National ID (هوية) pattern in prompts or logs
- [ ] Automated scan: no raw phone numbers in prompts (except sanitised/masked form)
- [ ] Automated scan: no email addresses in agent system prompts
- [ ] pgvector embeddings: verified no raw personal data in embedded text without consent
- [ ] LLM API logs: verified not being sent to vendor without DPA

**Evidence:** Regex scan CI job output.

---

### LLM07 — Insecure Plugin Design · HIGH · Release Blocker

- [ ] `rg 'requests\.get|httpx\.get|urllib'` in agent code returns zero direct HTTP calls (all must go through `BaseConnector`)
- [ ] All tool calls include OPA policy check before execution
- [ ] Tool call results validated against expected schema before agent processes response
- [ ] No tool can exceed its declared permission scope (verified via OpenFGA assertions)

**Evidence:** `rg` output screenshot / CI log.

---

### LLM08 — Excessive Agency · CRITICAL · Release Blocker

- [ ] OPA test: `agent_sensitivity.rego` — high-sensitivity action without `approval_packet` returns deny
- [ ] OPA test: `agent_sensitivity.rego` — critical action without dual approval returns deny
- [ ] HITL interrupt present in LangGraph graph for all Executor paths with sensitivity ∈ {high, critical}
- [ ] No new Executor agent added without entry in `agent-role-registry.md`

**Evidence:** OPA test suite — green (`opa test policies/`).

---

### LLM09 — Overreliance · HIGH · Release Blocker

- [ ] Confidence score displayed on all recommendations in executive UI
- [ ] Low-confidence threshold (< 0.6) triggers additional human review prompt
- [ ] Provenance score displayed; low-provenance warning shown to user
- [ ] HITL gate cannot be bypassed for irreversible actions

**Evidence:** Executive Room UI screenshot showing scores.

---

### LLM10 — Model Theft · MEDIUM · Release Warning

- [ ] All LLM API endpoints require Keycloak token (no unauthenticated access)
- [ ] Rate limiting on LLM proxy endpoints (per tenant, per user)
- [ ] No system prompt exposed in API response
- [ ] LLM API key stored in Vault (not in `.env`)

**Evidence:** `curl` test — unauthenticated request returns 401.

---

## Sign-off

```
AI Lead: _______________  Date: _______________
Security Lead: _______________  Date: _______________
Release approved: YES / NO
Blocker items (if any): _______________
```
