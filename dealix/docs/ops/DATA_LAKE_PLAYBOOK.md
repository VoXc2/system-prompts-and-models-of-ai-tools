# Dealix Data Lake + Lead Graph Playbook

How to use Dealix as a data ingestion + enrichment + outreach-prep system, not a blast tool.

## Mental model

```
Data Lake (raw_lead_imports + raw_lead_rows)
    ↓ normalize
Lead Graph (accounts + contacts + signals)
    ↓ enrich (providers)
Scored Accounts (lead_scores)
    ↓ suppression check + channel policy
Outreach Queue (always approval_required for first 30 days)
```

Raw rows are kept forever. Outreach happens only after compliance gates pass.

## 4 data types Dealix accepts

| Type | Example source | `source_type` |
|---|---|---|
| Owned | Customer CRM, your own form submissions | `owned` |
| Public | Google Search, Google Maps, business directories | `public` / `google_maps` / `google_search` |
| Paid | Vetted vendor lists with documented allowed-use | `paid` |
| Partner | Co-marketing list with explicit consent | `partner` |

**Never accept:** WhatsApp number lists with no source, scraped LinkedIn profiles,
personal emails without opt-in.

## Required metadata per import

```json
{
  "source_name": "vendor_x_saudi_real_estate_2026",
  "source_type": "paid",
  "allowed_use": "business_contact_research_only",
  "consent_status": "legitimate_interest",
  "risk_level": "high",
  "rows": [...]
}
```

If the vendor can't tell you `source`, `allowed_use`, and `last_updated` — don't buy the list.

## Step-by-step ingestion

### 1. Audit the file BEFORE upload

```bash
python scripts/audit_lead_file.py vendor_file.csv
```

Reports acceptance rate, phone/email validity, dedup risk. If acceptance < 50%,
reject the file or ask the vendor to clean it.

### 2. Upload

```bash
python scripts/import_leads.py vendor_file.csv \
    --source-name "vendor_x_2026_q2" \
    --source-type paid \
    --allowed-use "business_contact_research_only" \
    --risk-level high \
    --auto-pipeline
```

`--auto-pipeline` runs normalize → dedupe → enrich automatically.

### 3. Or call the API directly

```
POST /api/v1/data/import
POST /api/v1/data/import/{id}/normalize
POST /api/v1/data/import/{id}/dedupe
POST /api/v1/data/import/{id}/enrich        body: {enrichment_level: "standard", max_accounts: 25}
GET  /api/v1/data/import/{id}/report
```

### 4. Discover local Saudi sectors via Google Maps

```bash
python scripts/discover_local_to_csv.py dental_clinic riyadh --max 20
# wrote 20 rows → dental_clinic_riyadh.csv

python scripts/import_leads.py dental_clinic_riyadh.csv \
    --source-name "maps_dental_clinic_riyadh" \
    --source-type google_maps \
    --auto-pipeline
```

### 5. Suppress opt-outs

```
POST /api/v1/data/suppression
body: {"email": "...", "reason": "opt_out_request_2026_04"}
```

### 6. Prepare outreach

```
POST /api/v1/outreach/prepare-from-data
body: {"priority": ["P0","P1"], "max_accounts": 25, "persist": true}
```

Returns `ready` / `needs_review` / `blocked` lists. Persisted rows go to
`outreach_queue` with `approval_required=True` — Sami still approves manually.

### 7. Export a CSV for human send

```bash
python scripts/export_outreach_ready.py --priority P0,P1 --max 50 \
    --out today_outreach_50.csv
```

## Compliance guardrails (already enforced)

- Suppression hits → `blocked`, never queued.
- `opt_out=true` on contact → `blocked`.
- `risk_level=high` → `needs_review`, requires explicit approval.
- Missing `allowed_use` → `needs_review`.
- All queue rows have `approval_required=True` for the first 30 days.

## Data quality scoring

Each account gets a `data_quality_score` 0..100 based on field completeness +
signal coverage − negatives (no source, opt-out, high risk). See
`auto_client_acquisition/pipelines/scoring.py::compute_data_quality`.

`/api/v1/data/accounts?priority=P0` lets you pull the highest-DQ + highest-score
accounts ready for action.

## Google Maps cache policy

Per Google Maps Platform terms, we store `place_id` (allowed) and refresh details
on demand rather than caching everything forever. See
`auto_client_acquisition/connectors/google_maps.py::discover_local`.

## Don't do

- ❌ Auto-send from raw rows. Always normalize → dedupe → enrich → score → queue.
- ❌ Cold-blast WhatsApp. WhatsApp is inbound only in Dealix.
- ❌ Scrape LinkedIn. Use it for manual research only.
- ❌ Use a list with no `source` or `allowed_use`. Reject the data.
- ❌ Send unapproved messages in the first 30 days of any new customer.
