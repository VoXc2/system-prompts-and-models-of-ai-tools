# Dealix Operational Runbook

**Version:** 1.0.0  
**Last updated:** 2026-04-23  
**Owner:** Ops Lead

---

## Scenario 1: Service Down (API not responding)

**Detection:** UptimeRobot alert on `api.dealix.me/health` or Sentry alert spike.

**Steps:**

1. SSH to server: `ssh dealix_deploy@188.245.55.180`
2. Check systemd status: `sudo systemctl status dealix-api`
3. Check logs: `sudo journalctl -u dealix-api --since '10 min ago' -n 100`
4. If crashed: `sudo systemctl restart dealix-api`
5. Verify: `curl http://localhost:8001/health`
6. If still failing, check port conflict: `sudo ss -tlnp | grep 8001`
7. Check disk space: `df -h` (full disk = crash)
8. Check memory: `free -h` (OOM killer may have killed uvicorn)
9. If persistent: rollback to previous version (see Scenario 5)

**Recovery time target:** < 5 minutes  
**Escalation:** If not resolved in 15 minutes, escalate to founder.

---

## Scenario 2: Database Down (Postgres unreachable)

**Detection:** `/health/deep` returns `postgres: failed` or Sentry DB connection errors.

**Steps:**

1. Check Postgres status: `sudo systemctl status postgresql`
2. If stopped: `sudo systemctl start postgresql`
3. Check Postgres logs: `sudo journalctl -u postgresql --since '10 min ago'`
4. Check connections: `sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"`
5. If max connections hit: `sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle' AND query_start < now() - interval '30 min';"`
6. Check disk: `df -h /var/lib/postgresql`
7. If data corruption: restore from backup (see Scenario 4)
8. Verify: `curl http://localhost:8001/health/deep | python3 -m json.tool`

**Recovery time target:** < 10 minutes  
**Last backup location:** `/var/backups/dealix/` (daily cron)

---

## Scenario 3: LLM Provider Down (Groq/OpenAI)

**Detection:** `/health/deep` shows LLM provider failures, or Sentry errors on `/api/v1/ai-agents/*`.

**Steps:**

1. Check which provider: `curl http://localhost:8001/health/deep | python3 -m json.tool`
2. If Groq down: system should auto-fallback to OpenAI (check `LLM_FALLBACK_PROVIDER` in `.env`)
3. Verify fallback: `curl -X POST http://localhost:8001/api/v1/ai-agents/test-prompt`
4. If both down: check API keys validity
5. Check provider status pages:
   - Groq: `https://status.groq.com`
   - OpenAI: `https://status.openai.com`
6. If keys expired: rotate keys in `.env`, restart: `sudo systemctl restart dealix-api`

**Impact:** AI features degraded but core CRUD/lead management continues working.  
**Recovery time target:** Automatic (fallback). Manual intervention only if both providers fail.

---

## Scenario 4: Database Restore from Backup

**When:** Data corruption, accidental deletion, or disaster recovery.

**Steps:**

1. Stop the API: `sudo systemctl stop dealix-api`
2. List available backups: `ls -lt /var/backups/dealix/*.sql.gz`
3. Create safety snapshot of current state: `sudo -u postgres pg_dump dealix | gzip > /tmp/dealix_pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz`
4. Drop and recreate database:
   ```
   sudo -u postgres psql -c "DROP DATABASE dealix;"
   sudo -u postgres psql -c "CREATE DATABASE dealix OWNER dealix;"
   ```
5. Restore: `gunzip -c /var/backups/dealix/LATEST.sql.gz | sudo -u postgres psql dealix`
6. Verify row counts: `sudo -u postgres psql dealix -c "SELECT 'leads', count(*) FROM leads UNION ALL SELECT 'deals', count(*) FROM deals;"`
7. Start API: `sudo systemctl start dealix-api`
8. Verify health: `curl http://localhost:8001/health/deep`
9. Check integrity: manually verify recent leads/deals in dashboard

**Recovery time target:** < 15 minutes (tested)  
**RPO:** 24 hours (daily backup)  
**RTO:** 15 minutes

---

## Scenario 5: Rollback to Previous Version

**When:** Bad deploy, broken feature in production.

**Steps:**

1. Identify last working version: `git log --oneline -10`
2. Check current tag: `git describe --tags --always`
3. Checkout previous version: `git checkout v3.0.0` (or specific commit)
4. Install deps: `pip install -r requirements.txt`
5. Restart: `sudo systemctl restart dealix-api`
6. Verify: `curl http://localhost:8001/health`
7. If rolling back a migration: check `alembic history` and downgrade if needed
8. Notify team of rollback reason

**Recovery time target:** < 5 minutes  
**Note:** Never force-push or delete the broken commit. Create a revert commit instead for traceability.

---

## Quick Reference

| Check | Command |
|---|---|
| API health | `curl http://localhost:8001/health` |
| Deep health | `curl http://localhost:8001/health/deep` |
| Service status | `sudo systemctl status dealix-api` |
| Recent logs | `sudo journalctl -u dealix-api -n 50 --no-pager` |
| Postgres status | `sudo systemctl status postgresql` |
| Redis status | `redis-cli ping` |
| Disk space | `df -h` |
| Memory | `free -h` |
| DLQ depth | `curl http://localhost:8001/api/v1/admin/dlq/queues` |
| Circuit breakers | `curl http://localhost:8001/api/v1/admin/circuit-breakers` |
| Restart API | `sudo systemctl restart dealix-api` |
| Backup now | `sudo -u postgres pg_dump dealix \| gzip > /var/backups/dealix/manual_$(date +%Y%m%d).sql.gz` |
