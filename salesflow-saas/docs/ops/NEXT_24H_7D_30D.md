# Dealix — Execution Plan: 24h / 7d / 30d

**Starting state:** 28/39 gates closed. Product live. 0 revenue. 0 messages sent.

---

## Next 24 Hours

| # | Deliverable | Owner | Dependency | Definition of Done | Metric | Risk |
|---|-------------|-------|------------|-------------------|--------|------|
| 1 | Add GROQ_API_KEY in Railway env Dealix/web | Sami | console.groq.com (free) | `/api/v1/prospect/search-diag` shows GROQ set | LLM features activate | Key in wrong env (use Dealix, not Agent branch) |
| 2 | Add GOOGLE_SEARCH_API_KEY + CX in Railway | Sami | Google Cloud Console | `/api/v1/prospect/search-diag` shows Google set | Web discovery active | Needs billing account for Maps |
| 3 | Add SENTRY_DSN in Railway | Sami | sentry.io free plan | Sentry receives test error | Error alerting active | None |
| 4 | Send 5 WhatsApp warm messages | Sami | Personal contacts who own businesses | 5 conversations started | pipeline > 0 | Low reply rate from cold — use warm only |
| 5 | Publish Founder Launch Post on LinkedIn | Sami | LinkedIn account | Post visible + URL captured | Inbound starts | None |
| 6 | Send 1 LinkedIn DM to agency partner | Sami | LinkedIn | Connection request sent | Partner pipeline > 0 | May take days for acceptance |

**24h success = 3 keys added + 5 messages sent + 1 post published.**

---

## Next 7 Days

| # | Deliverable | Owner | Dependency | Definition of Done | Metric | Risk |
|---|-------------|-------|------------|-------------------|--------|------|
| 1 | 30+ outreach messages across channels | Sami | Templates in COMMAND_CENTER | Messages logged in tracker | 30 touches | Fatigue — batch 5/day |
| 2 | First demo booked via Calendly | Sami | At least 1 positive reply | Calendly notification received | 1 demo | Low conversion — try warm contacts first |
| 3 | First pilot offered (499 SAR) | Sami | Completed demo | Payment request sent | 1 offer | Prospect may need time |
| 4 | First partner contacted | Sami | AGENCY_PARTNER_OFFER.md | Agency responds | 1 partner conversation | Agency may want proof first |
| 5 | Moyasar diagnostic completed | Sami | Moyasar dashboard access | Know if live key works or needs fix | Unblocks automated payment | KYC may take days |
| 6 | PostHog receives 1+ event | Sami | POSTHOG_API_KEY added | Event visible in PostHog dashboard | Funnel measurement starts | Free plan sufficient |
| 7 | 3 LinkedIn posts published | Sami | Content from COMMAND_CENTER | Posts visible | Inbound pipeline | Consistency matters more than perfection |

**Week 1 success = 1 demo + 1 pilot offer + 3 posts + partner motion started.**

---

## Next 30 Days

| # | Deliverable | Owner | Dependency | Definition of Done | Metric | Risk |
|---|-------------|-------|------------|-------------------|--------|------|
| 1 | 200+ outreach touches total | Sami | Sustained daily activity | Tracker shows 200+ rows | Volume | Burnout — keep to 10/day |
| 2 | 5 demos completed | Sami | Positive replies | Calendly shows 5 past events | Demo rate | Need warm + cold mix |
| 3 | 3 pilot payments received | Sami | Completed demos | Bank/STC Pay proof | 1,497 SAR MRR | Conversion uncertainty |
| 4 | 1 agency partner active | Sami | Partner signs + brings client | Partner's client in pilot | Partner channel open | Agencies want proof |
| 5 | Marketers page rewritten | Claude | MARKETERS_PAGE_PLAN.md | Page sells services, not just links | Page conversion | TSX rewrite needed |
| 6 | Moyasar live checkout working | Sami | KYC + key fix | 1 SAR test transaction succeeds | Automated payment | May need new key |
| 7 | Case study draft from first client | Sami | First pilot completed | 1-page results document | Social proof | Client may not agree to name |
| 8 | Rollback drill completed | Claude/Sami | SSH access to server | Documented rollback in < 5 min | Recovery confidence | SSH currently blocked |
| 9 | 10 LinkedIn posts total | Sami | Weekly posting cadence | Posts visible | Brand building | Consistency > perfection |
| 10 | PostHog funnel visible | Sami/Claude | POSTHOG key + landing events | landing → signup → demo → paid visible | Data-driven decisions | Free plan limits |

**Month 1 success = 3 paid pilots (1,497 SAR) + 1 partner + funnel visible + case study draft.**

---

## Revenue Trajectory (conservative)

| Week | Touches | Replies | Demos | Pilots | Paid | MRR (SAR) |
|------|---------|---------|-------|--------|------|-----------|
| 1 | 30 | 3 | 1 | 0 | 0 | 0 |
| 2 | 60 | 8 | 2 | 1 | 0 | 0 |
| 3 | 90 | 12 | 3 | 2 | 1 | 499 |
| 4 | 120 | 15 | 5 | 3 | 3 | 1,497 |
| **Total** | **300** | **38** | **11** | **6** | **3** | **1,497** |

Assumes: 13% reply rate, 29% demo-from-reply rate, 55% pilot-from-demo, 50% paid-from-pilot.

---

## What NOT to Do in 30 Days

- Do NOT rebuild the dashboard
- Do NOT add new LLM providers
- Do NOT implement Temporal/LangGraph/Qdrant
- Do NOT build voice receptionist or webchat
- Do NOT start v3.1
- Do NOT expand to UAE/Egypt
- Do NOT build mobile app
- Do NOT hire before first 3 paid clients
- Do NOT spend on ads before proving manual outreach converts
