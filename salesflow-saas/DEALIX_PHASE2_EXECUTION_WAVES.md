# DEALIX — Phase 2 Execution Waves (90-Day Plan)

> **Core rule**: From self-reported completion to externally-validated reality.
> **Success metric**: 3 paying pilot customers + externally-validated security posture within 90 days.
> **Next action for coding agent**: Execute ONLY Verification Protocol (V001–V007). Do NOT start Wave A tasks until Week-12 Phase Gate returns Green.

---

## Executive Summary

Phase 1 foundation exists. Phase 2 foundation scaffolded. **This document governs the next 90 days** — specifically resisting "Plan Completion Syndrome" (generating plans faster than executing them).

**Rule**: No new features ship until:
1. Verification Protocol (§1) completes with external validation
2. Founder Decision Sprint (§2) closes (4 founder decisions)
3. Customer Validation (§3) returns ≥ 3 paying pilots

**Agent execution scope this phase**: V-tasks + scaffolding for FD and CV tracks. That's it.

---

## §1 — Verification Protocol (Weeks 1-2, before ANY new feature work)

Convert self-reported completion into externally-validated reality.

### V001 — Full git history secret scan
- **Beyond HEAD**: scan all 146+ commits with trufflehog + gitleaks
- **Two-tool rule**: defense in depth
- **Output**: `docs/internal/secret_audit_log.md` with every finding documented

### V002 — Runtime RLS fuzz test
- 10,000 cross-tenant queries as Tenant A switching to Tenant B
- Expected: zero rows returned from Tenant B's context
- Added to nightly CI
- Any violation = P0 incident

### V003 — External pentest
- Engage Cure53, Trail of Bits, NCC Group, or Securinc
- Scope: auth, RLS enforcement, ABAC, LLM injection, file uploads, webhooks
- Budget: $20K-40K
- **Cannot claim "pentested" until report exists**

### V004 — No-founder customer demo test
- 3 fresh testers complete golden path unassisted
- Founder watches silently
- Acceptance: 2/3 complete in <30 min with no show-stopper

### V005 — Truth Registry independent audit
- Engineer who did NOT write registry audits every claim
- Verdicts: SUPPORTED / UNSUPPORTED / AMBIGUOUS
- Any UNSUPPORTED → evidence added or demoted to roadmap within 48h

### V006 — Performance baseline
- k6 load test against staging with production-like data
- Output: `docs/baselines/perf_YYYYMMDD.json`
- Every future perf claim references this baseline

### V007 — Accessibility baseline
- Playwright + axe full scan
- Output: `docs/baselines/a11y_YYYYMMDD.json`
- Every future a11y claim references this baseline

---

## §2 — Founder Decision Sprint (Weeks 1-2, parallel)

**Agent cannot execute these.** Founder-only.

### FD001 — Legal entity decision
- MISA KSA LLC (recommended default for Saudi-primary positioning)
- OR DIFC/ADGM (UAE)
- OR Delaware C-Corp + KSA subsidiary (if raising US VC)
- Output: `docs/internal/legal_entity_decision.md`
- **Deadline: Week 2**

### FD002 — Counsel engaged
- Al Tamimi / Clyde & Co / local boutique
- Budget: 30-80K SAR initial engagement
- **Deadline: Week 2**

### FD003 — Repository extraction completed
- GitHub org created
- Phase 1 TASK-001 script executed
- Old fork archived/privatized
- **Deadline: Week 1**

### FD004 — SAIP trademark filed
- Classes: 9, 35, 42 (+ 41 if community)
- Marks: Dealix (Latin) + ديلكس (Arabic)
- Via counsel
- **Deadline: Week 3**

### FD005 — First hires initiated
- Founding Design Engineer (#1) — 30-45K SAR/month + 0.5-2% equity
- Founding Backend Engineer (#2) — 25-40K SAR/month
- Head of Customer Success (#3) — 35-55K SAR/month
- **Deadline: Week 4 (60-90 day lead time)**

---

## §3 — Customer Validation Program (Weeks 3-12)

**Hard rule**: no Phase 2 feature ships until pilot customers drive the backlog.

### ICP Filter
- Saudi-based HQ or KSA ops
- 200-2,000 employees
- Pain in commercial operations
- CFO/COO/GM personal sponsor
- Bilingual operations

### Pilot Structure
- 90 days
- 50% of Business tier ($1,500 total upfront)
- Defined success criteria before signing
- Weekly 30-min feedback session
- Permission for case study if successful

### First 3 (design partners)
- 6-month credit in exchange for:
  - Public testimonial + logo
  - Recorded case study
  - Speaking slot at first event

### Week-12 Phase Gate

| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| Customers with signed success | 3+ | 1-2 | 0 |
| Golden path completion rate | >90% | 70-90% | <70% |
| NPS | >30 | 0-30 | <0 |
| References willing | 3+ | 1-2 | 0 |
| Renewal intent | 3+ verbal | 1-2 | 0 |

- All Green: proceed to Wave A
- Mostly Yellow: extend pilot 60 days
- Any Red: HALT Phase 2 execution

---

## §4 — Phase 2 Execution Waves

**Waves, not streams**: each has a customer-impact gate.

### Wave A — Frontend Signature (Weeks 4-20)
- F201 (DS foundation) → F270 (Approval Card pattern)
- Exit: Lighthouse ≥95 on 5 routes + zero axe violations + 2+ pilots spontaneously compliment UI

### Wave B — Enterprise Unlock (Weeks 8-28, parallel)
- E510 (SSO/SCIM via WorkOS) → E550 (SLA tiers)
- Exit: First Business tier deal with SSO + audit export validated + <3 day security questionnaire turnaround

### Wave C — AI Depth (Weeks 16-36)
- AI410 (orchestrator) + AI440 (RAG) + AI460 (eval v2)
- Exit: +20pp Arabic performance vs baseline + first Dealix Labs benchmark paper

### Wave D — Ecosystem (Weeks 24-44)
- I610 (public API) + I620 (ZATCA) + I621 (2 MENA connectors)
- Exit: 3 integrations live + public API docs + 1 partner integration certified

### Wave E — Regional (Weeks 32-52)
- R1110 (UAE localization) + GITEX presence + trust portal public
- Exit: 1 UAE customer + 1 Egypt pilot + trust portal 30+ days uptime

---

## §5 — Operating System

### Weekly Rhythm
| Day | Block |
|-----|-------|
| Mon AM | Metrics review |
| Mon PM | Customer pipeline |
| Tue | Product standup |
| Wed | Customer learnings synthesis |
| Thu | Release window |
| Fri AM | Security review |
| Fri PM | Retrospective |

**Rule**: No deploys Friday after 14:00 AST. Ever.

### Decision Framework
1. Reversibility test (reversible → fast; irreversible → founder call)
2. Signature alignment (Arabic-first, evidence-backed, decision-grade)
3. Cost of delay
4. Customer test (would pilot customer ask for this?)
5. Moat compounding

---

## §6 — Failure Modes to Actively Resist

| Failure | Defense |
|---------|---------|
| Plan Completion Syndrome | Monthly planning/shipping ratio check; if planning >30%, stop |
| Premature Scaling | Hire-gate tied to MRR milestones |
| Customer Proxy Syndrome | 10 customer hours/week minimum for founder |
| Integration Sprawl | Only build integrations appearing in ≥3 pilot conversations |
| Security Theater | Auditor report or not-claimed |
| Arabic-First Erosion | Any English-only feature blocked at review |
| Founder Bottleneck | Authority matrix published by Month 6 |

---

## §7 — Day 90 Success Criteria (from Appendix A)

- [ ] 3 signed pilot customers (paid), 2 in active use
- [ ] Pentest report received; no open Critical, ≤2 open High
- [ ] Full history secret audit: 0 verified findings
- [ ] Truth Registry: 100% SUPPORTED claims
- [ ] First 3 hires: offers extended/accepted
- [ ] Repository extraction: done, old fork private
- [ ] Trademark: filed
- [ ] Legal entity: incorporated or restructuring with ETA
- [ ] Wave A: 40% progressed with measurable milestones
- [ ] NPS measured
- [ ] ≥1 customer reference willing to take a call
- [ ] Dealix Labs: 1 published research piece

**≥10/12 = category-defining trajectory. 6-9 = correctable. ≤5 = fundamental rethink.**

---

## §8 — What Dealix is NOT Doing in These 90 Days

Every "no" enables a sharper yes:

- ❌ New features off Wave A critical path
- ❌ Integrations no customer asked for
- ❌ Public marketing campaigns
- ❌ PR pushes
- ❌ Investor fundraising (unless already in progress)
- ❌ Mobile apps
- ❌ Workflow builder
- ❌ Voice interface
- ❌ Community platform
- ❌ Certification program
- ❌ Partner program
- ❌ "Thought leadership" beyond manifesto

---

## Coding Agent Instructions

1. **Execute Verification Protocol tasks (V001-V007)** — honest reporting, including unsupported claims
2. **Prepare scaffolding for FD tasks** — job specs, counsel research, trademark prep — but DO NOT execute founder-only decisions
3. **DO NOT start any Wave task until Week-12 Phase Gate returns Green**
4. If gate returns Yellow/Red → escalate to founder. Do not default to "ship more features"
5. Weekly `docs/execution_log.md` entry with facts, not celebrations

---

## Honest Note

1. Foundation is strong. More built in 2 weeks than most build in 6 months.
2. The next 90 days are about **proving**, not building.
3. **Highest-leverage action: close 3 pilot customers.** Everything else is downstream.
