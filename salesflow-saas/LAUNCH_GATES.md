# Dealix Launch Gates Checklist

**Version:** 2.0.0
**Last verified:** 2026-04-25 (Railway live check)
**Target:** 24/33 closed before declaring Soft Launch

---

## Product Gates

| # | Gate | Status | Evidence |
|---|------|--------|---------|
| P1 | Backend deployed + healthz=200 | **Closed** | Railway returns `{"status":"ok"}` |
| P2 | Pricing API returns plans | **Closed** | 3 plans, SAR currency, verified live |
| P3 | Route/Score/Message endpoints | **Closed** | All return 200 with rules-based output |
| P4 | Enrich-tech working | **Closed** | Foodics: HubSpot+WhatsApp+GTM+HubSpot Forms detected |
| P5 | Automation endpoints (targeting/email/reply) | **Closed** | 4 new endpoints on main, committed |
| P6 | Landing page live (dealix.me) | **Closed** | Returns 200 |
| P7 | Trial signup form | **Closed** | trial-signup.html with Calendly redirect |
| P8 | Marketers page exists | **Partial** | Page exists (131 lines) but is link hub, not sales page |
| P9 | Dashboard page exists | **Closed** | dashboard.html accessible |

## Operations Gates

| # | Gate | Status | Evidence |
|---|------|--------|---------|
| O1 | RUNBOOK written | **Closed** | RUNBOOK.md — 5 scenarios |
| O2 | SLO defined | **Closed** | SLO.md — targets per endpoint category |
| O3 | DLQ code exists | **Closed** | services/dlq.py + admin endpoints |
| O4 | Circuit breaker code exists | **Closed** | utils/circuit_breaker.py + admin endpoint |
| O5 | k6 load test script | **Closed** | scripts/k6_smoke_test.js |
| O6 | Dockerfile optimized | **Closed** | Multi-stage, CPU-only torch |
| O7 | Root /health for Railway | **Closed** | Returns {"status":"ok"} |
| O8 | Rollback drill tested | **Open** | Not executed |
| O9 | DB restore drill tested | **Open** | Not executed |

## Revenue Gates

| # | Gate | Status | Evidence |
|---|------|--------|---------|
| R1 | Pricing defined (API + docs) | **Closed** | 999/2490/7999 SAR + 499 pilot |
| R2 | Manual payment path (bank/STC) | **Closed** | Documented in COMMAND_CENTER + revenue-activation/ |
| R3 | Calendly booking active | **Closed** | Link verified active |
| R4 | Outreach templates ready | **Closed** | 6 segments × 9 sectors × Arabic messages |
| R5 | 60 targets with messages | **Closed** | SAUDI_60_TARGETS.md |
| R6 | Agency partner offer | **Closed** | AGENCY_PARTNER_OFFER.md — 3 tiers |
| R7 | Moyasar checkout working | **Blocked** | Returns 502 — Moyasar-side KYC/key |
| R8 | First 5 messages sent | **Open** | 0/5 — awaiting Sami |
| R9 | First demo booked | **Open** | 0 booked |
| R10 | First payment received | **Open** | 0 SAR |

## Measurement Gates

| # | Gate | Status | Evidence |
|---|------|--------|---------|
| M1 | PostHog client code | **Closed** | services/posthog_client.py — 16 event types |
| M2 | PostHog receiving events | **Open** | POSTHOG_API_KEY missing in Railway |
| M3 | GROQ_API_KEY in Railway | **Open** | Missing — LLM features degraded |
| M4 | GOOGLE_SEARCH_API_KEY in Railway | **Open** | Missing — /search returns 503 |
| M5 | SENTRY_DSN in Railway | **Open** | Missing — no error alerting |
| M6 | Daily revenue dashboard endpoint | **Closed** | `/api/v1/dashboard/metrics` returns 200 |

## Governance Gates

| # | Gate | Status | Evidence |
|---|------|--------|---------|
| G1 | Approval center code | **Closed** | approval_center.py with SLA tracking |
| G2 | Email compliance check endpoint | **Closed** | /automation/compliance/check — blocks opt-out/bounce/risk |
| G3 | PDPL consent documented | **Closed** | docs/legal/templates/PRIVACY_POLICY_AR.md |
| G4 | Claims registry | **Closed** | commercial/claims_registry.yaml |
| G5 | Outreach opt-out in every email | **Closed** | "إيقاف" line in all templates |

---

## Summary

| Category | Closed | Partial | Open | Blocked | Total |
|----------|--------|---------|------|---------|-------|
| Product | 8 | 1 | 0 | 0 | 9 |
| Operations | 7 | 0 | 2 | 0 | 9 |
| Revenue | 6 | 0 | 3 | 1 | 10 |
| Measurement | 2 | 0 | 4 | 0 | 6 |
| Governance | 5 | 0 | 0 | 0 | 5 |
| **Total** | **28** | **1** | **9** | **1** | **39** |

**28/39 closed (72%). 9 open. 1 blocked.**

Open items breakdown:
- 4 are env keys (Sami adds in Railway: GROQ, GOOGLE_SEARCH, POSTHOG, SENTRY)
- 3 are sales activity (send messages, book demo, receive payment)
- 2 are operational drills (rollback, DB restore)

**Verdict:** Product and governance are launch-ready. Revenue is blocked on sales activity, not engineering. Measurement is blocked on env keys, not code.
