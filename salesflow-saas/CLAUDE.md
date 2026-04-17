# CLAUDE.md — Dealix Repository Instructions for Coding Agents

> **This file is the source of truth for how Claude Code, Cursor, Codex, or any coding agent must behave when working in the Dealix repository.**
> Read it fully at the start of every session.
> Place this file at the repository root as `CLAUDE.md`. Also copy to `.cursorrules` for Cursor compatibility.

**Version:** 2.0.0
**Effective:** 2026-04-17
**Supersedes:** v1.0.0 (Discovery-Phase gating removed per `docs/internal/strategic_decisions/20260417_remove_discovery_phase_gate.md`)

---

## 1. WHO THIS FILE IS FOR

Any AI coding agent (Claude Code, Cursor, Codex, Windsurf, Qoder, GitHub Copilot, Warp, Comet, etc.) working in the Dealix codebase.

This file is the agent's operating manual. Humans may read it for awareness.

---

## 2. PROJECT IDENTITY

- **Name:** Dealix (ديلكس)
- **Type:** Enterprise Revenue, Deal, Partnership, Expansion & Commitment Operating System
- **Market:** Saudi Arabia & wider GCC, enterprise and mid-market
- **Stack:** FastAPI 0.115 (Python 3.12) + Next.js 15 + PostgreSQL 16 + Redis 7 + Celery 5
- **Frontend language:** Arabic-first, bilingual (AR/EN), RTL layout
- **AI layer:** Groq (primary) → OpenAI (fallback), routed via `services/model_router.py`
- **Agent system:** 8+ task-specific agents (Orchestrator, Researcher, Qualifier, Outreach, Closer, Compliance, Analytics, WhatsApp)
- **Positioning:** Policy-bound autonomous execution under human-in-the-loop approval, not fully autonomous

The founder owns scope decisions. Agents execute, they do not arbitrate strategy.

---

## 3. HOW TO WORK EFFICIENTLY (token/cost discipline)

See `salesflow-saas/docs/TOKEN_EFFICIENCY_RULES.md` for the full playbook. Summary:

1. **Use CLI over MCP.** `gh`, `git`, and direct shell are cheaper than connector MCPs.
2. **Grep before Read.** Don't read entire files if you need a section.
3. **Use `--depth 1`, `--jq`, `| head`, `| tail`.** Filter output before it reaches context.
4. **Edit, don't rewrite.** Use `old_string/new_string` patches on existing files.
5. **One task = one session.** Clear context between unrelated tasks.
6. **Match model to task.** Use Flash / mini for imports, formatting, simple bugs. Save Opus / GPT-5 for architecture.
7. **Test locally before push.** Failing CI = wasted tokens on re-analysis.

---

## 4. ARABIC-FIRST INVARIANTS (ENFORCED)

Any UI-facing change must pass these checks:

- No `left`/`right` CSS properties — use logical properties (`inline-start`, `inline-end`).
- All user-facing strings have Arabic parity, OR a justified English-only exception in `docs/internal/english_only_exceptions.md`.
- Date code supports Gregorian + Hijri where executive-facing.
- Numeral formatting respects user preference (Western vs Arabic-Indic).
- Phone inputs default to `+966` with country selector.
- Currency defaults to SAR in KSA contexts, not USD.
- Name fields support first + father's + grandfather's + family structure.
- BiDi isolation for mixed-direction content (Arabic + English + numerals).
- Form field order validated for RTL contexts.
- Icon mirroring rules applied per `mirror-rules.ts`.

If a change violates any invariant without documented exception, abort the change.

---

## 5. EVIDENCE-FIRST INVARIANTS (ENFORCED)

- Every side-effectful action goes through the idempotency wrapper (`dealix/idempotency.py`).
- Every approval generates an immutable evidence artifact with hash chain.
- Every LLM call goes through `dealix/ai/router.py` — no direct provider imports.
- Every tenant-scoped query runs in a context with `app.tenant_id` set.
- Every audit-logged action is hash-chained.
- Every LLM prompt change passes eval regression (≥ 95% pass, ≤ 30% latency regression, ≤ 20% cost regression).

---

## 6. TRUTH REGISTRY INTEGRATION

`docs/registry/TRUTH.yaml` is authoritative over marketing and sales assets.

- Never modify TRUTH.yaml to match a claim. Modify the implementation, OR demote the claim.
- Never mark `status: live` without 30 days of runtime telemetry. Use `pilot`, `partial`, or `roadmap` otherwise.
- New capabilities default to `pilot`. Promotion to `live` requires 30 days of production telemetry.
- When in doubt, `roadmap` is safe.

---

## 7. CLAIMS REGISTRY INTEGRATION

`commercial/claims_registry.yaml` governs every user-facing statement.

- `forbidden` claims MUST NOT appear anywhere (including fixtures, error messages, placeholders).
- `restricted` claims require conditions enforced in code (customer tier, disclaimer, etc.).
- `approved` claims are safe to use.

**Hard-forbidden regardless of scope:**
- "SOC 2 compliant" (until auditor issues report)
- "ISO 27001 certified" (until certified)
- "100% accurate" (no ML system is)
- "Fully autonomous" (Dealix is policy-bound by design)
- "Military-grade" / "bank-grade" (undefined marketing phrases)
- "Zero risk" / "Absolute security"

These are non-negotiable and survive any founder override. Claims honesty is a regulatory and reputational floor.

---

## 8. PRE-COMMIT CHECKLIST

Before every `git commit`, confirm:

- [ ] Does this change add a user-facing capability not in `commercial/claims_registry.yaml` with status `approved`? If yes, add it with `status: roadmap` or `pilot`.
- [ ] Does this modify `docs/registry/TRUTH.yaml`? If yes, run `scripts/validate_truth_registry.py` and require PR review.
- [ ] New dependency? Pinned version, SBOM update, `pip-audit` / `npm audit` pass.
- [ ] Touches an RLS-governed table? Test coverage includes cross-tenant fuzz.
- [ ] New user-facing text? Arabic parity confirmed OR English-only exception logged.
- [ ] Performance-critical path? Baseline comparison against `docs/baselines/perf_*.json`.

### Commit message format

```
<type>(<scope>): <short summary>

Truth-registry-updated: <yes|no>
Claims-registry-updated: <yes|no>

<longer body if needed>
```

---

## 9. EXECUTION LOG

Every meaningful action by a coding agent appends to `docs/execution_log.md`:

```
## YYYY-MM-DD HH:MM — <agent> — <task>

- Branch: <branch>
- Commit: <sha>
- Outcome: <short summary>
- Next: <what should happen next>
```

---

## 10. ESCALATION TRIGGERS

Stop and escalate to founder if:

- A commit would mark a claim as `live` without 30 days of runtime evidence.
- A commit would violate an invariant in §4 or §5 without a documented exception.
- Truth Registry audit would demote a claim that is currently published externally.
- Pentest finding with CVSS ≥ 9 is open > 72 hours.
- You are generating more than 1,000 lines of code in one session without tests.

---

## 11. META: HOW TO CHANGE THIS FILE

This file changes via:
1. A formal founder decision logged to `docs/internal/strategic_decisions/YYYYMMDD_claude_md_update.md`.
2. PR with at least one reviewer (human or separate agent).
3. Version bump.

Changes to the invariants in §4, §5, §6, §7 require extra review — these protect the founder, customers, and regulators, not just the project.

---

**Owner:** Founder (Sami Mohammed Assiri)
**Next review:** On request
