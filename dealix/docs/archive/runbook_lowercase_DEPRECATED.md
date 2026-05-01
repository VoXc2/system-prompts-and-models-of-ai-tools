# Dealix Production Runbook

**Version:** 1.0 (v3.0.0 Primitive Launch)
**Owner:** Sami Assiri
**Last updated:** 2026-04-23
**Environment:** Production — `api.dealix.me`, `188.245.55.180`

---

## 0. Contact & Access

- **Server:** `ssh -o StrictHostKeyChecking=no -i ~/.ssh/dealix_deploy root@188.245.55.180`
- **App dir:** `/opt/dealix`
- **systemd unit:** `dealix-api.service`
- **Database:** Postgres `postgresql://dealix@127.0.0.1:5432/dealix`
- **Cache/queue:** Redis `127.0.0.1:6379/0`
- **Nginx:** `api.dealix.me` → `127.0.0.1:8001`, `dealix.me` → `/var/www/dealix/landing`
- **GitHub:** https://github.com/VoXc2/dealix (main protected, `gh` CLI with `api_credentials=["github"]`)
- **Sentry:** DSN in `/opt/dealix/.env` → `SENTRY_DSN`
- **UptimeRobot:** monitors `https://api.dealix.me/health`
- **PostHog:** EU region `https://eu.i.posthog.com`

### First rule
**Never edit code or `.env` directly on the server.** All changes flow through GitHub PR → deploy script. Untracked production drift already cost 20 commits once — not again.

---

## Scenario 1 — Routine Deploy (merge to main → prod)

**When:** PR approved and merged to `main`.

1. **Verify CI green on main**
   ```bash
   gh run list --repo VoXc2/dealix --branch main --limit 3 --json name,status,conclusion
   ```
   All three latest must be `completed / success`. If not — **abort**.

2. **SSH to server**
   ```bash
   ssh -o StrictHostKeyChecking=no -i ~/.ssh/dealix_deploy root@188.245.55.180
   ```

3. **Snapshot current state (rollback safety)**
   ```bash
   cd /opt/dealix
   git rev-parse HEAD > /opt/dealix/.last_good_sha
   cp .env .env.bak.$(date -u +%Y%m%dT%H%M%SZ)
   ```

4. **Pull + install + migrate**
   ```bash
   git fetch origin
   git checkout main
   git pull --ff-only origin main
   /opt/dealix/.venv/bin/pip install -r requirements.txt
   /opt/dealix/.venv/bin/alembic upgrade head
   ```

5. **Restart service**
   ```bash
   systemctl restart dealix-api
   systemctl status dealix-api --no-pager
   ```

6. **Health verification (all must pass)**
   ```bash
   curl -sf https://api.dealix.me/health
   curl -sf https://api.dealix.me/health/deep | jq .
   curl -sf https://api.dealix.me/api/v1/pricing/plans | jq '.plans | length'
   ```
   `/health/deep` must show `postgres`, `redis`, `llm_providers` all green.

7. **Trigger Sentry + PostHog probes**
   ```bash
   curl -sf -H "X-API-Key: $ADMIN_KEY" https://api.dealix.me/api/v1/admin/sentry-check
   ```
   Verify in Sentry + PostHog dashboards within 60s.

**DoD:** Health green, Sentry ping received, no error spike in Sentry for 10 min.

---

## Scenario 2 — Rollback (bad deploy, 5-min target)

**Trigger:** error rate spike in Sentry, `/health/deep` red, 5xx surge, or user complaint post-deploy.

1. **Announce in channel** (if you have one — otherwise note in GitHub issue):
   > Rolling back prod to last good SHA due to <reason>.

2. **SSH in, revert to last known-good SHA**
   ```bash
   ssh -i ~/.ssh/dealix_deploy root@188.245.55.180
   cd /opt/dealix
   LAST_GOOD=$(cat /opt/dealix/.last_good_sha)
   git checkout "$LAST_GOOD"
   /opt/dealix/.venv/bin/pip install -r requirements.txt
   ```

3. **Roll back migrations only if the bad deploy added new ones**
   ```bash
   # Check what the bad deploy added:
   /opt/dealix/.venv/bin/alembic history | head
   # Downgrade one step ONLY if necessary:
   /opt/dealix/.venv/bin/alembic downgrade -1
   ```
   **Rule:** never downgrade more than 1 step without Sami's explicit approval.

4. **Restart + verify**
   ```bash
   systemctl restart dealix-api
   curl -sf https://api.dealix.me/health/deep | jq .
   ```

5. **Re-open main for fix via PR** (no direct commits to main; `main` is protected).

**DoD:** health green on old SHA within 5 minutes, Sentry error rate back to baseline within 10 min.
**Target:** <5 min from decision to rollback complete.

---

## Scenario 3 — Database Down / Unreachable

**Signals:** `/health/deep` reports `postgres: error`, 500s on leads endpoints, Sentry `OperationalError`.

1. **Triage — is it us or the DB?**
   ```bash
   ssh -i ~/.ssh/dealix_deploy root@188.245.55.180
   systemctl status postgresql --no-pager
   sudo -u postgres psql -c "SELECT 1;"
   ```

2. **If systemd says failed:**
   ```bash
   journalctl -u postgresql -n 200 --no-pager
   systemctl restart postgresql
   sleep 3
   sudo -u postgres psql -c "SELECT 1;"
   ```

3. **If disk full** (most common real cause):
   ```bash
   df -h /
   # Clear postgres WAL archives / old backups first:
   du -sh /var/lib/postgresql/* /var/backups/postgres/* 2>/dev/null | sort -h
   # DO NOT delete active WAL. Rotate old backups only.
   ```

4. **If connection pool exhausted** (API is up, DB healthy, but API can't connect):
   ```bash
   sudo -u postgres psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
   systemctl restart dealix-api  # drops API's stale connections
   ```

5. **If DB corrupt / cannot start** → **restore from backup** (Scenario 5).

6. **Post-incident:**
   - Write a 5-line postmortem in `docs/incidents/YYYY-MM-DD.md`.
   - If webhooks arrived during outage, drain `WEBHOOKS_DLQ`:
     ```bash
     curl -s -H "X-API-Key: $ADMIN_KEY" -X POST \
       'https://api.dealix.me/api/v1/admin/dlq/webhooks/drain?limit=100'
     ```

**DoD:** `/health/deep` postgres green; no lost webhooks (DLQ drained or re-queued).

---

## Scenario 4 — LLM Provider Down (Anthropic / OpenAI / Google)

**Signals:** Sentry shows provider timeouts, `/health/deep` `llm_providers` yellow/red, ConnectorFacade circuit breaker open, workflow failures in PostHog.

1. **Confirm it's the provider, not us:**
   - Check https://status.anthropic.com / https://status.openai.com / https://status.cloud.google.com.
   - `curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" ...`

2. **The circuit breaker should already be doing its job** — requests to the failing provider return fast with `CircuitOpenError`, DLQ absorbs the failures.

3. **Verify breaker state:**
   ```bash
   curl -s -H "X-API-Key: $ADMIN_KEY" https://api.dealix.me/api/v1/admin/dlq/stats | jq .
   ```
   If `OUTBOUND_DLQ` or `ENRICHMENT_DLQ` is growing fast, breaker is protecting us — **no action on our side**.

4. **Temporary failover** (if one provider is the primary and down for >30 min):
   Edit `/opt/dealix/.env` → `LLM_PROVIDER_PRIORITY="openai,google,anthropic"` (reorder).
   ```bash
   systemctl restart dealix-api
   ```
   **Rule:** this is the ONLY allowed in-place `.env` edit. Commit the change back to `.env.example` (without secret) next business day.

5. **When provider recovers:**
   - Breaker auto-half-opens after 60s, then closes on first success.
   - Drain the relevant DLQ to replay queued work:
     ```bash
     curl -s -H "X-API-Key: $ADMIN_KEY" -X POST \
       'https://api.dealix.me/api/v1/admin/dlq/outbound/drain?limit=50'
     ```

**DoD:** `/health/deep` llm_providers green; DLQ depth returning to zero; no workflow failures in last 10 min.

---

## Scenario 5 — Backup Restoration (Data Loss / Corruption)

**Trigger:** DB corrupt, accidental mass delete, ransomware, or monthly drill (required).

### Preflight
1. **Identify the target backup:**
   ```bash
   ls -lht /var/backups/postgres/*.sql.gz | head -5
   ```
2. **Never restore into production DB.** Restore into a staging clone first, validate, then swap.

### Drill / Restore procedure (on staging — monthly required)
1. **Create isolated DB:**
   ```bash
   sudo -u postgres createdb dealix_restore_test
   ```
2. **Restore:**
   ```bash
   BACKUP=/var/backups/postgres/dealix-YYYY-MM-DD.sql.gz
   gunzip -c "$BACKUP" | sudo -u postgres psql dealix_restore_test
   ```
3. **Validate row counts against prod (sanity):**
   ```bash
   sudo -u postgres psql dealix_restore_test -c "SELECT 'leads' t, count(*) FROM leads UNION ALL SELECT 'users', count(*) FROM users;"
   ```
4. **Validate latest lead timestamp is within acceptable RPO (≤24h):**
   ```bash
   sudo -u postgres psql dealix_restore_test -c "SELECT max(created_at) FROM leads;"
   ```
5. **Teardown:**
   ```bash
   sudo -u postgres dropdb dealix_restore_test
   ```

### Real incident restore (production data loss)
1. **Stop API to freeze writes:**
   ```bash
   systemctl stop dealix-api
   ```
2. **Rename current DB (do NOT drop — evidence):**
   ```bash
   sudo -u postgres psql -c "ALTER DATABASE dealix RENAME TO dealix_corrupt_$(date +%Y%m%d);"
   sudo -u postgres createdb dealix
   ```
3. **Restore latest good backup:**
   ```bash
   gunzip -c "$BACKUP" | sudo -u postgres psql dealix
   ```
4. **Restart API + verify:**
   ```bash
   systemctl start dealix-api
   curl -sf https://api.dealix.me/health/deep | jq .
   ```
5. **Postmortem mandatory** — how data was lost, why backup gap existed, what changed.

**DoD (drill):** restore completes in ≤15 min, row counts ±5% of prod, max timestamp within RPO.
**DoD (incident):** API back up, no data newer than last backup lost (document gap).

---

## Scenario 6 — Security Incident (suspected breach)

**Signals:** unexplained admin API calls, fail2ban banning authorized IPs, unexpected outbound traffic, Sentry `PermissionError` spike, unknown webhook signatures failing.

1. **Contain first, investigate second:**
   ```bash
   ssh -i ~/.ssh/dealix_deploy root@188.245.55.180
   # Rotate ALL secrets immediately
   cd /opt/dealix && bash scripts/rotate_secrets.sh
   systemctl restart dealix-api
   ```

2. **Lock down UFW to known IPs only** (temporary):
   ```bash
   # Save current rules first:
   ufw status numbered > /tmp/ufw.before.$(date +%s)
   # Restrict SSH to your IP:
   ufw delete allow 22/tcp || true
   ufw allow from <YOUR_PUBLIC_IP> to any port 22
   ```

3. **Check auth logs:**
   ```bash
   journalctl -u ssh -n 500 --no-pager | grep -iE 'accepted|failed'
   fail2ban-client status sshd
   ```

4. **Preserve evidence:**
   ```bash
   tar -czf /root/incident-$(date +%s).tgz /var/log/nginx /var/log/auth.log /var/log/dealix*
   ```

5. **Notify Sami, document in `docs/incidents/`, file GitHub security advisory if user data touched.**

**DoD:** all secrets rotated, UFW locked, attacker IPs banned, incident doc drafted within 1h.

---

## Appendix A — Health Check Cheat Sheet

| Signal | Command | Expected |
|---|---|---|
| Liveness | `curl -sf https://api.dealix.me/health` | 200 OK |
| Deep health | `curl -sf https://api.dealix.me/health/deep` | postgres+redis+llm_providers green |
| CI status | `gh run list --repo VoXc2/dealix --limit 3` | success |
| DLQ depth | `GET /api/v1/admin/dlq/stats` | 0 across all queues |
| Pending approvals | `GET /api/v1/admin/approvals/pending` | <10 |
| Service status | `systemctl status dealix-api` | active (running) |
| fail2ban | `fail2ban-client status sshd` | jail active |
| Nginx | `systemctl status nginx` | active (running) |

## Appendix B — Do-Not-Touch List

- `main` branch: protected, no direct push
- `/opt/dealix/.env.pre-v3.0.0.bak`: emergency reference, never delete
- `server-backup-20260423-084442` branch: historical evidence, do not force-delete
- Postgres `dealix_corrupt_*` dbs: keep for 7 days post-incident before dropping

## Appendix C — Runbook Review

Review every 4 weeks. If any command in this runbook failed during a real incident, update it **immediately** after that incident closes.
