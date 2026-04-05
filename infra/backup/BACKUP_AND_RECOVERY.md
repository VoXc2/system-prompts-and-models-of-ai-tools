# Dealix / SalesFlow — Backup, Disaster Recovery & Deployment Safety

This document describes a **production-grade** backup and recovery architecture for the monorepo under `salesflow-saas/` (PostgreSQL, Redis, uploads, logs, secrets) and **code** in Git.

**Reality check on RTO/RPO:** A **sub-15-minute recovery** for the full stack requires **pre-provisioned** capacity (standby DB, mirrored object storage, automated failover, runbooks exercised). Daily logical dumps alone are **not** sufficient for instant RTO; combine with managed DB PITR, replicas, and blue/green app deploys.

---

## 1. Architecture overview

| Layer | What | Primary | Secondary | RPO hint |
|-------|------|---------|-----------|----------|
| Code | Git commits + branches + tags | GitHub (private) | `git push --mirror` to second remote | Minutes |
| Database | PostgreSQL | Daily `pg_dump -Fc` + optional WAL/PITR | S3 + GCS mirror | 24h (dump) / minutes (WAL) |
| Files | `UPLOAD_DIR` uploads | Tar/zstd to disk → S3 | GCS rsync | 24h |
| Logs | App/nginx logs | Tarball to S3 | GCS | Best-effort |
| Secrets | `.env`, TLS keys | **GPG-encrypted** tarball only | S3/GCS (encrypted blobs) | On change |
| Config | Compose, K8s manifests | Git + encrypted env backup | — | Git |

**Data flow:** Host job runner (cron, systemd timer, or GitHub Actions self-hosted) → local staging dir → **AWS S3** (primary) → **GCS** (secondary mirror via `gsutil rsync`).

Scripts live in `infra/backup/scripts/`. Host env in `/etc/dealix/backup.env` (see `infra/backup/env.example`).

---

## 2. Version control (Git)

- **Branches:** `main` (production), `staging` (pre-prod), `development` (integration). Create with:

  ```bash
  bash infra/backup/scripts/ensure-git-branches.sh
  git push -u origin staging development
  ```

- **No code loss:** GitHub is the source of truth; add a **mirror** remote for vendor/region independence (see `git-mirror-all-branches.sh`).

---

## 3. GitHub setup (manual in GitHub UI)

Create a **private** repository (or keep org private).

**Protected `main`:**

- Settings → Branches → Branch protection rule for `main`
- Require a pull request before merging  
- Require approvals: **≥ 1**  
- Require status checks to pass (e.g. `backend`, `frontend` from `dealix-ci.yml`)  
- Require branches to be up to date before merging  
- Include administrators (optional)  
- Restrict who can push to matching branches  

Repeat for `staging` if releases are cut there.

**Secrets (for Actions backup jobs, if used):**

- `AWS_ROLE_ARN` + OIDC, or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (prefer OIDC)  
- `GCS_BUCKET` + workload identity or `GCP_SA_KEY`  
- `SLACK_BACKUP_WEBHOOK_URL`  
- `BACKUP_GPG_RECIPIENT` or passphrase in a secrets manager  

---

## 4. Automated backup (every 24 hours)

| Asset | Script | Notes |
|-------|--------|------|
| DB full | `backup-postgres-full.sh` | `pg_dump -Fc`; parallel restore with `pg_restore` |
| DB incremental | **Managed** RDS/GCP/Azure PITR, or WAL archive + `pg_basebackup`, or pgBackRest | See `backup-postgres-incremental-notes.sh` |
| Uploads | `backup-uploads.sh` | zstd if available |
| Logs | `backup-logs.sh` | Prefer central logging (Loki/CloudWatch) long-term |
| Env / certs | `backup-env-encrypted.sh` | **GPG**; never upload plaintext `.env` |

**Orchestrator:** `run-daily-backup.sh` — runs steps, then syncs recent artifacts to S3 + GCS.

**Cron:** see `infra/backup/cron/crontab.example`.

---

## 5. Cloud storage

- **Primary:** AWS S3 bucket with versioning + lifecycle (e.g. transition to Glacier after N days).  
- **Secondary:** Google Cloud Storage bucket with same retention; **mirror** after S3 upload.  
- Enable **default encryption** (SSE-S3 or KMS) on both.  
- Restrict IAM to least privilege; use separate keys for backup vs app runtime.

---

## 6. Database: full vs incremental

- **Full (implemented):** custom-format dump nightly.  
- **Incremental / PITR:**  
  - **Easiest:** RDS automated backups + point-in-time restore.  
  - **Self-hosted:** enable `archive_mode` + `archive_command` to S3; keep base backups weekly.  
  - **Advanced:** pgBackRest with S3.

---

## 7. Code backup

- **GitHub** already stores all commits and branches.  
- **Mirror:** `infra/backup/scripts/git-mirror-all-branches.sh` pushes **all refs** to a second remote (e.g. second org, Gitea, AWS CodeCommit).  
- Optional: periodic bundle: `git bundle create dealix.bundle --all`.

---

## 8. Disaster recovery procedures

### 8.1 Server crash (same region)

1. Provision new VM/K8s node from IaC (Terraform).  
2. Restore **secrets**: decrypt latest `*.gpg` from GCS/S3.  
3. Restore **DB**: `pg_restore` from latest `-Fc` dump or RDS restore snapshot.  
4. Restore **uploads**: extract tarball to `UPLOAD_DIR`.  
5. Deploy **known-good image** (pin by digest) via blue/green.  
6. Run **health checks** (`/health`, smoke tests).  
7. **DNS / load balancer** cutover to green.

### 8.2 Database corruption

1. Stop writers; **failover** to replica if healthy.  
2. If no replica: restore from **last good dump** or **PITR** to timestamp before corruption.  
3. Validate with `weekly-restore-test.sh` pattern on a scratch DB.

### 8.3 Deployment failure

1. **Rollback** deployment to previous digest (`kubectl rollout undo` / ECS previous task / Terraform previous).  
2. Revert Git commit on `main` only if artifact is bad; prefer forward fix + new deploy.  
3. Restore DB **only** if migrations broke data (from backup).

### 8.4 Security incident (credential leak)

1. Rotate **all** API keys, DB passwords, JWT signing keys, OAuth secrets.  
2. Invalidate sessions; force password reset if needed.  
3. Re-issue TLS certs if private keys exposed.  
4. Audit access logs; restore from backup if data was tampered.

---

## 9. Environment backup (encrypted)

- Script `backup-env-encrypted.sh` collects `.env` files under `COMPOSE_PROJECT_DIR` and optional `/etc/dealix/ssl/*.pem`.  
- Use **GPG** with a **recipient** or **symmetric** passphrase file stored in a vault (not in repo).  
- Store only `*.gpg` in S3/GCS.

---

## 10. Deployment safety

| Mechanism | Implementation hint |
|-----------|----------------------|
| Rollback | Pin container images by digest; keep last N versions; automate `kubectl rollout undo` / ECS desired-count swap |
| Blue-green | Two deployments behind LB; shift traffic after health OK |
| Health checks | K8s `readinessProbe` hitting `/health`; synthetic checks from monitoring |

The backend exposes health endpoints under `app/api/v1/health.py` — wire these to LB and uptime monitors.

---

## 11. Monitoring & alerts

**Monitor:**

- Backup job exit code (cron mail or CI)  
- Backup **size** trend (sudden drop = failure)  
- **sha256** verification (`verify-backup.sh`)  
- Weekly **restore test** success  

**Alerts (Slack / email / SMS):**

- Backup failed (non-zero exit)  
- Restore test failed  
- Disk/object storage **quota** / full (CloudWatch + GCS metrics)  

Wire `SLACK_BACKUP_WEBHOOK_URL`, `ALERT_EMAIL_TO`, and optional Twilio in `backup.env`.

---

## 12. Weekly restore test

1. Take latest `*.dump` from S3.  
2. Run `weekly-restore-test.sh /path/to/dump.dump` on a non-prod Postgres.  
3. Run `SELECT COUNT(*)` smoke + optional app migration check.  
4. Drop test DB after success.

---

## 13. Fast recovery checklist (target &lt; 15 minutes)

**Prerequisites (must be done before an incident):**

- [ ] IaC for infra (Terraform/OpenTofu)  
- [ ] Database: replica or managed PITR + snapshot  
- [ ] Container images in registry with **immutable digests**  
- [ ] Blue/green or rolling with **one-command rollback**  
- [ ] Runbook rehearsed quarterly  
- [ ] Backup secrets and GPG keys in **two** vaults  

Without these, **15 minutes** is not realistic; adjust SLO honestly.

---

## 14. File index

| Path | Purpose |
|------|---------|
| `infra/backup/env.example` | Variables for backup scripts |
| `infra/backup/scripts/run-daily-backup.sh` | Daily orchestration |
| `infra/backup/scripts/verify-backup.sh` | Integrity / staleness |
| `infra/backup/scripts/weekly-restore-test.sh` | Restore drill |
| `infra/backup/scripts/git-mirror-all-branches.sh` | Code mirror |
| `infra/backup/cron/crontab.example` | Sample scheduler |
| `.github/workflows/backup-*.yml` | Optional CI schedules |

---

## 15. Security notes

- Never commit real `.env` or PEM files.  
- Restrict S3/GCS bucket policies to backup role only.  
- Encrypt secrets at rest with GPG; rotate keys annually.  
- Audit who can decrypt backups.
