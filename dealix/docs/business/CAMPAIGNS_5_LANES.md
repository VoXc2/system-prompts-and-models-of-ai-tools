# Dealix — 5 Saudi Campaigns (Day 1 → Day 14)

Five segment-specific campaigns extracted from the directory.
Each lane has its own `top50_<segment>.csv` in this folder.

## Campaign 1 — Real Estate Developer (TOP-50)

**File:** `top50_real_estate.csv` (Riyadh + Jeddah priority)
**Pool size:** 2,042 deduped accounts
**Day 1 quota:** 8 calls

**Pain:** A real-estate inbound lead waits an average of 11 hours before first reply in Saudi B2B. Dealix replies in 45 seconds, captures budget + location + viewing time, and routes to the closer.

**Pilot offer:** 7 days × 25 leads × 999 SAR. Money-back if Dealix misses a single Arabic reply.

**Channels:** phone_task (primary), email (only when business domain), in-person follow-up after first reply.

## Campaign 2 — Construction / مقاولات (TOP-50)

**File:** `top50_construction.csv`
**Pool size:** 2,625 deduped accounts (Mecca + Riyadh + Jeddah heavy)
**Day 1 quota:** 0 (start Day 3 — slower sales cycle)

**Pain:** Quote requests scatter across WhatsApp, calls, email; ~30% leak before pricing engineer replies. Dealix gathers specs + budget + timeline + decision-maker upfront, surfaces the ready-to-quote queue.

**Pilot offer:** 7 days × 50 RFQ → 1,500 SAR. Refund if zero responded inside 1h.

**Channels:** phone_task (primary). Construction firms rarely answer cold email.

## Campaign 3 — Hospitality + Events (TOP-50)

**File:** `top50_hospitality_events.csv`
**Pool size:** 675 deduped (mix of fنادق + قاعات حفلات + تأجير حفلات)
**Day 1 quota:** 4 calls

**Pain:** A wedding-hall inquiry that waits 30 minutes loses to the next hall. Dealix replies instantly, captures date + headcount + package + budget, and books a viewing on the team calendar.

**Pilot offer:** 999 SAR for 7 days. Replace 1 receptionist shift with Dealix Arabic auto-reply.

**Channels:** phone_task + email (when business domain).

## Campaign 4 — Food & Beverage (TOP-50)

**File:** `top50_food_beverage.csv`
**Pool size:** 647 deduped (مطاعم + كافيهات + وجبات سريعة + تموين)
**Day 1 quota:** 4 calls

**Pain:** Catering / franchise / branch inquiries get lost between WhatsApp staff phones. Dealix sorts inquiries by serious vs. tire-kicker, books real prospects with management.

**Pilot offer:** 499 SAR pilot. Auto-reply to 50 inbound restaurant inquiries.

**Channels:** phone_task primary. Email second.

## Campaign 5 — Logistics / شحن (TOP-50)

**File:** `top50_logistics.csv`
**Pool size:** 570 deduped (شحن + نقل across all major cities)
**Day 1 quota:** 4 calls

**Pain:** RFQ for shipping is high-frequency, low-touch. Slow Arabic response = the prospect is gone in 10 minutes. Dealix gathers weight + destination + date + cargo type, opens a CRM ticket.

**Pilot offer:** 999 SAR / 7 days. Money-back if RFQ response time doesn't drop below 5 minutes.

**Channels:** phone_task primary. Some logistics co's answer email.

## Bonus — Saudi SaaS Companies (TOP-35)

**File:** `top50_saas_tech.csv`
**Pool size:** 35 deduped
**Day 1 quota:** 2 (use as ICP-match for product research, not just sales)

**Pain:** They sell SaaS in Saudi but don't have an Arabic-native AI sales rep. Dealix is in their stack.

**Pilot offer:** Free pilot in exchange for design partnership + case study.

**Channels:** LinkedIn manual research → email (most have business domains).

## Bonus — Agency Partners (only 2 in directory)

**File:** `top50_agency_marketing.csv`
**Pool size:** 2 (one Advertising agency, one Marketing agency in directory)
**Day 1 quota:** 2 (both — easy quota)

**Action:** This pool is thin in the uploaded directory. Use Google Maps `/api/v1/leads/discover/local` with `industry=marketing_agency` after deploy to fill the pipeline. Saudi agency landscape is mostly outside chamber directories.

## Day 1 batch (`day1_batch_20_direct_10_partners.csv`)

Pre-built for you:
- 8 real-estate calls (Riyadh focus)
- 4 hospitality_events calls
- 4 logistics calls
- 4 food_beverage calls
- 2 marketing-agency partner outreach
- 5 SaaS partner outreach

= 27 ready-to-execute outreaches with bilingual messages.

## Cadence (per account)

```
Day 0  — first touch (call/email)
Day 2  — bump if no reply
Day 5  — value-add (case study / metric)
Day 10 — last touch
Day 30 — quarterly nurture
```

## What the Saudi Data Source Catalog adds

After deploy, hit `GET /api/v1/data/sources/catalog` to get the green/yellow/red rated catalog of additional Saudi data sources (chambers, gov open data, trade associations) — the directory file is ONE source of many.
