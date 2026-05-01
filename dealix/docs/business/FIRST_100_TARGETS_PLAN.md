# Dealix — Day 1 Operating Playbook

100 Saudi B2B accounts queued. Zero auto-send. This file is your morning script.

## What's in this folder

| File | What you do with it |
|---|---|
| `day1_outreach_queue.csv` | 100 ready accounts with Arabic message drafts. Open in Excel, Sami approves row-by-row before any send. |
| `saudi_directory_normalized.csv` | All 6,957 unique Saudi B2B companies after dedupe + scoring. Master record. |
| `import_payload_high_fit.json` | 1,000-row payload to POST to `/api/v1/data/import` after deploy. |
| `day1_scorecard.json` | Pipeline metrics for the build. |
| `PRICING_AND_PACKAGES.md` | Pilot 499 SAR → Starter 999 SAR → Pro 5K SAR ladder. |

## Queue split (100 accounts)

| Sector | Count | Why this segment |
|---|---:|---|
| `real_estate_developer` (Riyadh) | 25 | Inbound leads, slow Arabic response = lost deal. ICP gold. |
| `real_estate_developer` (Jeddah) | 20 | Same as above, second-largest market. |
| `events` / قاعة حفلات | 15 | Each lead = 5K-100K SAR booking. Fastest pilot conversion. |
| `hospitality` / فندق | 15 | MICE + Iftar + Suhoor inquiries. Heavy Arabic inbound. |
| `logistics` / شحن | 15 | RFQ response time = revenue. Pure B2B. |
| `saas` / Software company | 10 | Saudi SaaS founders — Dealix is in their stack stack. |

All 100 → `priority=P2`, channel=`phone_task`. Personal-email rows demoted to phone (PDPL guard).

## Day 1 — 9:00 AM → end of day

### 9:00 — Coffee & open the queue
Open `day1_outreach_queue.csv` in Excel. Sort by `total_score` descending.

### 9:30 — Top 5 phone calls
First 5 P2 real-estate Riyadh accounts. Script (Khaliji Arabic):

> السلام عليكم، أنا سامي من Dealix. اتصلت لأن نشتغل على AI sales rep بالعربي يخدم شركات التطوير العقاري السعودية — يرد على lead خلال 45 ثانية بدل ما يعلق نص يوم.
> هل تواجهون مشكلة وقت الرد على leads الـ inbound؟

**Stop after 5 calls.** Log results in `pipeline_tracker.csv` (create if missing).

### 11:00 — 5 emails (with opt-out)
Top 5 accounts that have a business email (filter `is_personal_email=False`).
Use the `message_ar` column as draft. Send from Sami's Gmail. Always include the opt-out line.

### 14:00 — 1 LinkedIn message
**Manual research first** (use the LinkedIn URL only as research — never automate).
Pick 1 Saudi SaaS founder from the queue. Send a personalized note referencing their company.

### 16:00 — Pricing-page demo
Walk a real prospect through the demo using `PRICING_AND_PACKAGES.md` as reference.
Lead with: *"Pilot 499 ريال، 7 أيام، نرد على leadsكم بدلاً منكم. لو ما اقتنعتم — استرجاع كامل خلال 3 أيام."*

### 18:00 — End-of-day scorecard
Update `day1_scorecard.json` with:
- `messages_sent_today`
- `replies_today`
- `demos_booked`
- `pilot_signups`
- `payment_requested`

## Day 1 success criteria

| Metric | Target |
|---|---:|
| Outbound reaches | 11 (5 calls + 5 emails + 1 LinkedIn) |
| Replies | ≥ 2 |
| Demo booked | ≥ 1 |
| Pilot pay request sent | ≥ 1 |
| Hours worked | ≤ 6 |

If you hit ≥ 1 demo booked → you've proven the funnel works. **Repeat tomorrow with the next 11.**

## What you don't do today

- ❌ Cold WhatsApp blast (channel violation + spam)
- ❌ Bulk email to all 100 (ramp deliverability slowly)
- ❌ Promise custom features beyond pilot scope
- ❌ Skip the approval gate on any message
- ❌ Use any of the 6,636 personal emails for email channel

## Day 2 setup

1. Run `python scripts/audit_lead_file.py saudi_directory_normalized.csv` — confirm 0 collisions remain.
2. Pull the next 100 from `saudi_directory_normalized.csv` (filter to `priority=P2`, sort by score, skip any in yesterday's queue).
3. Same playbook, different segments. Maybe add `marketing_agency` if Maps key is now live.

## When the deploy lands

After Railway env is set + push lands, replace the manual queue with:

```
# Push 1000-row high-fit payload to the API
curl -X POST https://api.dealix.me/api/v1/data/import \
  -H 'content-type: application/json' \
  -d @import_payload_high_fit.json

# Run the server-side pipeline
curl -X POST https://api.dealix.me/api/v1/data/import/<id>/normalize
curl -X POST https://api.dealix.me/api/v1/data/import/<id>/dedupe
curl -X POST https://api.dealix.me/api/v1/data/import/<id>/enrich -d '{"enrichment_level":"standard","max_accounts":50}'

# Pull outreach-ready
curl -X POST https://api.dealix.me/api/v1/outreach/prepare-from-data \
  -d '{"priority":["P0","P1","P2"],"max_accounts":100,"persist":true}'
```

The server does what we did locally, plus enrichment via Google CSE + Maps + Crawler chains, and persists to Postgres so you have a real CRM behind the queue.
