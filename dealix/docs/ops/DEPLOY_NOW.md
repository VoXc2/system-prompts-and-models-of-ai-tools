# Dealix Lead Machine — Deploy Now

This bundle contains the full **Provider Adapters + Data Lake + Lead Graph + Outreach Prep** build, ready to land on `main` in **two** commits (`73b5bb7` + `7aa2302`). Both are inside the single patch file.

**Patch dry-applied to a fresh clone of `VoXc2/dealix` and 32 unit tests passed** — so `git am` will work on your local repo if your `main` is at `2a9df98` or earlier.

## What's in the bundle

| File | What |
|---|---|
| `0001-feat-lead-machine.patch` | Single git patch — apply with `git am` |
| `dealix-lead-machine-files.tar.gz` | Same files as a tarball — copy into your repo if `git am` fails |
| `DEPLOY_NOW.md` | This doc |

**Commit content:**
- 5 provider chains (Search / Maps / Crawler / Tech / EmailIntel) with env-gated fallbacks
- 7 new SQLAlchemy tables (`raw_lead_imports`, `raw_lead_rows`, `accounts`, `contacts`, `signals`, `lead_scores`, `data_suppression_list`)
- 4 normalize/dedupe/score/enrichment pipelines
- 19 new API endpoints (`/leads/discover/local`, `/leads/discover/web`, `/leads/enrich/full`, `/leads/enrich/batch`, all `/data/*`, all `/outreach/*`)
- 4 CLI scripts (`import_leads`, `audit_lead_file`, `discover_local_to_csv`, `export_outreach_ready`)
- 4 architecture docs
- 32 smoke tests passing
- Updated `.env.example` with all new env vars
- Updated `/api/v1/prospect/search-diag` with `tier1_ready` / `tier2_ready` flags

---

## Step 1 — Apply the patch

On your laptop, in your dealix repo:

```bash
cd /path/to/dealix
git checkout main
git pull --rebase origin main

# Apply the patch
git am < /path/to/0001-feat-lead-machine.patch

# OR if git am has trouble, extract the tarball and stage manually:
# tar xzf /path/to/dealix-lead-machine-files.tar.gz
# git add -A
# git commit -m "feat(lead-machine): provider chains + Data Lake + Lead Graph"
```

Verify:
```bash
git log --oneline -1
# should show: feat(lead-machine): provider chains + Data Lake + Lead Graph + outreach prep
```

## Step 2 — Push

If you don't have GitHub CLI auth set up:

```bash
gh auth login
# choose: GitHub.com → HTTPS → Login with browser
```

Then:
```bash
git push origin main
```

**Do NOT reuse the PAT you pasted in chat.** It should be revoked.

## Step 3 — Add Railway env vars

Railway → project → environment **Dealix** → service **web** → Variables. Add:

```env
# ── Layer 1 (required) ──
DATABASE_URL=${{Postgres.DATABASE_URL}}
GOOGLE_SEARCH_API_KEY=<your_key>
GOOGLE_SEARCH_CX=75ae2277dfd754a1a
GROQ_API_KEY=<your_key>
SENTRY_DSN=<your_dsn>

# ── Layer 2 (lead engine) ──
GOOGLE_MAPS_API_KEY=<your_places_key>
```

Click **Review** → **Deploy**.

For the Google Maps key:
1. Google Cloud Console → APIs & Services → Library → enable **Places API**.
2. Credentials → Create Credentials → API key.
3. Restrict the key: **API restrictions → Places API only**.
4. Paste into Railway as `GOOGLE_MAPS_API_KEY`.

## Step 4 — Verify deploy

After Railway shows the deploy as Active:

```bash
# Tier-readiness (one-shot check)
curl https://api.dealix.me/api/v1/prospect/search-diag | jq '{tier1_ready, tier2_ready, hint}'

# Should show tier1_ready: true, tier2_ready: true (after Maps key added)
```

```bash
# List Saudi industries + cities
curl https://api.dealix.me/api/v1/leads/discover/local-industries | jq '.industries[0:3], .cities[0:3]'
```

```bash
# Pull 20 dental clinics in Riyadh
curl -X POST https://api.dealix.me/api/v1/leads/discover/local \
  -H 'content-type: application/json' \
  -d '{"industry":"dental_clinic","city":"riyadh","max_results":20,"hydrate_details":true}' | jq '.data.results[0:3]'
```

```bash
# Single-account enrichment
curl -X POST https://api.dealix.me/api/v1/leads/enrich/full \
  -H 'content-type: application/json' \
  -d '{"company_name":"Foodics","domain":"foodics.com","city":"Riyadh","sector":"saas","level":"standard"}' | jq '.score, .data_quality, .providers_used'
```

## Step 5 — First end-to-end run (your data → outreach queue)

```bash
# 1. Audit a CSV before uploading (offline)
python scripts/audit_lead_file.py vendor_file.csv

# 2. Upload + run full pipeline (normalize → dedupe → enrich)
python scripts/import_leads.py vendor_file.csv \
    --source-name "vendor_x_2026_q2" \
    --source-type paid \
    --allowed-use "business_contact_research_only" \
    --risk-level high \
    --auto-pipeline

# 3. Get outreach-ready leads
python scripts/export_outreach_ready.py --priority P0,P1 --max 50 --out today_outreach_50.csv
```

Or skip the file and pull live from Maps:

```bash
python scripts/discover_local_to_csv.py dental_clinic riyadh --max 20
python scripts/import_leads.py dental_clinic_riyadh.csv \
    --source-name "maps_dental_clinic_riyadh" \
    --source-type google_maps --auto-pipeline
python scripts/export_outreach_ready.py --priority P0,P1 --max 20 --out riyadh_dentists_outreach.csv
```

## Step 6 — Check the local smoke tests pass

```bash
cd /path/to/dealix
python -m pytest tests/unit/test_pipelines_smoke.py tests/unit/test_provider_smoke.py -q -o "addopts="
# expected: 32 passed, 2 skipped (live provider tests skip without keys)
```

---

## Compliance reminders (already enforced in code)

- Every imported row carries `source_type`, `allowed_use`, `consent_status`, `risk_level`.
- `/outreach/prepare-from-data` checks `data_suppression_list` + `opt_out` before producing `ready` entries.
- `approval_required=True` is the default for all queued messages — Sami still approves.
- WhatsApp is **inbound only** in Dealix. Don't add an outbound WhatsApp adapter.
- LinkedIn is **manual research + manual send** only. Don't add scraping.

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `tier1_ready: false` after deploy | One of `DATABASE_URL`/`GOOGLE_SEARCH_API_KEY`+`CX`/LLM/`SENTRY_DSN` missing | Check `search-diag` output, add the missing one, re-deploy |
| `/leads/discover/local` returns `status: no_key` | `GOOGLE_MAPS_API_KEY` not set or empty in Railway | Add it, click Review → Deploy |
| `/data/import` returns `skipped_db_unreachable` | DB is the same problem as everywhere — `DATABASE_URL` empty | Set `DATABASE_URL=${{Postgres.DATABASE_URL}}` (with the literal Railway template syntax) |
| `git am` fails | local uncommitted work | `git stash` first, then `git am`, then `git stash pop` |
| 401 from Google Places | billing not enabled or wrong restriction | GCP Console → enable billing on the project, restrict key to Places API |
