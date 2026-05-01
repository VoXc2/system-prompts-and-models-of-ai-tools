# Dealix On-Call / Incident Contact

**Effective:** 2026-04-23
**Review:** after first paid deal (G5) — then set up a real rotation if >1 engineer

---

## Primary contact

- **Name:** Sami Assiri
- **Email:** sami.assiri11@gmail.com
- **Role:** Founder / sole maintainer
- **Timezone:** Asia/Riyadh (UTC+3)
- **Availability:** 24/7 during Primitive Launch phase (first 14 days)

Until there's a second engineer or a paid on-call service, **Sami is the
escalation path**. This is a conscious trade-off — it's cheaper than a
pager rotation until we have revenue.

## Secondary (automated)

- **Agent:** Perplexity agent with GitHub connector (`api_credentials=["github"]`)
  - Can: read repo state, open PRs, merge PRs with admin override, read
    GitHub-side CI logs
  - Cannot: SSH to prod, read `.env` values, run k6/drills on the server
  - Contact method: via existing Perplexity chat thread

## Escalation decision tree

```
incident
  ├─ can I see it in /health/deep ?
  │   ├─ yes + 5xx → page Sami immediately
  │   └─ no        → check /admin/dlq/stats, /admin/approvals/stats
  ├─ is revenue path affected (/checkout, /webhooks/moyasar) ?
  │   ├─ yes       → page Sami + open GitHub issue with label `P0`
  │   └─ no        → file GitHub issue with label `P1`, handle next business day
  └─ is it a security incident (suspected compromise) ?
      └─ yes       → follow RUNBOOK.md Scenario 6; rotate secrets; email Sami
```

## Channels

| Channel | Use for | Target response time |
|---|---|---|
| Email (sami.assiri11@gmail.com) | Everything | <4h business hours |
| GitHub issue with `P0` label | Incidents with repo evidence | Same as email |
| Perplexity agent chat | Automated daily briefs + follow-ups | Next scheduled run |

**To be added (blocked on credentials):**
- [ ] WhatsApp Business number — **blocker: need number from Sami**
- [ ] UptimeRobot status page → automated alerts — **blocker: UptimeRobot API key**
- [ ] Slack webhook for DLQ alerts — **blocker: Slack workspace + webhook URL**

---

## What closes I2

This document merged to `docs/ON_CALL.md` → **closed ✅** (you're looking at it)

I3 (public status page) remains blocked on the UptimeRobot key.

---

## Incident response checklist (first 15 minutes)

1. **Acknowledge** — reply to the alert, even just "on it"
2. **Assess** — one `/health/deep` curl + one `/admin/dlq/stats` curl
3. **Decide** — fix forward OR roll back (see RUNBOOK Scenario 2)
4. **Communicate** — if customer-visible, prepare a one-line status update
5. **Execute** — run the appropriate RUNBOOK scenario
6. **Verify** — re-check `/health/deep` and the specific endpoint that failed
7. **Document** — file the incident in `docs/incidents/YYYY-MM-DD-<slug>.md`

Post-mortem is required for any P0 incident within 48 hours.
