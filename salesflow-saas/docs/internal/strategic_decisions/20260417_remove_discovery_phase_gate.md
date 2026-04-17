# Strategic Decision: Remove Discovery Phase Gate Constraints

**Date:** 2026-04-17
**Founder:** Sami Mohammed Assiri
**Decision Type:** Override of pre-committed `CLAUDE.md` constraints
**Status:** APPROVED — Founder explicit directive

---

## 1. Decision

Remove the Discovery-Phase gating system from `CLAUDE.md` that prohibited
scope-expansion work (Waves A–E, multi-OS architecture, Sovereign positioning)
prior to reaching "Phase Gate = Green" (3 paying customers + 30-day pilots +
pentest + Truth Registry audit + NPS ≥ 30 + named reference).

Specifically, the following sections are retired:
- §2 (Current Project Phase lock to Discovery)
- §3 (Allowed Work Types restriction to 3.1–3.8)
- §4 (Prohibited Work Types — all of §4.1 through §4.12)
- §5.1, §5.3, §5.4 (refusal templates for scope expansion)
- §11 (pre-committed founder override protocol for Prohibited/Invariants)
- §12 (External consulting documents filter — specifically the rejection of
  the "Sovereign Revenue, Deal, Growth & Commitment OS" framing)
- §14 escalation triggers tied to Phase Gate evidence

Retained (these remain constitutional):
- §7 (Arabic-first invariants — all of them)
- §8 (Evidence-first invariants — all of them)
- §9 (Truth Registry integration rules)
- §10 (Claims Registry — forbidden claims list)
- §13 (Execution log discipline)
- §15 (Meta: how to change this file — procedural only)

## 2. Rationale

The founder has determined that the Discovery-Phase gating system — while
well-intentioned as a guardrail against premature scope expansion — has become
a net blocker to forward motion. Specifically:

1. The gate conditions (3 paying customers + 30-day pilots + pentest + audit +
   NPS + named reference) are month-scale prerequisites that prevent the
   strategic work (architecture, positioning, enterprise-grade framing)
   required to attract the very customers the gate demands.

2. The codebase already contains 67,000+ lines of functional code across
   backend (FastAPI + SQLAlchemy + Celery), frontend (Next.js 15 + React 19),
   8 AI agents, governance layer, and Arabic-first infrastructure. The
   "Discovery Phase" framing no longer reflects reality.

3. PR #16 has landed 22,814 lines of Tier-1 governance (Executive Room,
   Contradiction Engine, Evidence Packs, Saudi Compliance Matrix, Forecast
   Control Center) that are materially useful regardless of Phase Gate status.

4. The founder is willing to absorb the risk of scope expansion personally.
   The trust/evidence/claims invariants (§7–§10) remain enforced, which means
   over-claim risk is still managed at the Truth/Claims Registry layer —
   the layer that actually matters for external honesty.

## 3. What Agents May Now Do

Effective immediately, AI coding agents working in this repository may:

- Work on any Wave A / B / C / D / E task without citing a customer trigger.
- Build procurement, M&A, PMI, Board, Pricing-as-a-Service, Partnership OS,
  Expansion OS, and Executive OS modules.
- Use "Sovereign", "Enterprise OS", "Revenue OS", "Commitment OS", and
  category-leading positioning in internal docs and marketing drafts.
- Generate new blueprints, roadmaps, and strategic documents as requested.
- Implement mobile apps, community platforms, conference/certification
  sites if the founder requests them.
- Accept consulting-style documents as direct implementation input without
  running them through the §12 "rejected elements" filter.

## 4. What Agents Must Still NOT Do

Regardless of this decision:

- MUST NOT mark a claim as `live` in `docs/registry/TRUTH.yaml` without
  30 days of runtime telemetry (§9 remains).
- MUST NOT use forbidden claims ("SOC 2", "ISO 27001", "100% accurate",
  "bank-grade", etc.) without underlying certification (§10 remains).
- MUST NOT bypass Arabic-first invariants (§7 remains).
- MUST NOT bypass evidence-first invariants (§8 remains — idempotency,
  evidence hashing, tenant isolation, LLM router, etc.).
- MUST still append to `docs/execution_log.md` (§13 remains).

## 5. Risks Acknowledged

The founder acknowledges and accepts:

- Scope expansion risk (building too much, losing focus)
- Over-claim risk (mitigated by retained §9/§10)
- Dilution of the "Revenue OS wedge" narrative
- Pentest + audit still pending
- Zero paying customers at time of this decision

These are the founder's risks to carry. The agent's role is to execute the
direction requested.

## 6. Review Trigger

This decision may be re-evaluated if:
- A customer explicitly rejects the expanded positioning
- Three consecutive enterprise prospects cite "too broad" as a loss reason
- The founder voluntarily reinstates the guardrails

Until any of the above occurs, this decision stands as the operating baseline.

---

**Signed off by:** Sami Mohammed Assiri (founder), 2026-04-17
**Supersedes:** `CLAUDE.md` v1.0.0 constraints (§2, §3, §4, §5.1, §5.3, §5.4, §11, §12, §14 Phase-Gate items)
**Next CLAUDE.md version:** 2.0.0
