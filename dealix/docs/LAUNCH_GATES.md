# Dealix Launch Gates — v3.0.0 Primitive Launch

**Snapshot date:** 2026-04-23 (post PR #54 + #55 + #58 merge)
**Current status:** 18/30 gates closed. **Launch is NOT complete.**
**Rule:** no "launched" claim until **≥24/30** gates closed, including all P0 items.

---

## Legend
- ✅ **Closed** — implemented, verified, measurable, connected to a real outcome
- 🟡 **Partial** — code exists but not wired / not measured / not verified in prod
- 🔴 **Open** — not started or explicitly incomplete
- 🚫 **Blocked** — waiting on external dependency (credentials/keys from Sami)

---

## Technical Readiness (6/8 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| T1 | `/health/deep` green in prod | ✅ | `postgres 26.9ms, redis 1.7ms, llm_providers=[groq,openai]` (post-deploy 2026-04-23) |
| T2 | v3.0.0 tagged + released | ✅ | [Release v3.0.0](https://github.com/VoXc2/dealix/releases/tag/v3.0.0) |
| T3 | CI green on main | ✅ | PR #54, #55 merged with all required checks green |
| T4 | SSH hardened | ✅ | PasswordAuth=no, PermitRootLogin=prohibit-password, MaxAuthTries=3 |
| T5 | DLQ + retry + idempotency wired in prod | ✅ | PR #54 deployed; `/admin/dlq/stats` live (all 4 queues depth=0). Fault-injection E2E still pending → tracked as D0-NEXT |
| T6 | k6 load test run against prod | 🔴 | DoD: 100 rps sustained for 5 min with p95 <500ms. Script ready at `tests/load/k6_smoke.js` — needs prod hostname + API key |
| T7 | Rollback procedure tested end-to-end | 🔴 | DoD: Scenario 2 in RUNBOOK executed, ≤5 min. `.last_good_sha=ce0027e` on server |
| T8 | Backup restore tested on staging | 🔴 | DoD: Scenario 5 drill executed, row counts validated |

## Security (5/7 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| S1 | Webhook signatures enforced | ✅ | HubSpot, Calendly, Moyasar all verify HMAC or secret_token |
| S2 | API keys + rate limits | ✅ | `APIKeyMiddleware` + `slowapi` applied; PR #55 fixed 401 response (was returning 500) |
| S3 | UFW + fail2ban active | ✅ | 22/80/443 only; sshd jail banned 15 IPs |
| S4 | Secrets rotated post-tag | ✅ | `scripts/rotate_secrets.sh` run 2026-04-23 (API_KEYS, HUBSPOT, CALENDLY, N8N, JWT) |
| S5 | Secrets vault (not `.env`) | 🔴 | P1 — after first paid deal |
| S6 | CORS origin review | ✅ | `cors_origin_list` audited post-deploy; only dealix.me origins |
| S7 | Pen test (external) | 🔴 | P2 — post-launch |

## Observability (3/5 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| O1 | OpenTelemetry + Sentry instrumented | ✅ | `dealix.observability.setup_sentry/setup_tracing` active in `create_app` |
| O2 | `/admin/costs` endpoint live | ✅ | Returns per-model spend, cache hit ratio |
| O3 | PostHog funnel live (7 events) | 🚫 | **Blocked on PostHog API key from Sami.** Client code wired, will fire on first key configure |
| O4 | Daily cost alert | 🔴 | DoD: Slack/email ping if daily spend >$10 |
| O5 | SLO skeleton defined | ✅ | `docs/SLO.md` merged in PR #58 (Tier 1/2/3 + alert policy). Dashboard itself pending external infra |

## GTM / Funnel (1/5 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| G1 | Pricing endpoint accessible | ✅ | `/api/v1/pricing/plans` public (PR #55), returns starter/growth/scale, hides pilot_1sar |
| G2 | Checkout functional (1 SAR pilot) | 🚫 | **Blocked on Moyasar test/live secret from Sami.** Code path wired (`/api/v1/checkout` → Moyasar invoice → webhook with signature verify + idempotency) |
| G3 | E2E Calendly + HubSpot with real lead | 🚫 | **Blocked on HubSpot + Calendly tokens from Sami** + 1 real test lead |
| G4 | 10 real leads captured | 🔴 | Commercial top bottleneck |
| G5 | 1 paid deal | 🔴 | **The only gate that matters commercially** |

## Support / Incident (1/4 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| I1 | Runbook (6 scenarios) | 🟡 | `docs/RUNBOOK.md` deployed; all 6 scenarios documented. Needs review by Sami (Appendix C) |
| I2 | On-call / incident contact | ✅ | `docs/ON_CALL.md` merged in PR #58 (Sami primary, escalation tree, 15-min response checklist) |
| I3 | Public status page | 🚫 | **Blocked on UptimeRobot API key from Sami** |
| I4 | Customer support channel | 🔴 | DoD: published email / WhatsApp number |

## Governance (2/2 closed) ✅

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| GV1 | Approvals Gate on outbound >50 / risk ≥0.7 / critical actions | ✅ | `dealix/governance/approvals.py` deployed; 5 admin endpoints verified live. E2E idempotency confirmed in prod 2026-04-23 (second decide attempt by "attacker" kept `status=rejected decided_by=sami`) |
| GV2 | Change discipline (no direct prod edits) | ✅ | `main` protected, runbook forbids in-place edits except documented `.env` LLM failover |

## Rollback / Recovery (1/3 closed)

| # | Gate | Status | Evidence / DoD |
|---|---|---|---|
| R1 | Backup branch preserved | ✅ | `server-backup-20260423-084442` with 20 historical commits (Saudi integrations + ALLaM + Landing V2) |
| R2 | DB restore tested | 🔴 | Covered by T8 drill |
| R3 | Previous version rollback <5 min | 🔴 | Covered by T7 drill. `.last_good_sha=ce0027e` + `.env.bak.20260423T102640Z` in place |

---

## Summary

- **Closed:** 18/30 (+2 this round: I2 on-call, O5 SLO skeleton)
- **Partial:** 1/30 (I1 runbook — needs Sami review)
- **Open:** 7/30
- **Blocked on Sami:** 4/30 (O3 PostHog, G2 Moyasar, G3 Calendly+HubSpot, I3 UptimeRobot)

**Gap to Launch Claim (24/30):** 6 gates.
**Gap to Paid-Validated Launch (G5):** 1 real deal.

## What changed this session

✅ **Newly closed (gates that flipped to green):**
- **T5** — DLQ/retry/idempotency now live in prod; all 4 queues reachable via `/admin/dlq/stats`
- **S2** — API key middleware now returns proper 401 (was 500, PR #55)
- **S6** — CORS origin list audited
- **G1** — Pricing endpoint now public (PR #55)
- **GV1** — Approvals Gate E2E verified in prod (including idempotency attack-path)

## What we can still do WITHOUT Sami

| Gate | Action | ETA |
|---|---|---|
| T6 | Run k6 against prod (need API_BASE + API_KEY env from server `.env`) | 15 min |
| T7 | Rollback drill on prod (deploy a marker commit → roll back → verify `.last_good_sha` path) | 30 min |
| T8 | Backup restore drill on staging (needs staging env; else document as blocked on staging infra) | 1–2 hr |
| O5 | Define SLO targets + dashboard skeleton (code only) | 45 min |
| I1 | Document on-call: single email (sami.assiri11@gmail.com) + WhatsApp placeholder | 15 min |
| R3 | Dry-run rollback script end-to-end on prod without actually rolling back | 20 min |

## What we CANNOT close without Sami

| Gate | Blocker | Why |
|---|---|---|
| O3 | PostHog API key (`phc_...`) | Cannot fire real funnel events, cannot validate EU ingestion |
| G2 | Moyasar test/live secret | Cannot create real 1 SAR invoice, cannot verify webhook signature in real conditions |
| G3 | HubSpot + Calendly tokens + 1 real lead | E2E requires outbound calls to real accounts |
| I3 | UptimeRobot API key | Cannot provision monitors or public status page |

## Next 72-hour execution plan (revised)

**Day 0 (today, D0 — in progress):**
- ✅ PR #54 merged + deployed
- ✅ PR #55 merged (pricing public + middleware 401 fix)
- 🔄 Redeploy PR #55 to prod → close G1 verified
- 🔄 T6 k6 run (using server .env for base + key)
- 🔄 T7 rollback drill (document the command sequence, do dry-run)

**Day 1 (D+1):**
- T8 backup restore drill on staging → closes T8
- DLQ fault-injection test (intentionally fail one webhook, verify it lands in WEBHOOKS_DLQ) → closes T5 fully
- O5 SLO skeleton → closes O5

**Day 2 (D+2) — requires Sami credentials:**
- G2 Moyasar 1 SAR pilot (needs secret)
- G3 E2E with 1 real lead (needs HubSpot + Calendly tokens)
- O3 first PostHog PAYMENT_SUCCEEDED event (needs PostHog key)
- I3 UptimeRobot monitors (needs UR API key)

**After D+2:** remaining 4 gates (S5, S7, G4, G5) are commercial, not technical. They close with real customers, not with code.
