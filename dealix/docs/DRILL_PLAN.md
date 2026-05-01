# Dealix Launch Drills — Execution Plan

**Purpose:** concrete commands to execute T5, T6, T7, T8 drills from `LAUNCH_GATES.md`.

All drills are designed to be **runnable by Sami on the prod server** with minimal agent hand-holding. Each has a clear pass/fail signal.

---

## Preflight (once, on prod server)

```bash
# Ensure scripts are executable and up to date
cd /opt/dealix
git pull origin main
chmod +x scripts/ops/*.sh

# Verify current state
git rev-parse --short HEAD                       # should be latest main
cat /opt/dealix/.last_good_sha                   # should be ce0027e or newer good commit
systemctl is-active dealix-api                   # should be: active
curl -s http://127.0.0.1:8001/health/deep | jq . # should show postgres + redis + llm green
```

---

## T5 — DLQ fault-injection (full closure)

**Status:** 🟡 primitives live, E2E untested
**Target:** prove a malformed webhook lands in `WEBHOOKS_DLQ`

```bash
# From any machine with an API key (recommended: the prod server itself)
export API_KEY="$(grep '^API_KEYS=' /opt/dealix/.env | cut -d= -f2- | tr -d '"' | cut -d, -f1)"
export API_BASE="http://127.0.0.1:8001"

bash /opt/dealix/scripts/ops/dlq_fault_injection.sh
```

**Pass criteria:**
- Baseline `webhooks` depth is `N`
- After injection, depth is `N+1`
- `/admin/dlq/webhooks/peek` returns the injected event

**Cleanup:**
```bash
curl -X POST -H "X-API-Key: $API_KEY" "$API_BASE/api/v1/admin/dlq/webhooks/drain"
```

---

## T6 — k6 load test against prod

**Status:** 🔴 not run
**Target:** 100 VU, p95 <2s, failure <2% (thresholds baked into `k6_smoke.js`)

### Install k6 (once)

```bash
sudo gpg --no-default-keyring \
  --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 \
  --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install -y k6
```

### Run

```bash
sudo bash /opt/dealix/scripts/ops/run_k6_prod.sh
```

**Pass criteria:** k6 exits 0 (both thresholds green). Summary JSON saved to `/var/log/dealix_k6/`.

**If it fails:**
- Check `http_req_duration` breakdown — identify which endpoint breached p95
- Likely culprits: `/health/deep` (Postgres slow), `/api/v1/pricing/plans` (pure Python, should be fast)
- Re-run at 50 VU to confirm it's load-related not environmental

---

## T7 — Rollback drill

**Status:** 🔴 not drilled
**Target:** prove rollback works end-to-end in <5 minutes

### Step A: dry run (safe, always)

```bash
sudo bash /opt/dealix/scripts/ops/rollback_drill.sh --dry-run
```

Review the log. Confirm `.last_good_sha` points to a real earlier commit (not HEAD).

### Step B: real drill (only on staging OR a maintenance window)

```bash
# Only run on prod during a planned maintenance window with no active traffic
sudo CONFIRM=YES bash /opt/dealix/scripts/ops/rollback_drill.sh --real
```

**Pass criteria:**
- Script exits 0
- Elapsed time <300s (5 minutes)
- `/health/deep` returns 200 after rollback
- Log file at `/var/log/dealix_rollback_drill.<ts>.log`

**After drill:** roll forward immediately by:
```bash
cd /opt/dealix
git fetch origin && git reset --hard origin/main
.venv/bin/pip install -q -r requirements.txt
systemctl restart dealix-api
```

---

## T8 — Backup restore drill (staging required)

**Status:** 🔴 not drilled — follow RUNBOOK Scenario 5
**Target:** restore production DB dump into staging DB, verify row counts

### Prerequisites (blocked on staging infra)

1. Staging server with Postgres matching prod version
2. Recent `pg_dump` from prod (should run daily via cron; verify with `ls -lt /opt/dealix/backups/`)
3. SSH access to staging

### Procedure (summary — full detail in RUNBOOK.md)

```bash
# On staging server, as root
LATEST_DUMP=$(ls -1t /opt/dealix/backups/*.sql.gz | head -1)

# Pre-check row counts on staging (if it has prior data)
psql -U dealix -d dealix -c "SELECT COUNT(*) FROM leads;"

# Restore
gunzip -c "$LATEST_DUMP" | psql -U dealix -d dealix_restore_test

# Post-check row counts — must be non-zero and match production
psql -U dealix -d dealix_restore_test -c "SELECT COUNT(*) FROM leads;"
psql -U dealix -d dealix_restore_test -c "SELECT COUNT(*) FROM deals;"
```

**Pass criteria:** row counts for critical tables (`leads`, `deals`, `events`) are non-zero and within 1% of production counts at dump time.

**Current blocker:** no staging environment provisioned. Options:
1. Spin up a second Hetzner VPS as staging (cost: ~€5/mo) — recommended
2. Use a local Docker Postgres + local restore — acceptable for drill but not ongoing
3. Skip until G5 (first paid deal) — risky, contradicts launch gates philosophy

---

## Drill cadence (post-launch)

| Drill | Frequency | Owner |
|---|---|---|
| T5 DLQ fault-injection | Monthly | Sami or on-call |
| T6 k6 | Weekly for first month, then monthly | Sami |
| T7 rollback dry-run | Monthly | Sami |
| T7 rollback real | Quarterly (or after major deploy) | Sami |
| T8 backup restore | Monthly | Sami |

All drills should be logged in `docs/incidents/YYYY-MM-DD-drill-<name>.md` with the log file path and outcome.
