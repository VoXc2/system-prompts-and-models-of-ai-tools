# Dealix ICP Scoring Model — 100-point framework

**One score per lead. Used across all use cases with weight shifts per opportunity type.**

---

## Four components (100 total)

| Component | Points | Measures |
|-----------|--------|----------|
| **Fit** | 40 | Does the target match the product? |
| **Intent** | 30 | Are they showing buying / engagement signals now? |
| **Accessibility** | 15 | Can we reach them legally and personally? |
| **Revenue Potential** | 15 | How much revenue / leverage does this unlock? |

Priority tiers:
- **P0** — 80+ (contact now)
- **P1** — 65–79 (research + personalize, contact this week)
- **P2** — 45–64 (nurture / content / soft touch)
- **BACKLOG** — <45 or HIGH risk without approval

---

## Fit Score (40 points)

| Criterion | Points |
|-----------|--------|
| Segment match (is it in our 8 target sectors?) | 10 |
| Company size fit (20–500 employees sweet spot for B2B) | 5 |
| Market fit (Saudi / GCC / Arabic-first) | 5 |
| Lead flow evidence (they clearly have inbound leads) | 10 |
| Sales / booking workflow exists | 10 |

---

## Intent Score (30 points)

| Criterion | Points |
|-----------|--------|
| Hiring sales / BDR / growth (posted in last 90 days) | 8 |
| Uses CRM / Calendly / WhatsApp widget | 8 |
| Running paid ads OR active landing-page iteration | 6 |
| Recent funding or news (last 12 months) | 4 |
| Founder content about sales/GTM pain | 4 |

---

## Accessibility Score (15 points)

| Criterion | Points |
|-----------|--------|
| Decision maker identified publicly (LinkedIn page, press, site) | 5 |
| Legal contact path exists (public email, LinkedIn DM, intro available) | 5 |
| Strong personalization angle (specific recent event to reference) | 5 |

---

## Revenue Potential (15 points)

| Criterion | Points |
|-----------|--------|
| Can afford pilot (1 SAR – 999 SAR/mo starter) | 5 |
| Can afford retainer (growth 2,999 / scale 7,999) | 5 |
| Partner expansion potential (if they become advocate → 3+ referrals) | 5 |

---

## Weight profiles by opportunity type

Same components, different priorities:

| Opportunity type | Fit × | Intent × | Access × | Revenue × | Notes |
|------------------|-------|----------|----------|-----------|-------|
| DIRECT_CUSTOMER  | 1.0 | 1.0 | 1.0 | 1.0 | Balanced (baseline) |
| AGENCY_PARTNER   | 1.2 | 0.8 | 1.0 | 1.3 | Fit + revenue dominate |
| IMPLEMENTATION_PARTNER | 1.2 | 0.8 | 1.0 | 1.3 | Same as agency |
| REFERRAL_PARTNER | 0.8 | 0.6 | 1.5 | 1.0 | Access matters most |
| STRATEGIC_PARTNER | 1.3 | 0.5 | 1.0 | 1.5 | Fit + revenue dominate |
| CONTENT_COLLABORATION | 0.7 | 1.2 | 1.2 | 0.6 | Intent + access |
| INVESTOR_OR_ADVISOR | 1.0 | 0.6 | 1.5 | 1.0 | Access matters most |
| B2C_AUDIENCE     | 1.2 | 1.2 | 0.8 | 1.0 | Fit + intent |

After weighting, renormalize to 100 (divide by 4.0, multiply by 100 ÷ max_possible).

---

## Worked example — Foodics as DIRECT_CUSTOMER

| Criterion | Value | Points |
|-----------|-------|--------|
| Segment (SaaS for restaurants) | ✓ target | 10 |
| Size (200–1000 employees) | ✓ sweet spot | 5 |
| Market (Saudi native, GCC expansion) | ✓ | 5 |
| Lead flow (high inbound after Series C) | ✓✓ | 10 |
| Sales/booking workflow | ✓ (has demo form) | 10 |
| **Fit** | — | **40/40** |
| Hiring sales (active) | ✓ confirmed | 8 |
| CRM/Calendly likely | ✓ | 8 |
| Paid ads / landing iteration | ✓ | 6 |
| Series C Oct 2024 ($170M) | ✓ | 4 |
| Founder content on GTM | ✓ | 4 |
| **Intent** | — | **30/30** |
| DM identified (Ahmad Al-Zaini CEO) | ✓ | 5 |
| Legal contact path (LinkedIn DM manual) | ✓ | 5 |
| Personalization angle (Series C) | ✓ | 5 |
| **Accessibility** | — | **15/15** |
| Pilot affordable | ✓ | 5 |
| Retainer affordable | ✓ | 5 |
| Partner expansion (their merchants) | ✓ | 5 |
| **Revenue** | — | **15/15** |
| **Total** | — | **100/100** — **P0** |

---

## Risk score (separate from priority)

Risk reduces priority tier by one level if HIGH and no approval:

- **LOW** — Only company-level public data, outreach via public company contact
- **MEDIUM** — Named business contact from public source, single personalized DM
- **HIGH** — Personal phone / personal email / cold direct marketing
- **BLOCKED** — No lawful source, or platform-prohibited method (e.g. LinkedIn bot)

Rule: never contact HIGH or BLOCKED without explicit human approval logged in `pipeline_tracker.csv` notes.

---

## Using the score

The score drives four decisions:

1. **Order of outreach** — P0 today, P1 this week, P2 nurture, BACKLOG deferred
2. **Message investment** — P0 gets fully personalized (5 min), P1 semi-custom (2 min), P2 templated
3. **Channel selection** — P0 → LinkedIn manual + follow-up email, P1 → LinkedIn manual only, P2 → content mentions
4. **Follow-up cadence** — P0: +2/+5/+10 days; P1: +5/+14; P2: quarterly nurture

---

## Scoring a new lead — 5-minute process

1. Collect evidence (2 minutes) → company site scan + LinkedIn public + one news search
2. Mark signals against `SIGNAL_TAXONOMY.md` (1 minute)
3. Sum each component (1 minute)
4. Apply weight profile per opportunity type (30 seconds)
5. Assign risk level (30 seconds)

Output fields to fill in `pipeline_tracker.csv`: `fit_score`, `intent_score`, `access_score`, `revenue_score`, `priority`, `risk`, `opportunity_type`, `reason_1_line`.
