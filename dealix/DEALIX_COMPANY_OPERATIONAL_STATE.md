# 🚀 Dealix — Company Operational State (Live)

**Status:** LAUNCHED (backend + landing live). Blocked on Moyasar account activation for REVENUE VERIFIED.
**Last verified:** 2026-04-24
**Base URL:** https://web-dealix.up.railway.app
**Landing:** https://voxc2.github.io/dealix/

---

## ✅ Live Endpoints (verified)

| Endpoint | Status | Response |
|----------|--------|----------|
| `GET /healthz` | 200 | `{"status":"ok","service":"dealix"}` |
| `GET /health` | 200 | `{status, version:"3.0.0", env:"production", providers:[]}` |
| `GET /api/v1/pricing/plans` | 200 | Starter/Growth/Scale JSON |
| `POST /api/v1/public/demo-request` | 200 | Returns Calendly URL on valid payload |
| `POST /api/v1/public/partner-application` | 200 | Returns Arabic success message |
| `GET /docs` | 200 | FastAPI Swagger UI |
| `GET /openapi.json` | 200 | OpenAPI spec |
| `POST /api/v1/checkout` | 502 | **Blocked:** Moyasar `account_inactive_error` |

---

## 📊 What's Working

### Infrastructure
- ✅ Railway deploy: service `web`, environment `Dealix`, builder RAILPACK auto-detects Dockerfile
- ✅ Dynamic `$PORT` binding via Dockerfile `/app/start.sh`
- ✅ Database: Railway Postgres auto-linked via `DATABASE_URL=${{Postgres.DATABASE_URL}}`
- ✅ Env vars (all set via Railway GraphQL API):
  - APP_SECRET_KEY, ADMIN_TOKEN, LOG_LEVEL, ENVIRONMENT, APP_ENV
  - APP_URL, PUBLIC_BASE_URL, CORS_ORIGINS, CALENDLY_URL
  - MOYASAR_SECRET_KEY, MOYASAR_WEBHOOK_SECRET, MOYASAR_PUBLIC_KEY
  - POSTHOG_API_KEY, POSTHOG_HOST, POSTHOG_ENABLED
  - CALENDLY_OAUTH_CLIENT_ID, CALENDLY_PAT, CALENDLY_WEBHOOK_SECRET
- ✅ Startup healthcheck passing (tini + uvicorn via Dockerfile CMD)

### Application
- ✅ All routers mounted: health, pricing, public, webhooks, leads, sales, sectors, admin, agents
- ✅ Sentry SDK initialized on startup (waiting for DSN)
- ✅ PostHog analytics initialized
- ✅ DLQ + idempotency in place for webhooks
- ✅ Moyasar invoice client code verified functional (blocked only by account status)

### Landing
- ✅ GitHub Pages serves from `gh-pages` branch
- ✅ All 4 pages (home/marketers/pricing/partners) return 200
- ✅ `window.DEALIX_API_BASE = 'https://web-dealix.up.railway.app'` baked in
- ✅ Demo form → backend → Calendly URL (verified round-trip)
- ✅ Partner form → backend (verified round-trip)

---

## 🔴 Blocked by Sami (manual dashboard action)

### 1. Moyasar Account Activation (CRITICAL for revenue)
**Error:** `{"type":"account_inactive_error","message":"Entity not activated to use live account"}`

**Steps Sami must take:**
1. Open https://dashboard.moyasar.com
2. Settings → Business → complete all KYC fields:
   - Commercial Registration (CR) or freelance license
   - National ID / Iqama
   - Bank account (IBAN)
   - Business address
3. Submit for review — typically activated within 1-3 business days
4. Once active, rotate `MOYASAR_SECRET_KEY` in Moyasar → paste new key into Railway (I can do this via API if you send the new key only)
5. Configure webhook:
   - URL: `https://web-dealix.up.railway.app/api/v1/webhooks/moyasar`
   - Events: `payment_paid`, `payment_failed`, `payment_refunded`
   - Secret: use existing `MOYASAR_WEBHOOK_SECRET` from Railway or regenerate

**Alternative for testing today:** Sami creates a Moyasar **test** account key (sk_test_...) — I can switch Railway env var to test mode for full flow verification without touching real money.

### 2. SENTRY_DSN (not set)
Sami should:
1. Open https://sentry.io → create project "dealix"
2. Copy the DSN (starts with `https://...@...ingest.sentry.io/...`)
3. Send it — I add to Railway via GraphQL.

### 3. UptimeRobot (not configured)
Sami opens https://uptimerobot.com → Add HTTPS monitor:
- URL: `https://web-dealix.up.railway.app/healthz`
- Interval: 5 min
- Alert to phone/email
- Save

### 4. First LinkedIn DM (identity-only)
Ready in `docs/ops/launch_content_queue.md`. Sami opens LinkedIn → pastes → sends.

---

## 🎯 Launch Truth Table

| Area | Status |
|------|--------|
| GitHub main + CI | ✅ VERIFIED READY (SHA ahead of 44cc3513e3) |
| Landing pages live | ✅ VERIFIED READY |
| Backend production | ✅ VERIFIED READY (web-dealix.up.railway.app) |
| Demo form → backend | ✅ VERIFIED READY |
| Partner form → backend | ✅ VERIFIED READY |
| Moyasar live payments | 🔴 BLOCKED (account activation) |
| Moyasar webhook | ❌ NOT READY (depends on above) |
| 1 SAR verified | ❌ NOT READY (depends on above) |
| Sentry DSN | 🟡 EMPTY (waiting for DSN) |
| UptimeRobot | ❌ NOT READY |
| First DM sent | ❌ NOT READY (Sami identity) |
| CRM tracker | ✅ VERIFIED READY (`docs/ops/pipeline_tracker.csv`) |
| Launch content queue | ✅ VERIFIED READY (`docs/ops/launch_content_queue.md`) |

---

## 📋 Pipeline (Day 1 Seed — 5 priority leads)

See `docs/ops/pipeline_tracker.csv` — seeded with:
1. عبدالله العسيري · Lucidya · CEO (surname affinity priority)
2. Ahmad Al-Zaini · Foodics · CEO ($170M Series C)
3. Nawaf Hariri · Salla · CEO (70K+ merchants distribution)
4. Hisham Al-Falih · Lean Technologies · CEO (API-first B2B)
5. Ibrahim Manna · BRKZ · Founder ($30M debt contech)

All with personalized DMs ready in `launch_content_queue.md`.

---

## 📈 3 Paying Customers/Day — Staged Math

```
Conversion per outbound (conservative):
  0.05 × 0.40 × 0.70 × 0.20 × 0.80 = 0.00224

Required touches for 3 paid/day:
  3 / 0.00224 ≈ 1,340 touches/day
```

| Stage | Goal | Daily Touches | Channels | When |
|-------|------|---------------|----------|------|
| 1 | First customer | 25-50 | Founder-led | Now (Day 1-14) |
| 2 | 3 customers/week | 50-100 | Founder + first partner | Day 15-45 |
| 3 | 1 customer/day | 200-400 | Partners + SDR | Day 45-90 |
| 4 | 3 customers/day | 1,000+ | Full reseller channel | Day 90+ |

---

## 🚦 Next 24 Hours Execution Plan

### When Moyasar activates (Sami's work):
- Sami sends `NEW_MOYASAR_KEY: sk_live_...` OR `NEW_MOYASAR_TEST_KEY: sk_test_...`
- I update Railway env → redeploy → test 1 SAR checkout → verify webhook round-trip
- Mark **REVENUE VERIFIED**

### When Sami sends SENTRY_DSN:
- I add to Railway env via GraphQL → redeploy
- Trigger `/_test_sentry` → verify issue appears in Sentry UI

### When Sami has 10 minutes for UptimeRobot:
- Complete from docs/ops/UPTIME_AND_ALERTS.md — 10 min, then `UPTIME MONITOR ACTIVE`

### Outreach today (Sami):
- Sami opens LinkedIn → sends DM #1 (Abdullah) from launch_content_queue.md
- Updates `docs/ops/pipeline_tracker.csv` row 1 with `sent_at` timestamp
- Schedules Day +2 reminder

### Content (Sami):
- Post 1 (founder launch) → LinkedIn personal account
- Same post → X/Twitter

---

## 📞 Contact Points

- **Backend:** https://web-dealix.up.railway.app
- **Landing:** https://voxc2.github.io/dealix/
- **Demo booking:** https://calendly.com/sami-assiri11/dealix-demo
- **GitHub:** https://github.com/VoXc2/dealix
- **Pipeline tracker:** `docs/ops/pipeline_tracker.csv`
- **Content queue:** `docs/ops/launch_content_queue.md`

---

## ⚡ Final Executive Decision

**State:** LAUNCHED (technical) — blocked on Moyasar activation for REVENUE VERIFIED.

- Launch target A (LAUNCHED): ✅ REACHED
- Launch target B (REVENUE READY): 🔴 Blocked on Moyasar account activation
- Launch target C (REVENUE VERIFIED): ❌ Depends on B
- Launch target D (ACQUISITION STARTED): 🟡 Ready — waiting only on Sami's first send
- Launch target E (COMPANY OPERATING): 🟡 Pipeline + content ready — daily loop documented

**One credential unlock revenue:** Send me `NEW_MOYASAR_KEY` (test or live after activation). Everything downstream I can do.
