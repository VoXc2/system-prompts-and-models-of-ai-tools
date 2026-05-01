# 📊 Dealix — Daily Scorecard

**Update at end of each working day (17:00 Saudi time).**

---

## Day 2 Final — All Non-Blocked Phases Closed

**Live diag env = Dealix / service = web · 2026-04-24**

### Endpoints (live verified)
- ✅ `/healthz`, `/api/v1/pricing/plans`, `/api/v1/prospect/demo`
- ✅ `/api/v1/prospect/route`, `/score`, `/message` (rules, no LLM)
- ✅ `/api/v1/prospect/bulk-enrich`, `/enrich-tech`
- ✅ `/api/v1/prospect/discover` (degraded demo)
- ✅ `/api/v1/prospect/enrich-domain` (tech+rules degraded)
- ⏸️ `/api/v1/prospect/search` → 503 (awaits Google keys in env Dealix)
- ⏸️ `/api/v1/checkout` → 502 (Moyasar live rejection; manual path ready)

### Keys in env `Dealix/web`
- SET: MOYASAR_SECRET_KEY, MOYASAR_WEBHOOK_SECRET, MOYASAR_PUBLIC_KEY, POSTHOG_API_KEY, APP_URL
- MISSING: GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CX, GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY, SENTRY_DSN

### Lead Machine
- 106 accounts in Saudi Lead Graph V2 (router-scored)
- TOP_25_DIRECT_CUSTOMERS.csv · TOP_25_PARTNERS.csv (22) · TOP_10_STRATEGIC_PARTNERS.csv
- TODAY_15_TARGETS.csv (5/5/3/2 split) + TODAY_15_MESSAGES.json (6 variants each)

### Content queue
- Posts 1-3 pre-existing (Founder / Agency / Problem)
- **Posts 4-7 added this pass:** Proof · Pilot Offer · Partner Invite · Week Recap

### Active Gates
- LinkedIn Message 1 (Abdullah Al-Assiri / Lucidya) = AWAITING `SENT`
- Messages 2-5 + Partner 1-5 + Posts 1-7 staged
- Atomic on-SENT protocol: update row 1 + schedule +2/+5/+10 + release next only

---



### Endpoints (production)
- ✅ `/healthz`, `/api/v1/pricing/plans`, `/api/v1/prospect/demo` — 200
- ✅ `/api/v1/prospect/enrich-tech` — 200 (free Saudi-tuned detector)
- ✅ `/api/v1/prospect/bulk-enrich` — 200 (up to 25 domains/req)
- ✅ `/api/v1/prospect/route` — **NEW** rules-based classifier + scorer
- ✅ `/api/v1/prospect/score` — **NEW** 100-pt scoring only
- ✅ `/api/v1/prospect/message` — **NEW** deterministic Arabic message generator
- ✅ `/api/v1/prospect/discover` — now serves **degraded demo** if LLM missing
- ✅ `/api/v1/prospect/enrich-domain` — now serves **tech + rules** if LLM missing
- ⏸️ `/api/v1/prospect/search` — awaits Google keys in env Dealix (503 with clear hint)
- ⏸️ `/api/v1/checkout` — Moyasar returns 502; manual path available

### Lead Intelligence Router files
- `SAUDI_LEAD_GRAPH_V2.csv` — all 106 accounts re-scored by rules router
- `TOP_25_DIRECT_CUSTOMERS.csv` — ranked
- `TOP_25_PARTNERS.csv` — ranked (22 rows)
- `TOP_10_STRATEGIC_PARTNERS.csv`
- `TODAY_15_TARGETS.csv` — 5 direct + 5 agency + 3 strategic + 2 content
- `TODAY_15_MESSAGES.json` — LinkedIn + email + WhatsApp-warm + +2/+5/+10 follow-ups per target

### Breakdown (rules-routed)
- DIRECT_CUSTOMER: 59
- AGENCY_PARTNER: 14
- STRATEGIC_PARTNER: 11
- REFERRAL_PARTNER: 8
- INVESTOR_OR_ADVISOR: 8
- CONTENT_COLLABORATION: 6

### Top by rules priority_score
1. Foodics (DIRECT, 78, P1)
2. Lucidya (DIRECT, 70, P1)
3. Sary (DIRECT, 61, P2)
4. Hakbah (DIRECT, 61, P2)
5. Lean (DIRECT, 58, P2)

**Note on scoring:** rules router is conservative — uses only evidence present. Higher P0 scores require more detected signals (hiring posts, recent funding press, etc.) which need Google CSE to fetch, currently blocked.

---

## Day 2 — Execution Day 1

**Date:** 2026-04-24 (continued session)
**Production:** ✅ Green (healthz 200, pricing 200, landing 200 — verified this session)
**Custom Domain:** ✅ **https://dealix.me LIVE** with Let's Encrypt SSL (valid until 2026-07-23, auto-renew). GitHub Pages DNS check successful. www + all subpages serving 200 with proper cert.
**API Custom Domain:** 🟡 api.dealix.me DNS + TXT verify in place; awaiting Sami click "Update" in Railway → Networking dialog to finalize SSL + routing.
**Moyasar:** ✅ Webhook secret live (401 bad_signature on test confirms secret read). sk_live_ KYC-activated but key in Railway still returning 502 — likely paste whitespace; manual path unaffected.
**Lead Intelligence Router v1:** ✅ Shipped — Prospector agent upgraded with 9 opportunity types + 100-pt scoring + risk levels + next-action enum. 5 specs in `docs/ops/lead_machine/`. Top-10 direct + Top-5 partner leads scored. Live UI on dealix.me.
**Operating docs shipped today:** objection_library_ar · sector_playbooks · agency_partner_kit · reply_handling_log · manual_payment_log · partner_send_queue.

### Inputs (target → actual)
| Metric | Target | Actual | Notes |
|--------|--------|--------|-------|
| DMs sent | 5 | 0 | Message 1 delivered to Sami, awaiting SENT |
| Agency DMs sent | 2 | 0 | Partner Msg 1 prepared, not released |
| Follow-ups sent | 0 | 0 | Nothing to follow up yet |
| Content posts | 1 | 0 | Founder Launch Post queued for Sami |
| New leads added | 0 | 0 | Pipeline at 50, no need |

### Responses
| Metric | Target | Actual |
|--------|--------|--------|
| Positive replies | 0-1 | 0 |
| Demos booked | 0-1 | 0 |
| Demos completed | 0 | 0 |

### Revenue
| Metric | Target | Actual |
|--------|--------|--------|
| Pilots started | 0 | 0 |
| Payments requested | 0 | 0 |
| Payments received | 0 SAR | 0 SAR |
| Cumulative MRR | 0 SAR | 0 SAR |

### Blockers / Status
- ✅ Production OK (backend + landing + pricing all 200)
- 🟡 Moyasar live blocked on KYC — `/api/v1/checkout` returns `payment_provider_error` (502)
- 🟡 No `sk_test_` key provided to session — sandbox round-trip cannot be proven until Sami sends one
- ✅ Manual payment path (`MANUAL_PAYMENT_SOP.md` + `FIRST_REVENUE_ATTEMPT.md`) fully operational — no prospect will be lost if they say yes
- ⏸️ LinkedIn access is Sami-side — all DMs gated on `SENT` confirmations

### Next Single Action
**Sami sends Message 1 to Abdullah Al-Assiri → replies `SENT`.** Everything else waits on that one event.

---

## Day 1 — Launch Day

**Date:** 2026-04-24
**Production:** ✅ Green (backend + landing + healthcheck all 200)

### Inputs (target → actual)
| Metric | Target | Actual | Notes |
|--------|--------|--------|-------|
| New leads added | 10 | 50 | Pipeline tracker seeded |
| DMs sent | 5 | 0 | 10 queued as GitHub Issues #99-108 |
| Agency DMs sent | 2 | 0 | Queued in issues |
| Follow-ups sent | 0 | 0 | N/A — Day 1 |
| Content posts | 1 | 0 | Queued as Issue #109 |

### Responses (target → actual)
| Metric | Target | Actual |
|--------|--------|--------|
| Positive replies | 0-1 | 0 |
| Demos booked | 0-1 | 0 |
| Demos completed | 0 | 0 |

### Revenue
| Metric | Target | Actual |
|--------|--------|--------|
| Pilots started | 0 | 0 |
| Payments requested | 0 | 0 |
| Payments received | 0 SAR | 0 SAR |
| Cumulative MRR | 0 SAR | 0 SAR |

### Blockers
- 🔴 Moyasar KYC (Sami → Issue #110)
- 🔴 First DM not sent (Sami → Issues #99-108)
- 🟡 Sentry DSN empty (Sami → Issue #111)

### Tomorrow's Top 5 Actions
1. Send 5 Tier-A direct DMs (Issues #99-103)
2. Send 5 agency partner DMs (Issues #104-108)
3. Publish Founder Launch post (Issue #109)
4. Complete Moyasar KYC OR send test key (Issue #110)
5. Set up Sentry DSN (Issue #111)

---

## Template — Day N

Copy this block each day:

```
## Day N — YYYY-MM-DD

**Production:** ✅ / ❌ [explain if red]

### Inputs
| Metric            | Target | Actual |
|-------------------|--------|--------|
| New leads added   | 10     | __     |
| DMs sent          | 5      | __     |
| Agency DMs sent   | 2      | __     |
| Follow-ups sent   | 5      | __     |
| Content posts     | 1      | __     |

### Responses
| Metric            | Target | Actual |
|-------------------|--------|--------|
| Positive replies  | 1-2    | __     |
| Demos booked      | 0-1    | __     |
| Demos completed   | 0-1    | __     |

### Revenue
| Metric             | Target | Actual     |
|--------------------|--------|------------|
| Pilots started     | 0-1    | __         |
| Payments requested | 0-1    | __         |
| Payments received  | 0 SAR  | __ SAR     |
| Cumulative MRR     | 0 SAR  | __ SAR     |

### Blockers
- [list open blockers]

### Tomorrow's Top 5 Actions
1. 
2. 
3. 
4. 
5. 

### Learning
- Best channel today: __
- Biggest blocker: __
- Change for tomorrow: __
```

---

## Weekly Review Template (fill every Friday 17:00)

```
## Week N Review — YYYY-MM-DD

### Funnel Conversion
- Touches: __
- Reply rate: __% (target 5%)
- Demo booking rate: __% (target 40% of replies)
- Demo show rate: __% (target 70%)
- Close rate: __% (target 20%)
- Payment completion: __% (target 80%)

### Revenue
- New MRR this week: __ SAR
- Churn this week: __ SAR
- Net new MRR: __ SAR
- Cumulative MRR: __ SAR

### Best / Worst
- Best-converting segment: __
- Worst-performing segment: __
- Kill this segment: __
- Double down on: __

### Experiment for next week
- Hypothesis: __
- Metric: __
- Outcome target: __
```

---

## 30-Day Cumulative Dashboard

Update this section on 30-day mark:

```
## 30-Day Dashboard — YYYY-MM-DD

Leads:          __ contacted  / 250 target
Demos:          __ completed  / 20 target
Pilots:         __ started    / 5 target
Paid:           __ customers  / 2 target
MRR:            __ SAR        / 4,000 SAR target

Partners:       __ signed     / 1 target
Referrals:      __ received   / 0 target
Case studies:   __ published  / 0 target
```

---

**This file is the single scorecard for Dealix company operations.**
