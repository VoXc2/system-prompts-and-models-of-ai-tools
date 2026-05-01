# Incident & Rollback Runbook

> What to do when things are on fire. Kept short on purpose — reach for this at 3am, not in a quiet conference room.

---

## 0. Severity ladder

| Level | Definition | Response |
|---|---|---|
| **P0** | Production down, data loss risk, active security incident | All-hands; incident commander within 15 min |
| **P1** | Major feature broken, elevated error rate (>10%), single-customer blocker | On-call owns; update every 30 min |
| **P2** | Degraded performance, minor feature broken | Business-hours triage |
| **P3** | Cosmetic, non-blocking | Backlog |

---

## 1. First 10 minutes (any P0/P1)

1. **Declare.** Post in `#incidents`: severity, symptoms, impact, one incident commander.
2. **Stop the bleeding.** If a recent deploy is suspect → roll back (see §6).
3. **Freeze.** No new deploys to the affected env until green.
4. **Preserve.** Snapshot logs, metrics, traces, DB state before touching anything.
5. **Communicate.** Customer-facing status update if a customer is affected.

---

## 2. Common P0/P1 scenarios

### 2.1 LLM provider outage

**Symptoms**: high 5xx from `core.llm.router`, specific provider in error spike.

**Response**:
1. Check the provider's status page.
2. Verify the router is falling back (`router.usage_summary()["<provider>"]["fallbacks_triggered"]`).
3. If fallback chain is not triggering, force-route by setting env var override and restarting the app.
4. If multiple providers are down, pause the affected pipeline (set a feature flag).

**Prevention**: keep fallback chains healthy; monitor `trust_policy_decisions_total` dropping.

### 2.2 Postgres unavailable

**Symptoms**: `asyncpg.PostgresError`, API returning 5xx from `/api/v1/leads`.

**Response**:
1. Check DB container / managed service status.
2. Check connection pool saturation (`db.session._engine().pool.status()`).
3. If the DB is healthy, restart the app (pool may be stale after a failover).
4. If the DB is down, surface a 503 from the app and queue inbound webhooks for replay.

### 2.3 HubSpot 429 (rate limit)

**Symptoms**: `crm_sync_failed` warnings spiking; deals not landing in HubSpot.

**Response**:
1. The CRMAgent already retries with exponential backoff. Confirm retries are firing.
2. If sustained, reduce concurrent sync rate via app config.
3. File a HubSpot rate-limit-raise request if regular.

### 2.4 WhatsApp webhook signature failures

**Symptoms**: `whatsapp_invalid_signature` warnings; inbound leads not processed.

**Response**:
1. Verify `WHATSAPP_APP_SECRET` matches the Meta app dashboard.
2. Check for clock skew on the server.
3. If signature verification is misconfigured but source is trusted, temporarily disable the check (config flag) and re-enable after fix.

### 2.5 Suspected secret leak

**Symptoms**: gitleaks alert, unusual API activity, provider notifying you.

**Response**:
1. **Immediately** rotate the affected key in the provider dashboard.
2. Update `.env` / secrets manager with the new key.
3. Redeploy.
4. `gitleaks detect --source . --log-level debug` against the full history.
5. If the leak was in a pushed commit: force-push a history rewrite IF the repo is private and team coordination allows. If public, the assumption is leaked — rotation is the only remedy.
6. File a SECURITY.md report.

### 2.6 Approval Center stuck

**Symptoms**: `trust_approval_lag_seconds` climbing; approvals not flowing.

**Response**:
1. Check notifier health (email/Slack/WhatsApp delivery).
2. `POST /api/v1/trust/approvals/check-timeouts` (or run `ApprovalCenter.check_timeouts()`).
3. If the queue has grown large, temporarily raise the TTL and process backlog manually.

### 2.7 Tool verification contradictions spiking

**Symptoms**: `trust_tool_contradictions_total{tool=<name>}` rising.

**Response**:
1. Inspect `ToolVerificationLedger.contradictions()`.
2. If the intended action format changed (e.g. prompt drift), revert the prompt or fix the schema.
3. If a tool is actually misbehaving, disable the agent that uses it (feature flag).

---

## 3. Data incidents

### Breach response (personal data)

Per PDPL:
1. Contain: revoke access, rotate keys.
2. Assess scope: which entities, which data classes.
3. Notify SDAIA within 72 hours (PDPL requirement for qualifying breaches).
4. Notify affected data subjects if required by risk assessment.
5. Document: root cause, timeline, remediation.

See `compliance_saudi.yaml` for the full PDPL workflow and DPO contact.

---

## 4. Incident roles

- **Incident Commander (IC)** — drives the response; doesn't debug.
- **Ops Lead** — mitigates, deploys, rolls back.
- **Comms Lead** — customer status, internal updates.
- **Scribe** — timeline notes in the incident channel.

For small incidents, one person can hold multiple roles.

---

## 5. Post-incident

Within 3 business days:
- Blameless post-mortem document in `docs/incidents/YYYY-MM-DD-<slug>.md`.
- Timeline, root cause, contributing factors, what worked, what didn't, action items.
- Review in next architecture meeting; close out action items.

---

## 6. Rollback procedures

### 6.1 Application rollback

```bash
# Find previous tag
gh release list

# Pull and restart
docker compose pull ghcr.io/ORG/ai-company-saudi:v<prev>
docker compose up -d

# Verify
curl -fv https://api.ai-company.sa/health
```

### 6.2 DB migration rollback

```bash
# Downgrade one revision
alembic downgrade -1

# Or to a specific revision
alembic downgrade <revision_id>
```

Rollback window: 24h free of blame. After 24h, prefer fix-forward unless severity demands.

### 6.3 Feature flag rollback

If the problematic change is behind a flag, disable the flag first; no deploy needed.

---

## 7. Pre-incident hygiene (preventive)

- Healthchecks on every environment (`/health`) monitored every 30s
- Error rate alerts at >1% for 5 minutes
- Latency p95 alerts at >10s for 5 minutes
- LLM fallback rate alerts at >20% for 10 minutes
- Weekly restore-test on the DB backups
- Monthly game day: simulate an LLM outage + a DB failover

---

## 8. Who to page

| Condition | Who |
|---|---|
| App down / 5xx storm | On-call platform |
| DB down | On-call platform + DBA (if staffed) |
| Security incident | Security lead + DPO |
| Customer-facing issue | On-call platform + Customer Success |
| LLM cost spike | On-call platform + CTO |
| PDPL breach candidate | DPO + Legal + Security |

Concrete names, phones, escalation chain: `dealix/masters/oncall.md` (per deployment — NOT committed publicly).
