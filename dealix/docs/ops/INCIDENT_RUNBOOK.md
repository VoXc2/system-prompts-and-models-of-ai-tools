# 🚨 Dealix — Incident Runbook

**Use when production breaks.**
**Goal:** Restore service + communicate + learn.

---

## Severity Levels

| Level | Definition | Response Time | Communication |
|-------|-----------|---------------|---------------|
| **SEV-1** | Full outage, no customers can use service | < 15 min | Immediate Slack + email customers |
| **SEV-2** | Major feature broken, most customers affected | < 1 hour | Slack alert, status page update |
| **SEV-3** | Minor bug, one customer affected | < 4 hours | Individual customer comms |
| **SEV-4** | Cosmetic, not user-blocking | < 24 hours | Ticket only |

---

## SEV-1 Response (Full Outage)

### Within 5 minutes
1. Confirm: Open `/healthz` in browser. If 5xx or timeout → SEV-1.
2. Check Railway dashboard → service status
3. Check UptimeRobot → when did it start?

### Within 15 minutes
1. **Diagnose:**
   - Last deploy in Railway?
   - Recent PR merged?
   - DB connection?
   - Moyasar API outage?
2. **Mitigate:**
   - Roll back last deploy if caused by recent change
   - Restart service in Railway
   - Check env vars

### Communicate
Post to customers (if any active):
```
نواجه مشكلة فنية مؤقتة في النظام. الفريق يعمل على حلها.
سنحدثكم خلال 30 دقيقة.
— فريق Dealix
```

### After Resolution (within 48h)
Write post-mortem:
1. Timeline
2. Root cause
3. What worked
4. What didn't
5. Action items to prevent recurrence

---

## Common Issues + Fixes

### Issue: `/api/v1/*` returns 404
**Likely cause:** Deploy failed or wrong Start Command.
**Fix:**
1. Railway → Deployments → check latest deploy status
2. If failed: check logs, fix, redeploy
3. If succeeded but still 404: Settings → Start Command = `/app/start.sh`

### Issue: Moyasar webhook returns 401
**Likely cause:** Secret mismatch.
**Fix:**
1. Railway → Variables → `MOYASAR_WEBHOOK_SECRET`
2. Moyasar Dashboard → Webhooks → same secret
3. Must be identical string

### Issue: Database connection refused
**Likely cause:** DATABASE_URL wrong or Postgres add-on down.
**Fix:**
1. Railway → PostgreSQL service → check status
2. Copy connection string
3. Update env var
4. Redeploy

### Issue: High error rate in Sentry
**Likely cause:** New deploy or traffic spike.
**Fix:**
1. Check last deploy diff
2. If unrelated: scale Railway resources
3. If related: roll back

---

## Rollback Procedure

### Railway Rollback (2 minutes)
1. Railway → Deployments
2. Find previous successful deployment
3. Click `...` → Redeploy
4. Wait for `Active` status
5. Verify `/healthz` = 200

### Git Revert (if code caused)
```bash
git checkout main
git revert <bad-commit-sha>
git push origin main
# CI runs, deploy triggered automatically
```

---

## Who to Contact

| Issue | Contact |
|-------|---------|
| Backend down | Sami (founder, on-call 24/7) |
| Payment processing | Moyasar support |
| Domain DNS | Domain registrar |
| Hosting | Railway support |

---

## Monitoring Setup Check

Run monthly:
- [ ] Sentry alerts still firing? (trigger test error)
- [ ] UptimeRobot still polling? (check dashboard)
- [ ] Slack channel `#dealix-alerts` active?
- [ ] Emergency phone numbers current?

---

## Learning from Incidents

Every SEV-1 or SEV-2 requires:
1. Post-mortem within 48 hours
2. File in `docs/ops/postmortems/YYYY-MM-DD-summary.md`
3. Review in weekly team sync (even solo)
4. Update this runbook if new pattern
