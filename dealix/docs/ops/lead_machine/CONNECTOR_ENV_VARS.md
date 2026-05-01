# Connector Env Vars — when you're ready to upgrade the machine

v1 ships without paid connectors (LLM-native). Add these env vars in Railway → Variables to unlock each connector.

---

## Google Custom Search API

**Purpose:** real-time web discovery of Saudi companies, press, job posts, partner pages.

| Env var | Where to get it | Notes |
|---------|-----------------|-------|
| `GOOGLE_SEARCH_API_KEY` | https://console.cloud.google.com/apis/credentials → Create API key | Enable "Custom Search API" on the project first |
| `GOOGLE_SEARCH_CX` | https://programmablesearchengine.google.com → Create engine → copy the "cx" ID | Configure to search the entire web, enable "Image search" off |

**Free tier:** 100 queries/day. Paid: $5 per 1K queries after that (up to 10K/day).

**Cost estimate for Dealix:** with 5-10 queries per lead and 20 leads/day → 100–200 queries/day → mostly within free tier.

---

## Technographics — Dealix native detector (FREE, no API key needed)

**Purpose:** detect which tools a target uses (HubSpot, Calendly, Shopify, Intercom, Meta Pixel, Moyasar, Salla, etc.) — the strongest intent signal.

**Shipped:** `auto_client_acquisition/connectors/tech_detect.py` — native detector that covers the ~45 tools that matter for Dealix (Saudi-tuned, B2B-focused).

**Usage via API (public, no auth):**
```bash
curl -X POST https://api.dealix.me/api/v1/prospect/enrich-tech \
  -H "Content-Type: application/json" \
  -d '{"domain":"foodics.com"}'
```

**Usage via CLI:**
```bash
python -m auto_client_acquisition.connectors.tech_detect foodics.com
```

**Cost:** 0 SAR · **Lookup:** ~2-5 seconds · **API keys:** none.

### Categories covered

Booking (Calendly, HubSpot Meetings, Chili Piper, Cal.com) · CRM (HubSpot, Salesforce, Pipedrive, Zoho, ActiveCampaign, Marketo) · Payments MENA (**Moyasar, Tap, PayTabs, HyperPay**) + global (Stripe, PayPal, Checkout.com) · E-commerce MENA (**Salla, Zid**) + global (Shopify, WooCommerce, Magento, BigCommerce) · Chat (Intercom, Zendesk, Crisp, LiveChat, Tawk + **WhatsApp Widget**) · Analytics/Ads (GTM, GA4, Meta Pixel, TikTok Pixel, Snapchat Pixel, LinkedIn Insight, Hotjar, PostHog, Mixpanel, Segment, Google Ads) · Forms (Typeform, Jotform, HubSpot Forms, Formspree, Google Forms) · CMS (WordPress, Webflow, Wix, Next.js, Framer).

### Why native over Wappalyzer

| Option | Cost | Coverage | Saudi focus | Dealix fit |
|--------|------|----------|-------------|------------|
| **Dealix native** (shipped) | **0** | ~45 tools (the important ones) | ✅ Moyasar/Tap/Salla/Zid built-in | ✅ best |
| Wappalyzer hosted API | $100+/mo | 2500+ | ❌ no MENA specificity | overkill for v1 |
| `python-Wappalyzer` (self-host) | 0 | 2000+ | ❌ generic rules | fine if want breadth |
| `webappanalyzer` fork | 0 | 2000+ (2024 rules) | ❌ generic | fine if want breadth |
| BuiltWith API | $295+/mo | 70K+ | ❌ | enterprise only |

**For Dealix v1:** native is enough. Add `python-Wappalyzer` as a fallback later if broader coverage becomes important.

### When to upgrade to hosted Wappalyzer

Only if:
- Crossing 500 lookups/day (native is CPU-cheap but hosted parallelizes better)
- Need technographics on domains the native misses (e.g. obscure eastern-European CRMs)
- Clients require a "third-party-verified" data provenance

Until then: native.

---

## Apollo API

**Purpose:** find decision-makers by role + seniority + geography. Optional enrichment (email, phone) within plan.

| Env var | Where to get it |
|---------|-----------------|
| `APOLLO_API_KEY` | Apollo.io → Settings → API |

**Pricing:** Free tier limited; paid plans from $49/user/mo.

**Dealix pattern:** use People Search only (no email reveals) unless explicitly needed; stay within plan.

---

## Moyasar (already wired)

| Env var | Status |
|---------|--------|
| `MOYASAR_SECRET_KEY` | ⚠️ Sami to re-verify after KYC activation — see `MOYASAR_HOSTED_CHECKOUT.md` |
| `MOYASAR_WEBHOOK_SECRET` | ✅ Set in Railway |

---

## Optional: Saudi-specific sources

### CR (Commercial Registration) lookup
Public SP portal: https://www.mc.gov.sa/ar/eservices/Pages/ShowServiceDetails.aspx — manual lookup only (no public API). Use for validation, not bulk.

### Monsha'at / SME Authority
https://www.monshaat.gov.sa — public lists of SMEs that joined programs. Manual discovery.

### GOSI (public-sector contractor list)
Public contractor directory. Only use for B2G pathway.

### Wamda / MAGNiTT press
https://www.wamda.com , https://magnitt.com — public press and startup pages. Use `site:` queries via Google Custom Search.

---

## Setup order recommendation

1. **First week:** v1 LLM-native (no connectors) — validate product-market fit
2. **After 5 paying customers:** add `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_CX` (free tier covers you)
3. **After 10 customers:** add `WAPPALYZER_API_KEY` ($100/mo pays back with better targeting)
4. **After 20 customers or partner launch:** add `APOLLO_API_KEY` (when volume justifies)

Do not pay for connectors until v1 proves value.
