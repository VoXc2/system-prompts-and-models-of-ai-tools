# Dealix — Launch Gaps Closure Plan
> P0 closure guide with real code/config, owner, DoD, verification.

## Gap #1 — CI Black formatter failure
- **Status**: ✅ Fixed in this PR (5 files reformatted)
- **DoD**: `gh run list --branch main --status success` shows latest CI green
- **Verify**: `black --check .` → "All done"
- **Owner**: Dealix agent (automated)

## Gap #2 — Alerts aren't wired to a real channel
- **Problem**: Sentry DSN configured, but no Slack/email routing → silent errors
- **Fix**: Add `SENTRY_SLACK_WEBHOOK_URL` to Railway env + Sentry Alert Rule
- **Steps**:
  1. Create Slack app → incoming webhook
  2. Sentry → Settings → Integrations → Slack → paste webhook
  3. Sentry → Alerts → Create Alert → "issue is first seen" → route to #dealix-alerts
  4. Test: `curl https://<domain>/api/_test_error` (add temp route)
- **DoD**: deliberate error reaches Slack within 60 seconds
- **Owner**: Sami (manual, ~15 min)

## Gap #3 — UptimeRobot on /healthz
- **Setup**:
  1. uptimerobot.com → Add monitor → HTTP(s) → https://<domain>/healthz
  2. 5-minute interval
  3. Alert contacts: Sami email + WhatsApp
- **DoD**: monitor shows "up" + test down by stopping Railway → alert fires
- **Owner**: Sami (manual, ~10 min)

## Gap #4 — 1 SAR payment E2E not yet run
- **Why this matters**: Everything else is theoretical until a real payment flows
- **Steps**:
  1. Verify Moyasar secret rotated (urgent manual step)
  2. Create a test invoice: `python -c "import asyncio; from dealix.payments.moyasar import MoyasarClient; c = MoyasarClient(); print(asyncio.run(c.create_invoice(amount=100, currency='SAR', description='Test', callback_url='https://dealix.sa/payment/callback')))"`
  3. Pay 1 SAR via returned invoice URL
  4. Confirm webhook received: `tail -f /var/log/dealix/webhooks.log`
  5. Confirm lead status updated in DB: `SELECT * FROM leads WHERE status='paid' LIMIT 1`
- **DoD**: Invoice URL → payment → webhook → DB row updated — all 4 steps green
- **Owner**: Sami (manual, ~20 min)

## Gap #5 — Marketers/Pricing/Partners not on landing domain
- **Fix**: This PR uploads 3 HTML files into `landing/` directory
- **DoD**: curl returns 200 for all 3 URLs after deploy
- **Owner**: Dealix agent (automated in this PR) + Sami (verify after Railway deploys)

## Gap #6 — PostHog events not fired from landing
- **Fix**: PostHog snippet injected into marketers/pricing/partners pages (this PR)
- **TODO for Sami**: Set `POSTHOG_KEY` as `window.POSTHOG_KEY` in `landing/index.html` inline script
- **DoD**: Open PostHog → Live events → see `marketers_viewed`, `pricing_viewed`, `partners_viewed`

## Gap #7 — Moyasar webhook secret rotation
- **Status**: ❌ Not done (in git history forever; need rotation)
- **Steps**:
  1. dashboard.moyasar.com → Webhooks → Rotate secret
  2. Copy new secret
  3. Railway → env → `MOYASAR_WEBHOOK_SECRET` → paste
  4. Redeploy
  5. Test webhook with new secret
- **DoD**: old secret fails signature check, new secret passes
- **Owner**: Sami (manual, ~5 min)

## Gap #8 — Calendly webhook → CRM sync
- **Current**: Calendly link exists; no webhook handler
- **Fix**: Add route `/api/webhooks/calendly` — done in separate PR (P1, not blocker)
- **DoD**: booking on calendly → lead.stage=demo_booked in DB
- **Owner**: Dealix agent (P1, next sprint)

## Gap #9 — Backup & restore drill
- **Current**: Railway auto-backups exist; never restored
- **Fix**:
  1. Create `docs/runbooks/restore_drill.md`
  2. Monthly: restore latest backup to a staging env
  3. Log result in `docs/runbooks/drill_log.md`
- **DoD**: first drill completed + documented
- **Owner**: Sami (P1, within 7 days)

## Gap #10 — No paying customer
- **Fix**: Execute outreach plan in `dealix_multi_stakeholder_outreach.md`
- **DoD**: ≥1 paid pilot (even 1 SAR) in 14 days
- **Owner**: Sami (ongoing)
