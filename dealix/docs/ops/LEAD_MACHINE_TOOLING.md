# Dealix Lead Machine — Tooling Stack

The lead machine has 4 layers. Each layer activates by adding the env var to Railway.

## Layer 1 — Required for production

| Env var | Purpose | Fallback if missing |
|---|---|---|
| `DATABASE_URL` | Postgres for lead graph + queue | endpoints return `skipped_db_unreachable` |
| `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_CX` | Web discovery + ICP discovery | static (empty) results |
| `GROQ_API_KEY` | LLM for prospector + reply classifier | rules-only mode |
| `SENTRY_DSN` | Error monitoring | no observability |

## Layer 2 — Lead discovery power

| Env var | Unlocks | Chain priority |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | Google Places — local Saudi sectors (clinics, real-estate, training, agencies) | 1st in MapsProvider |
| `TAVILY_API_KEY` | Agent-grade search with summaries | 2nd in SearchProvider |
| `FIRECRAWL_API_KEY` | Markdown crawler with dynamic content | 1st in CrawlerProvider |
| `HUNTER_API_KEY` | Domain → public B2B emails + verification | 1st in EmailIntelProvider |
| `ABSTRACT_API_KEY` | Email verification (no domain search) | 2nd in EmailIntelProvider |

## Layer 3 — Channels

| Env var | Channel |
|---|---|
| `SENDGRID_API_KEY` + `SENDGRID_INBOUND_SECRET` | Inbound email parser |
| `WHATSAPP_PROVIDER`, `WHATSAPP_*` | WhatsApp BSP for inbound |
| `META_APP_SECRET` + `META_PAGE_ACCESS_TOKEN` | Meta Lead Forms |
| `GOOGLE_LEAD_FORM_WEBHOOK_KEY` | Google Lead Forms webhook |

## Layer 4 — Later (after first revenue)

| Env var | Purpose |
|---|---|
| `WAPPALYZER_API_KEY` | Tech detection breadth |
| `SERPAPI_API_KEY` | Backup search/maps |
| `APIFY_TOKEN` | Backup local discovery |

## Activation order

1. Fix `DATABASE_URL` — without it nothing persists.
2. Add `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_CX` — unlocks ICP discovery.
3. Add `GROQ_API_KEY` — unlocks LLM-quality messages.
4. Add `SENTRY_DSN` — catch errors before customers do.
5. Add `GOOGLE_MAPS_API_KEY` — unlocks the local Saudi engine (highest ROI sectors).
6. After first paying pilot: `FIRECRAWL_API_KEY` or `HUNTER_API_KEY`.
7. After 3 customers: channel APIs (SendGrid + WhatsApp BSP).

## Endpoints touching each layer

```
Layer 1 (DB + LLM + CSE + Sentry)
  /api/v1/data/import (+ normalize / dedupe / enrich / report)
  /api/v1/leads/discover/web
  /api/v1/prospect/discover (LLM)
  /api/v1/leads (intake pipeline)

Layer 2 (Maps + Crawler + EmailIntel)
  /api/v1/leads/discover/local
  /api/v1/leads/enrich/full
  /api/v1/leads/enrich/batch
  /api/v1/data/import/{id}/enrich

Layer 3 (Channels)
  /api/v1/integrations/google-lead-form
  /api/v1/integrations/meta-lead-form
  /api/v1/inbound/email
  /api/v1/inbound/whatsapp
  /api/v1/outreach/queue
  /api/v1/outreach/prepare-from-data
```

## Verifying the chain

```
GET /api/v1/prospect/search-diag
```

Returns `tier1_ready` and `tier2_ready` booleans plus per-key set/unset state.
Treat it as the canonical pre-flight check before claiming a deploy is live.
