# 🎛️ Dealix — Company Control Center

**Single source of truth for today's operating state.** Everything else is reference.

Last updated: 2026-04-24 · Keep this file fresh — update it before/after every operating session.

> 🌅 **Start here every morning:** [`docs/ops/TODAY.md`](TODAY.md) — the 60-minute command page.
> 💰 **When a prospect says yes:** [`docs/ops/FIRST_REVENUE_ATTEMPT.md`](FIRST_REVENUE_ATTEMPT.md) — 15-min close-to-paid script.
> 🧾 **Generate an invoice:** `bash docs/ops/moyasar_live_test.sh customer@email.com 999 starter`

---

## 🚦 Decision State

| Area | State | Evidence |
|------|-------|----------|
| Backend | ✅ LIVE | `curl https://web-dealix.up.railway.app/healthz` → 200 |
| Landing | ✅ LIVE | https://voxc2.github.io/dealix |
| Demo form | ✅ VERIFIED | POST → `{ok: true, calendly_url, message}` |
| Partner form | ✅ VERIFIED | POST → `{ok: true, message}` |
| Pricing API | ✅ LIVE | Returns 3 plans JSON |
| Monitoring | ✅ AUTO | GitHub Actions healthcheck every 15 min → auto-creates P0 issue on fail |
| Revenue (Moyasar live) | 🔴 BLOCKED | `account_inactive_error` — KYC pending |
| Revenue (manual) | ✅ READY | `MANUAL_PAYMENT_SOP.md` — bank transfer / STC Pay |
| Sentry | 🟡 SDK READY | DSN empty — Sami provides DSN → I set via Railway |
| First DM | ⏸️ QUEUED | Exact text in `today_send_queue.md` |

**Overall: COMPANY_OPERATING_MANUAL_REVENUE**

---

## 🔗 Live URLs

| Purpose | URL |
|---------|-----|
| **Homepage (custom domain)** | **https://dealix.me** ✅ SSL live |
| Homepage (fallback) | https://voxc2.github.io/dealix/ |
| Marketers page | https://dealix.me/marketers.html |
| Pricing page | https://dealix.me/pricing.html |
| Partners page | https://dealix.me/partners.html |
| **Backend API (custom)** | https://api.dealix.me 🟡 Railway routing finalizing |
| Backend API (fallback) | https://web-dealix.up.railway.app |
| Backend docs | https://web-dealix.up.railway.app/docs |
| Book demo | https://calendly.com/sami-assiri11/dealix-demo |
| Repo | https://github.com/VoXc2/dealix |

---

## 💳 Payment Paths (3 parallel)

### Path A — Moyasar Live (BLOCKED, waiting on KYC)
- Sami must complete KYC at https://dashboard.moyasar.com/settings/business
- Required: CR/freelance license · National ID · Bank IBAN · Business address
- Activation: 1-3 business days after submission
- Once active: Sami sends new `sk_live_...` → I update Railway env → verify 1 SAR flow

### Path B — Moyasar Test (INSTANT unblock option)
- Sami creates sandbox account at Moyasar → gets `sk_test_...` key
- Sends to me → I set in Railway → verify full automated flow today (using test cards)
- Not real money but proves the entire technical revenue round-trip works

### Path C — Manual Revenue (AVAILABLE NOW)
- Use `docs/ops/MANUAL_PAYMENT_SOP.md`
- Bank transfer to Sami's business IBAN
- STC Pay to Sami's number
- Customer pays → Sami confirms in bank → updates `pipeline_tracker.csv` → starts onboarding
- **Valid for first 10 customers** — after that, automate

**Current path in use:** C (Manual)

---

## 🎯 Top 10 Priority Leads (from `pipeline_tracker.csv`)

### Tier A — Direct customers (5)
1. **عبدالله العسيري** · Lucidya CEO · LinkedIn · Priority: surname affinity
2. **Ahmad Al-Zaini** · Foodics CEO · LinkedIn · Series C $170M
3. **Nawaf Hariri** · Salla CEO · Twitter + LinkedIn · 70K merchants distribution
4. **Hisham Al-Falih** · Lean Technologies CEO · LinkedIn · 300+ API customers
5. **Ibrahim Manna** · BRKZ Founder · LinkedIn · $30M debt contech

### Tier B — Agency partners (5)
6. **Peak Content** · Service exchange target
7. **Digital8** · Full-service agency
8. **Brand Lounge** · Referral partner
9. **Qatar Digital** · KSA/UAE agency
10. **Wavy Saudi** · White-label candidate

---

## 📤 Today's Send Queue (Priority 1)

See `docs/ops/today_send_queue.md` — 10 ready-to-send messages across LinkedIn direct + agency partner track.

**Execution rule:** 5 per hour max. Respond to replies within 30 min.

---

## 📝 Today's Content Queue

Today (publish 1): **Founder Launch Post** (from `launch_content_queue.md`)

Rest of week:
- Day +1: Agency angle post
- Day +2: Problem angle post
- Day +3: Reply to 3 relevant tweets with Dealix angle
- Day +4: Customer pain post
- Day +5: Partner invitation post
- Day +6: AI sales rep positioning post

All copy is ready. Publishing requires Sami's LinkedIn/X identity.

---

## 🤝 Partner Queue

10 agency targets in tracker (rows 22-29 + 2 freelance). Partner DM template ready in `launch_content_queue.md`. Send max 2/day to avoid burn.

Partner packages:
- **Starter:** 3,000 SAR setup + 20% of client MRR
- **Growth:** 8,000 SAR setup + 25% of client MRR
- **Scale:** 25,000 SAR setup + 30% of client MRR + white-label option

---

## 🚫 Open Blockers

| # | Blocker | Owner | Unblock action | ETA |
|---|---------|-------|----------------|-----|
| 1 | Moyasar KYC | Sami | Complete dashboard KYC OR send test key | 1-3 days OR instant |
| 2 | SENTRY_DSN empty | Sami | Create Sentry project → send DSN | 5 min |
| 3 | First LinkedIn DM not sent | Sami | Open LinkedIn → paste → send | 3 min |
| 4 | POSTHOG_KEY placeholder in landing | Sami (or me once new key provided) | Send real key | 2 min |

None of these block **selling today** via manual path.

---

## 🎬 Next 5 Actions (executable now)

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | Send LinkedIn DM #1 to Abdullah Al-Assiri | Sami | Today | ⏸️ Ready in `today_send_queue.md` |
| 2 | Publish Founder Launch post on LinkedIn/X | Sami | Today | ⏸️ Copy in `launch_content_queue.md` |
| 3 | Complete Moyasar KYC OR send sandbox test key | Sami | Today | ⏸️ Dashboard access needed |
| 4 | Send Sentry DSN (create project → copy DSN) | Sami | Today | ⏸️ 5 min |
| 5 | Send 2 agency partner DMs | Sami | Today | ⏸️ Copy in `launch_content_queue.md` |

---

## 📊 Daily Scorecard Template (fill end-of-day)

```
Date: ____
INPUTS           | target | actual
---------------- | ------ | ------
New leads added  | 10     | __
DMs sent         | 5      | __
Follow-ups       | 5      | __
Partner DMs      | 2      | __
Content posts    | 1      | __

RESPONSES
Replies          | 1-2    | __
Demos booked     | 0-1    | __
Demos completed  | 0-1    | __

REVENUE
Pilots started   | 0-1    | __
Payments req'd   | 0-1    | __
Payments recv'd  | 0      | __
MRR added        | 0 SAR  | __ SAR

LEARNING
Best channel     |        | __
Biggest blocker  |        | __
Tomorrow change  |        | __
```

---

## 📚 Reference Documents

| File | Purpose |
|------|---------|
| `docs/ops/TODAY.md` | 🌅 Morning 60-min command page — open this first |
| `docs/ops/FIRST_REVENUE_ATTEMPT.md` | 💰 15-min close-to-paid playbook |
| `docs/ops/moyasar_live_test.sh` | 🧾 One-command invoice generator (Pilot/Starter/Growth/Scale) |
| `docs/ops/pipeline_tracker.csv` | 50 leads, source of truth |
| `docs/ops/launch_content_queue.md` | All outreach + content copy |
| `docs/ops/today_send_queue.md` | Today's ready-to-send 10 messages |
| `docs/ops/MANUAL_PAYMENT_SOP.md` | How to collect money without Moyasar automation |
| `docs/ops/FIRST_CUSTOMER_ONBOARDING_CHECKLIST.md` | Intake → Day 1 → Day 7 |
| `docs/ops/FIRST_CUSTOMER_DELIVERY_TEMPLATE.md` | How to manually deliver Dealix until dashboard exists |
| `docs/ops/DAILY_OPERATING_LOOP.md` | Hour-by-hour daily system |
| `docs/ops/THREE_CUSTOMERS_PER_DAY_OPERATING_MODEL.md` | Staged math + 4-tier growth plan |
| `.github/workflows/scheduled_healthcheck.yml` | Auto-monitor with issue creation on failure |
| `DEALIX_COMPANY_OPERATIONAL_STATE.md` | Full state snapshot (repo root) |

---

## 🎯 Week 1 Target (conservative)

- 50 touches
- 21 follow-ups
- 5-7 demos
- 1-2 pilots signed (manual payment if needed)
- 0-1 paid customers

## 30-Day Target

- 250 touches
- 20-25 demos
- 5-10 pilots
- 2-3 paid customers (pending Moyasar or via manual)
- 1 agency partner signed

## 90-Day Target

- 750 touches
- 60-80 demos
- 25-30 pilots
- 10-15 paid customers
- 3-5 agency partners
- First referral won

Full math in `THREE_CUSTOMERS_PER_DAY_OPERATING_MODEL.md`.

---

## 🚨 Production Failure Protocol

1. GitHub Actions healthcheck auto-creates Issue labeled `production-down` + `P0`
2. Sami sees issue in repo notifications / email
3. Runbook: `docs/ops/INCIDENT_RUNBOOK.md`
4. Common fix: Railway → Deployments → rollback last successful
5. Sentry (when DSN set): will capture 5xx errors with Slack alert (when integration configured)

---

## ⚡ If a customer says yes TODAY

1. Confirm plan (Starter 999 / Growth 2,999 / Scale 7,999 / Pilot 1 SAR)
2. Send manual invoice from `MANUAL_PAYMENT_SOP.md` (bank IBAN + STC Pay)
3. Customer pays → Sami confirms within 30 min
4. Sami updates `pipeline_tracker.csv` row: `payment_status=paid, revenue_sar=[amount]`
5. Sami starts `FIRST_CUSTOMER_ONBOARDING_CHECKLIST.md` kickoff call within 24 hours
6. Manual fulfillment per `FIRST_CUSTOMER_DELIVERY_TEMPLATE.md` for first 10 customers

---

**Owner:** Sami Assiri · sami.assiri11@gmail.com
**This file is law until changed.** Any operating decision must be reflected here first.
