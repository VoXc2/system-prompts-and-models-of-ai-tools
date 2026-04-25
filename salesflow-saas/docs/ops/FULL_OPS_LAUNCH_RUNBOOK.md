# Dealix — Full Ops Launch Runbook

**Version:** 1.0.0
**Date:** 2026-04-25

---

## Launch Status

| System | Status | Evidence |
|--------|--------|---------|
| Backend (Railway) | LIVE | healthz=200, pricing=200, route/message/enrich=200 |
| Landing (dealix.me) | LIVE | Returns 200 |
| Frontend (Next.js) | DEPLOYED | Marketers page rewritten as sales page |
| Manual Payment | READY | Bank transfer + STC Pay documented |
| Automated Payment | BLOCKED | Moyasar returns 502 |
| Outreach Templates | READY | 5 messages + 60 targets + automation endpoints |
| Customer Onboarding | READY | Pilot template + success playbook |
| Monitoring | PARTIAL | GitHub Actions healthcheck; Sentry not configured |

## What Is Live
- `/healthz` → 200
- `/api/v1/pricing/plans` → 3 plans in SAR
- `/api/v1/prospect/route` → rules-based lead classification
- `/api/v1/prospect/message` → Arabic message generation
- `/api/v1/prospect/enrich-tech` → real tech stack detection
- `/api/v1/automation/email/generate` → personalized email + follow-ups
- `/api/v1/automation/compliance/check` → compliance gate
- `/api/v1/automation/reply/classify` → 12-category reply handler
- `dealix.me` → landing page
- `trial-signup.html` → lead capture form

## What Is Not Live
- LLM personalization (needs GROQ_API_KEY)
- Web discovery (needs GOOGLE_SEARCH_API_KEY)
- PostHog funnel tracking (needs POSTHOG_API_KEY)
- Sentry error alerting (needs SENTRY_DSN)
- Moyasar automated checkout (returns 502)
- HubSpot CRM sync (needs HUBSPOT_API_KEY)
- Gmail automated send (needs OAuth setup)

## Manual Blockers (Sami-Only)

| Blocker | Action | Time | Priority |
|---------|--------|------|----------|
| GROQ_API_KEY | Add in Railway env Dealix/web | 3 min | P0 |
| GOOGLE_SEARCH_API_KEY + CX | Add in Railway | 5 min | P0 |
| SENTRY_DSN | Add in Railway | 3 min | P0 |
| POSTHOG_API_KEY + HOST | Add in Railway | 3 min | P0 |
| Send first 5 messages | WhatsApp + LinkedIn | 30 min | P0 |
| Book first demo | Calendly | Depends on replies | P0 |
| Test Moyasar key | curl from terminal | 5 min | P1 |
| Rollback drill | SSH to Hetzner Console | 15 min | P1 |
| DB restore drill | SSH to Hetzner Console | 15 min | P1 |

---

## Daily Checklist (until first 3 paid clients)

### Morning (08:00)
- [ ] Check Railway healthz → 200?
- [ ] Check Sentry for overnight errors (if configured)
- [ ] Review replies from yesterday
- [ ] Classify replies (use /api/v1/automation/reply/classify)
- [ ] Select today's 5-10 outreach targets

### Midday (12:00)
- [ ] Send 5 outreach messages (WhatsApp warm + LinkedIn)
- [ ] Follow up on Day +2 / +5 leads
- [ ] Respond to all positive replies within 2 hours
- [ ] Book demos for interested prospects

### Afternoon (16:00)
- [ ] Run demos (if scheduled)
- [ ] Send pilot offers to demo'd prospects
- [ ] Publish 1 LinkedIn/X post

### Evening (20:00)
- [ ] Update lead tracker
- [ ] Count: sent / replied / demo'd / offered / paid
- [ ] Plan tomorrow's targets
- [ ] Handle late replies

---

## Payment Test Checklist (for Sami)

### Manual Payment Test
1. Ask a friend to transfer 1 SAR via bank or STC Pay
2. Verify receipt in bank app
3. Mark test as passed
4. This is your production payment path until Moyasar works

### Moyasar Diagnostic
1. Open [dashboard.moyasar.com](https://dashboard.moyasar.com)
2. Check Account Status (Active? Pending? Suspended?)
3. Check API Keys → is `sk_live_` the current key?
4. Test from terminal:
   ```
   curl -u "sk_live_YOUR_KEY:" https://api.moyasar.com/v1/invoices \
     -d "amount=100" -d "currency=SAR"
   ```
5. If "authentication_error" → key mismatch, regenerate
6. If "account_inactive" → complete KYC
7. If success → Railway env has whitespace, re-paste carefully

---

## Outreach Checklist
- [ ] 5 warm WhatsApp messages sent (from FIRST_5_OUTREACH.md)
- [ ] 1 LinkedIn founder post published
- [ ] 1 LinkedIn DM to agency partner
- [ ] All follow-ups current (no lead older than 3 days without follow-up)
- [ ] Tracker updated with today's activity

## Demo Checklist
- [ ] Prospect's website reviewed
- [ ] enrich-tech run on their domain
- [ ] 20-minute demo completed per DEMO_BOOKING_RUNBOOK.md
- [ ] Follow-up sent same day
- [ ] Pilot offer sent if positive

## Rollback Checklist (if something breaks)
1. Railway → Deployments → click previous green deployment → Redeploy
2. If Railway is down: Hetzner Console → `systemctl restart dealix-api`
3. If DB corrupted: restore from Railway Postgres auto-backup
4. If code breaks: `git revert HEAD && git push origin main`

## DB Restore Checklist
1. Railway Postgres has automatic daily backups
2. Railway → Postgres service → Backups → Restore
3. After restore: verify `/api/v1/dashboard/metrics` returns data

## Incident Checklist
1. Check Railway logs → identify error
2. If 502/503: restart deployment
3. If code bug: revert last commit
4. If env issue: check Variables tab
5. If DNS: check GoDaddy/Cloudflare
6. Notify any active pilot clients if downtime > 30 minutes

---

## Do Not Touch List
- Do NOT add new LLM providers
- Do NOT rebuild dashboard
- Do NOT start v3.1
- Do NOT implement Temporal/LangGraph/Qdrant
- Do NOT build voice/webchat/mobile
- Do NOT expand to UAE/Egypt
- Do NOT hire before 3 paid clients
- Do NOT spend on ads before manual outreach proves conversion

---

## Definition of Launch-Ready
All of these must be true:
- [ ] Railway healthz=200
- [ ] 4 env keys added (GROQ, GOOGLE, SENTRY, POSTHOG)
- [ ] 5+ outreach messages sent
- [ ] 1+ demo booked
- [ ] Manual payment path tested (1 SAR friend test)

## Definition of Revenue-Live
All of the above, plus:
- [ ] 1+ pilot payment received (499 SAR)
- [ ] 1+ customer onboarded
- [ ] 1+ daily report sent to customer
