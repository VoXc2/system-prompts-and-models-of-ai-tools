# DEALIX — Phase 2 Category Leadership Blueprint

> **Prerequisite**: Phase 1 (`DEALIX_EXECUTION_BLUEPRINT.md`) complete.
> **Time horizon**: 6-18 months.
> **Status**: Execution roadmap. Parallelizable streams.

---

## Strategic Reframe

After Phase 1, Dealix is operationally excellent. Phase 2 makes it **category-defining**.

### The Dealix Signature (every decision must pass)
1. Does this make Arabic-first enterprise ops noticeably better than English-first tools retrofitted?
2. Does this make decisions more evidence-backed than competitors?
3. Does this make the operator's next action clearer than anywhere else?

If no → don't ship.

---

## 10 Parallel Streams

| Stream | Scope | TASK prefix |
|--------|-------|-------------|
| 1 — Frontend Excellence | Design system, Arabic/RTL, a11y, motion, viz | F2xx |
| 2 — Product Depth | 5 workflows, builder, templates, analytics | P3xx |
| 3 — AI Intelligence | Multi-agent, Arabic NLP, KG, RAG, voice, evals | AI4xx |
| 4 — Enterprise | SSO/SCIM, ABAC, audit, residency, SLAs | E5xx |
| 5 — Integrations | API, SDK, MENA connectors (Qoyod, Zid, Salla) | I6xx |
| 6 — Scale | Multi-region, edge, DB scale, chaos | S7xx |
| 7 — Commercial | Self-serve, billing, partners, referrals | C8xx |
| 8 — Customer Platform | Docs, community, certification, conference | CP9xx |
| 9 — Trust | ISO 27001/17/18, pentest, bug bounty, trust portal | T10xx |
| 10 — Category POV | Manifesto, Dealix Labs, content, OSS | CAT13xx |

---

## Executable Now (no external services required)

| Task | Status | Notes |
|------|--------|-------|
| TASK-F201 | SCAFFOLDED | `packages/design-system/tokens/` created |
| TASK-F212 | SCAFFOLDED | `packages/arabic-ui/` Arabic utilities |
| TASK-CAT1310 | SCAFFOLDED | `marketing/manifesto.md` bilingual draft |
| TASK-CAT1320 | SCAFFOLDED | `docs/labs/` Dealix Labs structure |

## Requires External Services

| Task | Blocker |
|------|---------|
| TASK-E510 (SSO/SCIM) | WorkOS account + IdP integration testing |
| TASK-T1010 (ISO 27001) | Accredited cert body + 12-18 months |
| TASK-T1020 (bug bounty) | HackerOne/Intigriti account |
| TASK-CP910 (docs) | Mintlify account |
| TASK-CP930 (community) | Discourse hosting or Slack Connect |
| TASK-CP940 (certification) | Teachable/LearnWorlds account |
| TASK-CP950 (conference) | Event venue booking |
| TASK-AI450 (voice) | ElevenLabs account + customer demand |
| TASK-S710 (multi-region) | AWS account + production customers |
| TASK-R1110 (localization) | Market validation per country |

## Requires Product-Market Fit Signal

These shouldn't start until paying customers exist:
- Workflow Builder (P320)
- Partner Program (C840)
- Referral Engine (C850)
- Multi-agent orchestrator (AI410) — has small version now, full scale later
- Voice interface (AI450)

---

## Phase 2 Completion Criteria (18 months)

| Signal | Threshold |
|--------|-----------|
| Organic inbound (Arabic enterprise AI keywords) | Top 3 for 20+ commercial keywords |
| Named customer references | ≥ 15 across ≥ 3 countries |
| Open-source contributions | ≥ 6 accepted upstream PRs |
| Whitepapers cited externally | ≥ 2 |
| Conference keynotes | ≥ 6 regional + ≥ 2 international |
| NPS | ≥ 50 |
| NRR | ≥ 120% |

---

## Phase 2 Execution Order Recommendation

### Month 1-3 (immediate)
- TASK-F201: Design system foundation (blocks most frontend)
- TASK-F210: Arabic typography
- TASK-F211: RTL-aware layout
- TASK-AI460: Eval harness v2
- TASK-CAT1310: Publish manifesto

### Month 3-6 (after first paying customers)
- TASK-F220/230/240: Performance + a11y + motion
- TASK-E510: SSO/SCIM (enables enterprise deals)
- TASK-E520: OpenFGA ABAC
- TASK-I620: ZATCA integration (if KSA customers)
- TASK-P310: Second golden path

### Month 6-12
- TASK-E530: Audit platform
- TASK-E540: Data residency options
- TASK-I621: MENA connectors (on demand)
- TASK-T1010: ISO 27001 start
- TASK-CP910: Docs portal launch

### Month 12-18
- TASK-F290: Executive iOS app
- TASK-S710: Multi-region
- TASK-T1020: Bug bounty program
- TASK-CP950: First Dealix Majlis conference
- TASK-CAT1340: Open-source @dealix/arabic-ui

---

## Signature Components — Phase 2 Anchors

### 1. ApprovalCard (from Phase 2 §1.8)
The one component that shows the Dealix signature:
- Narrative brief authored by LLM at generation time
- Evidence count + model inference count + policy check status
- Economics summary with forecast impact
- Risk flags with color + reason
- Keyboard shortcuts: ⌘1 approve, ⌘2 request more, ⌘3 reject, ⌘E open evidence

### 2. Executive Room Weekly Pack
Already live in Phase 1 at `/api/v1/executive-room/weekly-pack`. Phase 2 adds:
- Narrative header (ExecBriefAgent-generated)
- Interactive drill-down to source evidence
- Dual Gregorian/Hijri dates
- Board-ready PDF export with embedded Arabic fonts

### 3. Evidence Timeline
The story of a decision rendered as a readable timeline:
- Who proposed → data sources consulted → model reasoning → approvals collected → final commitment
- Every node clickable → full provenance
- Scrubbable timeline for long workflows

---

## Non-Negotiable Phase 2 Invariants

Extended from Phase 1:
1. Performance budget enforced in CI (LCP <1.5s, INP <150ms, CLS <0.05)
2. Accessibility: 0 axe violations; WCAG 2.2 AA minimum, AAA for approval surfaces
3. Arabic parity: every new feature ships with Arabic UI + Arabic docs
4. Zero claims beyond `claims_registry.yaml`
5. Every LLM call goes through `dealix.ai.router` (no direct provider imports)
6. Every side-effect has idempotency key
7. Every external commitment has approval + evidence + correlation
