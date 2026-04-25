# Dealix — Railway Environment Keys

**Where to add:** Railway → Project → Service "web" → Variables tab → Review → Deploy

---

## P0 — Required for Launch

| Variable | Source | Cost | Effect When Missing | Verification |
|----------|--------|------|-------------------|-------------|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) | Free tier available | LLM features degraded (rules-only) | `curl /api/v1/prospect/search-diag` shows `GROQ_API_KEY.set: true` |
| `GOOGLE_SEARCH_API_KEY` | [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) | 100 queries/day free | `/prospect/search` returns 503 | search-diag shows key set |
| `GOOGLE_SEARCH_CX` | Fixed value: `75ae2277dfd754a1a` | Free | Same as above | search-diag shows CX set |
| `SENTRY_DSN` | [sentry.io](https://sentry.io) → Create Python project → copy DSN | Free plan | No error alerting | Sentry receives test error |
| `POSTHOG_API_KEY` | [posthog.com](https://posthog.com) → Project Settings → API Key | Free plan | No funnel tracking | PostHog dashboard shows events |
| `POSTHOG_HOST` | `https://us.i.posthog.com` or `https://eu.i.posthog.com` | — | PostHog events go nowhere | Same as above |

## P1 — Required for Automated Payment

| Variable | Source | Cost | Effect When Missing |
|----------|--------|------|-------------------|
| `MOYASAR_SECRET_KEY` | [dashboard.moyasar.com](https://dashboard.moyasar.com) → API Keys | Per-transaction fee | Checkout returns 502 |
| `MOYASAR_PUBLISHABLE_KEY` | Same dashboard | — | Frontend checkout broken |
| `MOYASAR_WEBHOOK_SECRET` | Moyasar → Webhooks → Secret | — | Webhook signature validation fails |

**Note:** Moyasar keys appear to be set but checkout returns 502. See REVENUE_READINESS_CHECKLIST.md → Moyasar Diagnostic Checklist.

## P2 — Optional Enrichment (after first customer)

| Variable | Source | Effect When Missing |
|----------|--------|-------------------|
| `GOOGLE_MAPS_API_KEY` | Google Cloud → Maps → Places API | Local discovery disabled |
| `SENDGRID_API_KEY` | sendgrid.com | No automated email |
| `WHATSAPP_ACCESS_TOKEN` | Meta Business | No WhatsApp API |
| `HUBSPOT_API_KEY` | HubSpot → Private Apps | No CRM sync |
| `TAVILY_API_KEY` | tavily.com | No web crawl enrichment |

## Already Set (verified via search-diag)

| Variable | Status |
|----------|--------|
| `MOYASAR_SECRET_KEY` | Set (48 chars, sk_liv...) |
| `MOYASAR_WEBHOOK_SECRET` | Set (64 chars) |
| `MOYASAR_PUBLIC_KEY` | Set |
| `APP_URL` | Set |
| `DATABASE_URL` | Set (via Railway Postgres) |

---

## Critical Reminders

1. **Environment dropdown:** Make sure you're in environment "Dealix" (not "adventurous-tenderness" or other Agent branches)
2. **Service:** Variables go in service "web" (not Postgres or Redis)
3. **Deploy:** After adding variables, you MUST click Review → Deploy. Variables are staged until deployed.
4. **No secrets in chat:** Never paste API keys in any chat window. Add them directly in Railway.
