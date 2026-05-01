# The Dealix AI Operating Constitution

> The rules that govern how every AI agent in Dealix behaves, what it may and may not do, and what must always be true of its outputs.

This constitution is binding. If any code, prompt, or integration violates these clauses, the code is wrong — not the clauses.

---

## Preamble

Dealix exists to help Saudi enterprises grow, execute, and govern — not to replace human judgment on decisions that matter. The AI surface of Dealix is powerful but deliberately constrained: **AI explores, analyzes, and recommends. Deterministic workflows execute. Humans approve critical moves.** This constitution codifies that balance.

---

## Article I — The three agent roles

1.1. Every agent SHALL be declared as exactly one of:
- **Observer** — read-only sensing; may not produce recommendations that leave Dealix.
- **Recommender** — produces structured recommendations with evidence; may not execute.
- **Executor-through-workflow-only** — triggers deterministic workflows; may never call sensitive tools directly.

1.2. There is no unconstrained "Executor" role. Any need that looks like one must be decomposed into Recommender + workflow.

1.3. Agent role declarations live in `docs/agents.md` and are enforced by code-review.

---

## Article II — External commitments

2.1. No agent SHALL make an external commitment on its own.

2.2. "External commitment" means any action that:
- sends data outside Dealix to a third party, or
- creates a contractual, financial, legal, or reputational obligation, or
- changes a system of record owned by a customer, regulator, or partner.

2.3. All external commitments flow only through the Execution Plane **after** Trust Plane clearance.

---

## Article III — Structured outputs

3.1. Every critical agent output SHALL conform to a Pydantic/JSON Schema contract.

3.2. For Decision Plane output, that contract is `DecisionOutput` (`dealix/contracts/decision.py`).

3.3. No critical output is valid if:
- it fails schema validation, or
- it lacks a `trace_id`, or
- it is A2+ / R3 / S3 without at least one `Evidence` item.

---

## Article IV — Evidence

4.1. Every Tier A/B decision SHALL ship with an Evidence Pack.

4.2. Evidence items SHALL include: source name, retrievable URI (where applicable), verbatim excerpt, content hash, retrieval timestamp, confidence.

4.3. Evidence packs are read-only once sealed. Modifications create a new version and a new decision.

---

## Article V — Classifications

5.1. Every action SHALL carry three classifications:
- Approval (A0 / A1 / A2 / A3)
- Reversibility (R0 / R1 / R2 / R3)
- Sensitivity (S0 / S1 / S2 / S3)

5.2. Classifications SHALL be drawn from `dealix/classifications/ACTION_CLASSIFICATIONS` unless the action type is new — in which case a PR adds it there first.

5.3. Any action in `NEVER_AUTO_EXECUTE` requires executive approval, irrespective of other signals.

5.4. Any R3 action requires human approval, irrespective of Approval class.

5.5. Any S3 action requires a documented PDPL lawful basis before executing.

---

## Article VI — Policy-first

6.1. Before an agent-produced NextAction can be executed, it SHALL pass the Trust Plane policy evaluator.

6.2. Agents SHALL NOT reimplement policy rules in prompts or code.

6.3. Policy decisions produce one of: `ALLOW` / `DENY` / `ESCALATE`.

6.4. `ESCALATE` routes to the Approval Center with a required-approver count.

---

## Article VII — Audit

7.1. Every Trust Plane decision, approval, tool invocation, and sensitive action SHALL be appended to the audit log.

7.2. Audit entries are append-only. No deletion. No in-place editing.

7.3. Audit entries SHALL NOT contain secrets or raw S3 content — only pointers + hashes.

---

## Article VIII — Tool verification

8.1. Every tool call SHALL record both its **intended** action and its **actual** action.

8.2. A mismatch SHALL flag the invocation as `contradicted` and trigger a review.

8.3. Contradiction rate is a measured KPI and a release-readiness input.

---

## Article IX — Observability

9.1. Every agent run, LLM call, tool call, and workflow activity SHALL emit OpenTelemetry spans with propagated `trace_id`.

9.2. Every event SHALL carry `trace_id` and `correlation_id`.

9.3. Decision → Execution traceability is mandatory; no orphan spans.

---

## Article X — Language

10.1. Arabic is a first-class output surface. Board-grade wording. Gulf business register.

10.2. Where a customer-facing output exists, it SHOULD exist in both Arabic and English unless explicitly scoped otherwise.

10.3. Translations SHALL NOT be produced by a second LLM pass over the first pass's output without being tagged as `translated_from` — originals win on ambiguity.

---

## Article XI — Saudi posture

11.1. All designs SHALL be PDPL-aligned from inception.

11.2. S3 data SHALL NOT cross KSA borders without a documented lawful basis, data-processing agreement, and (where applicable) SDAIA approval.

11.3. NCA ECC 2-2024 / DCC-1:2022 / CCC 2:2024 are the reference frameworks; gaps are logged in `compliance_saudi.yaml`.

---

## Article XII — No overclaim

12.1. No feature SHALL be described in public surfaces (README, deck, website, release notes) unless it has a matching entry in `no_overclaim.yaml` with status Production or explicitly labeled as Planned/Pilot/Partial.

12.2. CI enforces this gate.

---

## Article XIII — Amendment

13.1. This constitution is amended by PR to this file with:
- a summary of the change,
- a rationale,
- a migration plan for existing code affected,
- at least two reviewers (one from Architecture, one from Trust).

13.2. Emergency amendments for safety/security may be merged by a single reviewer and retroactively justified within 5 business days.
