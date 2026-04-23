# V004 — No-Founder Customer Demo Test

> **Status**: Template ready — founder schedules 3 sessions
> **Gate**: Acceptance = 2 of 3 fresh testers complete the golden path unassisted in <30 minutes with no show-stopper
> **Target completion**: Week 6

---

## Purpose

Eliminate "founder-assisted success" bias. If the product requires the founder in the room, it is not ready for pilot.

---

## Tester Profile (matches ICP Filter §3)

- Commercial operations background (CFO adjacent, Sales Ops, RevOps)
- 3+ years in Saudi/GCC enterprise
- Bilingual (Arabic + English)
- Has NOT been exposed to Dealix demo before
- NOT a founder friend (too generous in feedback)
- Compensated 500 SAR + short LinkedIn endorsement

---

## Protocol

### Before the Session

1. Provide tester a single PDF brief (2 pages max) with:
   - What Dealix is (30 seconds)
   - Credentials for a seeded demo tenant
   - Goal: "Bring a new partner through the golden path and generate an evidence pack"
2. Confirm tester will screen-share
3. Confirm 60-minute window (30 for task + 30 for retro)

### During the Session

1. Founder is on the call but **MUTED** and video OFF
2. Tester proceeds without assistance
3. Observer (founder + one engineer) takes notes on the Friction Log template
4. **DO NOT** intervene even if tester is stuck, unless >10 minutes on same step → then ask: "What are you trying to do right now?" (diagnostic only)

### After the Session

1. Ask tester 5 questions (see below)
2. Tester uninstalls / forgets credentials
3. Add findings to `docs/customer_learnings/friction_log.md` within 24h

---

## The 5 Post-Session Questions

1. In one sentence, what did Dealix do for you?
2. What was the one thing that felt confusing or wrong?
3. On a scale of 1–10, how likely are you to recommend this to a peer CFO/COO? (NPS)
4. What word(s) would you use to describe the UI? (signature capture)
5. If you had to pay $3,000/year for this, what would you need to see added first?

---

## Scoring (Pass / Fail per tester)

| Dimension | Pass | Fail |
|-----------|------|------|
| Time to golden path completion | <30 min | >30 min or abandoned |
| Show-stoppers encountered | 0 | 1+ (e.g., crash, auth loop, untranslated Arabic, broken approval) |
| NPS | ≥7 | ≤6 |
| Arabic experience | "clean" or "native" | "broken" or "translated feel" |

**Overall verdict**: 2 of 3 testers PASS → V004 green. Anything less → iterate UX before pilot.

---

## Deliverables

- [ ] 3 session recordings archived at `docs/customer_learnings/v004/` (PRIVATE)
- [ ] 3 completed friction logs
- [ ] Aggregated findings report at `docs/customer_learnings/v004/summary.md`
- [ ] Top-5 UX issues added to Wave A backlog
