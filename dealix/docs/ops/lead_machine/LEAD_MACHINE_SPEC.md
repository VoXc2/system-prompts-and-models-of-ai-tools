# Dealix Lead Intelligence Router — v1 Spec

**What it is:** A legal, evidence-based engine that discovers, enriches, scores, and routes leads (companies + people) against a natural-language Ideal Customer Profile, for 5 use cases: sales, partnership, collaboration, investor, b2c_audience.

**What it is not:** a scraper. No unauthorized LinkedIn automation, no bot messaging, no browser extensions that bypass anti-bot defenses.

---

## Core pipeline (10 stages)

```
(1) ICP intake           →  natural-language goal  →  structured ICP + signals required
(2) Source routing       →  decide connectors to call based on what's configured
(3) Discovery            →  produce candidate companies with source attribution
(4) Enrichment           →  technographics + firmographics + public pages
(5) Signal detection     →  buying / partnership / collab / investor / b2c signals
(6) Decision-makers      →  legal role + contact surface identification
(7) Scoring              →  100-point model → priority
(8) Personalization      →  short Arabic/English message tailored to evidence
(9) Compliance check     →  source, opt-out, channel legality, jurisdiction
(10) Export              →  CSV / pipeline_tracker.csv / CRM / GitHub issue
```

Every stage emits an **evidence record** — claim + source_url + source_type + collected_at + confidence.

---

## Minimum viable v1 (what actually ships today)

| Stage | v1 implementation | Connector needed |
|-------|-------------------|------------------|
| 1. ICP intake | Free-text form on landing + `POST /api/v1/prospect/discover` body | — |
| 2. Source routing | LLM-native (Claude/Gemini) — uses training knowledge of Saudi market | — |
| 3. Discovery | LLM-produced candidates with strict "no invention" prompt | (later: Google CSE) |
| 4. Enrichment | LLM + optional manual lookup | (later: Wappalyzer API) |
| 5. Signals | LLM extracts from its knowledge + prompt-provided evidence | (later: job-post/news crawlers) |
| 6. Decision-makers | LLM names public founders/execs; URL only if high-confidence | (later: Apollo People API) |
| 7. Scoring | 100-point model in [ICP_SCORING_MODEL.md](./ICP_SCORING_MODEL.md) | — |
| 8. Personalization | LLM generates ≤280-char Khaliji opening referencing one evidence item | — |
| 9. Compliance | Static checks: channel ≠ LinkedIn-bot; email has opt-out; no PII fabrication | — |
| 10. Export | JSON response → landing UI + `docs/ops/lead_machine/TOP_10_SCORED.csv` | — |

**Ships now.** Connector upgrades slot in later behind env vars (`GOOGLE_SEARCH_API_KEY`, `WAPPALYZER_API_KEY`, `APOLLO_API_KEY`) without changing the pipeline shape.

---

## Legal boundaries (hard rules)

Allowed:
- Google Custom Search API (100 free queries/day)
- Bing Search API
- Wappalyzer API (technographics)
- Apollo API (people search, enrichment — within plan limits)
- Company public pages (about, careers, pricing, partners, integrations, case studies)
- Public job postings (GulfTalent, Bayt, LinkedIn Jobs public listings)
- Public funding / press pages (MAGNiTT, Crunchbase public, Wamda, ArabNews)
- Customer-provided CSVs
- Manual LinkedIn research (human-driven, browser, no automation)

Not allowed:
- LinkedIn scraping via bots or browser extensions
- Automated LinkedIn DM sending (violates ToS, risks account ban)
- Bypassing anti-bot systems
- Harvesting private/authenticated data
- Storing sensitive PII without operational need
- Mass email spam
- Deceptive outreach or impersonation

Every lead record **must include**:
- `source` — where the claim came from
- `source_type` — website | api | public_page | manual | customer_csv
- `reason` — why this lead is being suggested
- `confidence` — 0-100
- `recommended_channel` — LinkedIn_manual | email | partner_intro | phone | in_person
- `compliance_note` — short string stating legal basis

---

## Use cases (5 supported)

| Use case | Who | Signal priority | Recommended channel |
|----------|-----|-----------------|----------------------|
| `sales` | B2B decision-makers w/ budget | CRM + booking tool + hiring sales + paid ads + recent funding | LinkedIn manual, email |
| `partnership` | agencies, integrators, resellers | agency service + SME customer base + retainer model + complementary tech | LinkedIn manual, partner form |
| `collaboration` | founders, creators, thought leaders | public content on sales/growth + newsletter + podcast + community | LinkedIn manual, email |
| `investor` | VCs, angels active in MENA SaaS/AI | portfolio overlap + recent thesis posts + MENA mandate | warm intro, LinkedIn manual |
| `b2c_audience` | consumer audiences | demographics + behavior + purchase channels | paid ads, WhatsApp broadcast, content |

Each use case has a different scoring weight profile defined in [ICP_SCORING_MODEL.md](./ICP_SCORING_MODEL.md).

---

## API surface (shipped)

```
POST /api/v1/prospect/discover
  body: {"icp": str, "use_case": str, "count": int}
  returns: ProspectResult JSON (see LEAD_OUTPUT_SCHEMA.json)

POST /api/v1/prospect/demo
  returns: canned 3-lead preview for UI smoke test

GET  /api/v1/prospect/use-cases
  returns: {use_cases: {...}, max_count: 20}
```

---

## Evidence store (contract every field must honor)

```json
{
  "claim": "Foodics raised Series C at $170M in 2025",
  "source_url": "https://magnitt.com/...",
  "source_type": "public_page",
  "collected_at": "2026-04-24T15:40:00Z",
  "confidence": 85
}
```

Fields without a source must be `null`. No invented URLs. No invented phone numbers. No invented emails.

---

## Feedback loop (the moat)

Every lead that moves through outreach stages writes back:
- `sent_at` — when outreach went out
- `replied_at` + `reply_sentiment` — positive / neutral / negative
- `demo_booked_at`
- `paid_at` + `revenue_sar`
- `lost_reason` — objection category

This data flows back into:
- Signal weights (which signals actually predict conversion?)
- Message angles (which openings actually got replies?)
- Segment priority (which segments closed fastest?)

**This is the sovereign layer.** Apollo has 300M contacts; we have the ground-truth feedback loop for the Saudi/GCC B2B market.

---

## Product positioning

> **Arabic-first Lead Intelligence + AI Sales Operations layer for companies and agencies that need to qualify leads, book demos, follow up, and convert inbound/outbound interest into revenue.**

Not: generic chatbot · scraping tool · AI-for-everything · spam machine.

Differentiators:
1. Arabic-first GTM (Saudi Khaliji dialect output by default)
2. Saudi/GCC signal intelligence (local CR, local hiring boards, local funding press)
3. Manual-to-automation ops model (ship by hand, automate what works)
4. Agency/reseller motion (built-in commission model, white-label path)
5. Evidence-backed lead scoring (every claim has a source)
6. Payment + onboarding workflow (Moyasar automated + manual fallback)
7. Founder-led launch engine (sovereign dataset grows with every outreach)
8. Legally safer sourcing (no scraping lock-in risk)

---

## Files in this directory

- [SIGNAL_TAXONOMY.md](./SIGNAL_TAXONOMY.md) — the signal dictionary by use case
- [ICP_SCORING_MODEL.md](./ICP_SCORING_MODEL.md) — 100-point scoring model with weights
- [LEAD_OUTPUT_SCHEMA.json](./LEAD_OUTPUT_SCHEMA.json) — canonical JSON schema
- [TOP_10_SCORED.csv](./TOP_10_SCORED.csv) — today's top 10 leads scored by this model
- [CONNECTOR_ENV_VARS.md](./CONNECTOR_ENV_VARS.md) — required env vars when upgrading connectors
