# Dealix Launch Gates Checklist

**Version:** 1.0.0  
**Last updated:** 2026-04-23  
**Target:** 24/30 gates closed before declaring Soft Launch

---

## Technical Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| T1 | `/health/deep` all green | Closed | Postgres + Redis + LLM providers |
| T2 | v3.0.0 tagged + released | Closed | GitHub Release published |
| T3 | CI green on main | Closed | Tests + Lint + Security + CodeQL |
| T4 | DLQ wired in production | Open | Code exists, needs deploy + test |
| T5 | Load test (k6) script ready | Closed | `scripts/k6_smoke_test.js` — needs execution on prod |
| T6 | Rollback tested (<5min) | Open | Needs drill |
| T7 | Backup restoration tested | Open | Needs drill on staging |

## Security Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| S1 | Webhook signature verification | Closed | Moyasar + WhatsApp |
| S2 | API keys + rate limiting | Closed | SlowAPI configured |
| S3 | SSH hardened + key-auth only | Closed | fail2ban active |
| S4 | UFW firewall active | Closed | 22/80/443 only |
| S5 | Secrets not in git | Partial | .env on disk, not vault |
| S6 | CORS policy reviewed | Partial | Set but not audited |
| S7 | Security scan (basic) | Open | OWASP ZAP or similar |

## Observability Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| O1 | OpenTelemetry + Sentry wired | Closed | DSN configured |
| O2 | `/admin/costs` endpoint | Closed | LLM cost tracking |
| O3 | PostHog funnel (7 events) | Open | Client built, needs deploy + verify |
| O4 | Daily cost alert | Open | Needs cron or PostHog action |
| O5 | SLO defined (p95 latency) | Closed | `SLO.md` — targets set for all endpoint categories |

## GTM / Funnel Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| G1 | Pricing accessible | Partial | Router built, needs deploy |
| G2 | Checkout functional | Open | Moyasar integration ready, needs real test |
| G3 | Calendly E2E tested | Open | Code exists, no real booking test |
| G4 | HubSpot sync E2E tested | Open | Code exists, no real sync test |
| G5 | First 10 leads captured | Open | 0 leads in funnel |
| G6 | First paid transaction | Open | 0 SAR revenue |

## Support / Incident Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| I1 | Runbook written | Closed | `RUNBOOK.md` — 5 scenarios |
| I2 | On-call rota defined | Open | Solo founder = 24/7 for now |
| I3 | Status page | Open | UptimeRobot public page |
| I4 | Customer support channel | Open | WhatsApp Business or email |

## Recovery / Rollback Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| R1 | Git tags + backup branch | Closed | v3.0.0 + server-backup branch |
| R2 | DB restore tested | Open | Needs drill |
| R3 | Previous version deployable <5min | Open | Needs drill |

## Governance Gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| V1 | Approvals gate on outbound | Partial | approval_center exists, threshold enforcement built |

---

## Summary

| Category | Closed | Partial | Open | Total |
|----------|--------|---------|------|-------|
| Technical | 4 | 0 | 3 | 7 |
| Security | 4 | 2 | 1 | 7 |
| Observability | 3 | 0 | 2 | 5 |
| GTM/Funnel | 0 | 1 | 5 | 6 |
| Support | 1 | 0 | 3 | 4 |
| Recovery | 1 | 0 | 2 | 3 |
| Governance | 0 | 1 | 0 | 1 |
| **TOTAL** | **13** | **4** | **16** | **33** |

**Verdict:** 13/33 closed. Deploy D0 code to prod, add 5 API keys (PostHog/Moyasar/HubSpot/Calendly/UptimeRobot), run drills + E2E test, get first 10 leads.

**Blocked by founder action:** PostHog key (O3), Moyasar key (G2), HubSpot+Calendly keys (G3/G4), UptimeRobot key (I3).
