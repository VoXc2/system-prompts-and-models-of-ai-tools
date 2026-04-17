# Founding Backend Engineer — Dealix (Hire #2)

> **Compensation**: 25,000–40,000 SAR/month + 0.3–1.5% equity (vesting 4yr / 1yr cliff)
> **Location**: Riyadh-primary, remote within GMT±3 accepted
> **Reports to**: Founder
> **Start**: Within 60 days of offer

---

## The role

You will own the **durable execution and trust fabric** of Dealix — OpenClaw runtime, policy bridge, evidence ledger, durable checkpoints, idempotency, RLS, OpenTelemetry, and the AI model routing. This is the engine room.

Not a typical "backend dev." We need someone who thinks about guarantees, not endpoints. Correctness-oriented, skeptical of their own code, comfortable reading papers + PostgreSQL manuals + OpenTelemetry specs.

---

## What you will do in the first 90 days

1. Close the Program E/F/G/K runtime gaps to production-grade (currently partial).
2. Integrate DurableRuntime into Golden Path + Saudi Workflow so every multi-step flow survives restarts.
3. Deploy RLS to production (migration exists) and ensure V002 fuzz test (10,000 cross-tenant queries) stays at zero leaks.
4. Wire OpenTelemetry exporters to a real backend (Honeycomb / Grafana Tempo / Axiom) and make `trace_id` queryable from every log line.
5. Stand up load test baseline (V006 k6) against staging with 200 concurrent users.

---

## Requirements

- 5+ years Python + Postgres in production. Async Python (FastAPI or Starlette) essential.
- SQL that goes beyond ORMs — window functions, CTEs, partial indexes, pg_stat_statements.
- Have built or maintained at least one system with correctness guarantees (idempotency / retries / replay / consensus).
- Comfortable reading RFCs, CVEs, OWASP LLM Top 10, OpenTelemetry spec.
- Security mindset: can spot an SSRF, IDOR, or row-level auth bypass in a diff.

### Nice to have
- LLM provider abstraction experience (Groq, OpenAI, Anthropic, Bedrock)
- Temporal / Cadence / AWS Step Functions
- OpenFGA / SpiceDB / Cedar
- Arabic language skills (not required but helpful for eval work)

---

## Signals we want to see in your application

- Link to a production incident you diagnosed + fixed (postmortem or blog post)
- 200-word opinion on "why Temporal-style durable execution matters for AI agents"
- Most subtle bug you have fixed (2 paragraphs)

## Signals we do NOT want

- CRUD-only portfolios
- Fluff about "microservices" with no context on failure modes
- AWS certifications in lieu of production experience

---

## Interview loop (3 stages, max 5 hours total)

1. **Intro** (45 min) — Founder. Values fit, story check.
2. **Systems deep-dive** (75 min) — Walk through the Dealix codebase (shared ahead of time). Point out one thing you would refactor for correctness and one thing you would keep.
3. **Paid trial task** (4 hours, 3,000 SAR compensation):
   - Option A: Make DurableRuntime resume 1,000 interrupted flows on startup without duplicate side effects. Ship a PR + test.
   - Option B: Add OpenFGA to the approval bridge. Ship a PR + test.

No coding interviews of the "reverse a linked list" genre.

---

## Why you might want this

- Build the correctness backbone of a system that handles real enterprise money + regulatory audit.
- Hire #2 — your architecture decisions stick for years.
- No framework-of-the-week cargo cult; we pick and stay.
- Deep work friendly (Wed/Thu are deep-work days, no meetings).

## Why you might NOT want this

- You must write integration tests, not just unit tests.
- You will handle pager rotation (Founder + you, split week-on/week-off).
- Customer security questionnaires are part of your job, not "ops."

---

## Apply

Send to: founder@dealix.sa
Subject: `Founding Backend Engineer — [Your Name]`
Body: incident post-mortem link + 200-word opinion. No resume needed yet.
