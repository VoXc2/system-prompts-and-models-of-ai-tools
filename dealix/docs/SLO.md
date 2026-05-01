# Dealix Service Level Objectives (SLO) — v3.0.0

**Status:** Draft / Skeleton
**Owner:** Sami (sami.assiri11@gmail.com)
**Review cadence:** Monthly for first 3 months, then quarterly

---

## Philosophy

We are in **Primitive Launch** phase with <10 customers. SLOs should be:
- **Conservative** (high bar) on correctness and security
- **Lenient** on latency until we have real traffic baselines
- **Boring** — easy to explain, easy to measure, easy to page on

No 99.99% theater. If we can't measure it cheaply, it's not an SLO.

---

## Tier 1 — Paid-customer critical path

| SLI | SLO | Measurement | Why |
|---|---|---|---|
| `/health/deep` returns 200 | **99.5%** over 30 days | UptimeRobot poll every 60s | Core liveness — if this is red, nothing works |
| `/api/v1/webhooks/moyasar` p95 latency | **<2000ms** | Sentry transaction sampling | Payment webhook must not time out and retry incorrectly |
| `/api/v1/checkout` success rate | **>98%** | 2xx / total, excl. 4xx from bad input | Revenue path — 5xx here loses real money |
| Moyasar payment event → PostHog event | **<60s e2e** | timestamp delta | Funnel accuracy depends on this |

**Error budget (30d):** 3.6 hours of `/health/deep` downtime.

## Tier 2 — Operational

| SLI | SLO | Measurement |
|---|---|---|
| DLQ depth (`webhooks` queue) | **<10 entries** at any time | `/admin/dlq/stats` poll every 5m |
| DLQ age (oldest entry) | **<24h** | queue inspection; alert if older |
| Approvals pending | **<50 requests** | `/admin/approvals/stats` |
| LLM provider fallback rate | **<5%** of requests | `/admin/costs` breakdown |

## Tier 3 — Cost

| SLI | SLO | Measurement |
|---|---|---|
| Daily LLM spend | **<$10 USD/day** with alert | `/admin/costs` aggregated daily |
| Redis memory | **<500MB** | `redis-cli INFO memory used_memory_human` |
| Postgres connections | **<80** | `pg_stat_activity` count |

---

## Alerting policy

- **Page Sami immediately** if:
  - `/health/deep` returns non-200 for >5 consecutive minutes
  - DLQ `webhooks` depth >50
  - Moyasar webhook 5xx rate >5% over 10 minutes
- **Slack/email (non-urgent)** if:
  - Any Tier 1 SLO burns >25% of its 30d budget in a single day
  - Daily LLM cost >$15
  - Approvals pending >100

---

## Dashboards (to build)

Minimum viable dashboard (Grafana or Sentry Dashboards):

1. **Liveness row:** `/health`, `/health/deep`, process uptime
2. **Revenue row:** /checkout 2xx/5xx count (last 24h), pending approvals, Moyasar webhook rate
3. **Backlog row:** DLQ depth per queue, oldest entry age, approvals pending
4. **Cost row:** LLM spend per provider (last 24h), Redis memory, Postgres connections

**Current state:** 0/4 rows built. Sentry already collects performance data but no dashboard cut yet.

---

## What closes O5 gate

1. This document merged to `docs/SLO.md` ✅ (this PR)
2. At least Tier 1 dashboard built and linked in RUNBOOK.md → **blocked on UptimeRobot API key** for external health SLI
3. Alert routing configured → **blocked on UptimeRobot + Slack/email settings**

---

## Revisions

| Date | Change | Author |
|---|---|---|
| 2026-04-23 | Initial skeleton created as part of Primitive Launch D0 hardening | Agent (approved by Sami) |
