# 🗄️ Dealix — Production Database State

**Last seeded:** 2026-04-24
**Seed script:** `scripts/seed_production_db.py`
**Target:** Postgres on Railway (env: `Dealix` / service: `web`)
**Source:** `docs/ops/lead_machine/SAUDI_LEAD_GRAPH_MASTER.csv`

---

## What's in the DB right now

### `leads` table

| Field | Example value |
|-------|---------------|
| id | auto-generated |
| source | manual |
| company_name | Foodics, Lucidya, Salla, ... |
| contact_name | CEO / Founder / BD Lead (role-based) |
| sector | SaaS Restaurant / CXM / E-commerce / Fintech / ... |
| region | SA / AE-SA / KW-SA / etc. |
| locale | ar |
| status | new (after intake) |
| message | first_message_angle + priority + opportunity_type + offer_recommended |
| fit_score | (computed by Phase 8 pipeline on insert) |
| created_at | 2026-04-24 |

**Row count:** 158 leads seeded (all eligible rows from the 159 in master CSV minus HIGH/BLOCKED/HOLD_FOR_APPROVAL)

### `deals` table

Empty until first conversation moves to qualified stage.

### `agent_runs` table

Populated as endpoints run. Not user-visible data.

---

## Health check status

```
GET /health/deep:
  postgres   → async driver OK, writes succeeding (158 rows inserted)
               sync health-check fails (psycopg2 not installed — cosmetic only)
  redis      → skip (no REDIS_URL — optional, not needed for Phase 8)
  llm        → fail (no LLM keys configured)
```

**Interpretation:** writes work, reads work, the "fail" on postgres in `/health/deep` is a misleading sync-driver check. The async driver (asyncpg) is what the app actually uses.

---

## How to re-seed / update

```bash
cd dealix
python scripts/seed_production_db.py
# Or with custom paths:
python scripts/seed_production_db.py --api https://web-dealix.up.railway.app --csv path/to/leads.csv
```

**Idempotency note:** The intake pipeline uses `dedup_hash` based on email+phone+company. Re-running the seed will NOT duplicate entries that already exist. New companies added to the CSV will be appended on next run.

---

## Who sees this data

| Access | Path |
|--------|------|
| Internal (Sami) | Railway Postgres dashboard → `leads` table |
| Frontend form | `POST /api/v1/leads` (live) — new leads auto-score + CRM sync |
| Public | No listing endpoint yet (privacy) |

**Privacy note:** no personal phone numbers / emails for the 158 seeded rows (only role names like "CEO"). Real customer data gets stored only when someone submits a form or replies to outreach and explicitly consents.

---

## Upgrade path (when LLM key added)

Once `GROQ_API_KEY` or `ANTHROPIC_API_KEY` is set in Railway env `Dealix/web`:

1. Each lead on insert goes through full pipeline:
   - Intake (dedup + normalize)
   - ICP Matcher (fit_score via LLM)
   - Pain Extractor (extract pains from message)
   - Qualification (BANT)
   - CRM sync (HubSpot if configured)
   - Booking (Calendly if auto_book=true)
2. `fit_score` becomes meaningful (not 0.0)
3. Pipeline response includes rich extraction + qualification details

Without LLM key, only intake + dedup run (all 158 rows have intake + dedup complete).

---

## Next DB work (when revenue starts)

### When 1st customer signs:
- Populate `deals` table with their signed plan
- Link deal → lead via foreign key
- Add `customer_success_tracker.csv` as new table

### When 5+ customers:
- Add `conversations` table (for reply handling log)
- Add `payments` table (manual + Moyasar)
- Add `partners` table (agencies)

### When 20+ customers:
- Add `case_studies` table
- Add `testimonials` table
- Full CRM extension

---

## Backup rhythm

Railway Postgres has automatic daily backups (7-day retention on free tier). Recommend:

1. **Weekly:** export `leads` table → CSV → commit to `docs/ops/lead_machine/db_snapshot_YYYY-MM-DD.csv`
2. **Monthly:** full pg_dump to local storage
3. **Before major migrations:** manual backup

---

## Cost estimate

| Item | Cost |
|------|------|
| Railway Postgres (starter) | $5/month |
| Railway app (web service) | $5/month |
| Total infrastructure | **$10/month** |
| Optional at scale: | |
| PostHog analytics | Free tier fine for 100 customers |
| Sentry | $26/month (Team plan, when ready) |
| Custom domain SSL | Free (Let's Encrypt auto) |

Scaling plan: infra stays < $30/month up to 1,000 customers.

---

## Recovery playbook

If DB corrupts or gets wiped:

1. Restore from Railway backup (last 24h always available)
2. Re-run `python scripts/seed_production_db.py`
3. Re-upload customer-specific data from `manual_payment_log.md`
4. Verify with sample GET (once read endpoint is built)
5. Document incident in `docs/ops/INCIDENT_RUNBOOK.md`

RTO: < 30 minutes from detection.
RPO: < 24 hours (daily backup cadence).
