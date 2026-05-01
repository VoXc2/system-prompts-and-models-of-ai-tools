# Saudi B2B Data Source Catalog

Curated list of Saudi business directory sources — **legality-graded** for Dealix ingestion.

**Hard rule:** never ingest a source unless its `recommended_use` is `green` or `yellow`. Red-flagged sources fall outside Dealix policy and don't go into the Data Lake.

## Source rating system

| Color | Meaning | Ingestion |
|---|---|---|
| 🟢 Green | Public + clearly permissive | Direct ingest with `source_type=public` |
| 🟡 Yellow | Public but ToS-sensitive | Ingest only company-level data; require manual approval; cite source |
| 🔴 Red | Scraping forbidden, paywalled-without-allowed-use, or platform-restricted | Do NOT ingest |

## 1. Saudi Chambers of Commerce (Official) 🟢

| Source | URL | Coverage | Access |
|---|---|---|---|
| Riyadh Chamber Member Directory | chamber.org.sa | Riyadh members | Public business directory |
| Jeddah Chamber Member Directory | jcci.org.sa | Jeddah members | Public business directory |
| Asharqia (Eastern Province) Chamber | chamber.org.sa/eastern | Dammam/Khobar/Jubail | Public business directory |
| Madinah Chamber | mcci.org.sa | Madinah | Public business directory |
| Makkah Chamber | mcc.org.sa | Mecca | Public business directory |
| Federation of Saudi Chambers | csc.org.sa | National | Public business directory |

**Why green:** These are public chambers serving members; member directories are explicitly published for business networking.

**Ingest plan:** crawl with `requests_bs4` provider → extract company name, sector, contact info → import as `source_type=public`, `source_name=chamber_<city>_<year_month>`, `allowed_use=business_contact_research_only`.

## 2. Government / Open Data 🟢

| Source | URL | Coverage |
|---|---|---|
| SDAIA Open Data Portal | data.gov.sa | National datasets, business registry samples |
| MCI (Ministry of Commerce) public registry | mci.gov.sa | Commercial registrations |
| MISA (Investment) license registry | misa.gov.sa | Foreign-investment-licensed entities |
| ZATCA taxpayer registry (limited) | zatca.gov.sa | VAT-registered entities (lookups only) |

**Why green:** Government open-data programs publish business-registry-style datasets explicitly for reuse.

## 3. Trade Associations 🟢

| Source | Sector |
|---|---|
| Saudi Real Estate Refereeing Center | real estate |
| Saudi Contractors Authority | construction |
| Saudi Tourism Authority registry | hospitality, events |
| Saudi Authority for Data and AI vendor catalog | tech |

## 4. Saudi Business Directory Websites 🟡

| Source | Notes |
|---|---|
| daleel-saudi.com | Yellow — public listings, but ToS limits bulk export. Ingest individual lookups only. |
| saudisteps.com | Yellow — sector-specific directories |
| arabbusinessguide.com | Yellow — pan-GCC, includes Saudi |

**Ingestion rule:** lookup individual companies for enrichment, not bulk download.

## 5. Map Data via Google Places 🟢

Already wired into Dealix as `MapsProvider`. Per Google Maps Platform terms:
- Store `place_id` (allowed)
- Store internal scores + Dealix-derived metadata
- Refresh place details on demand
- Display Google attribution where shown to end users

Treat Google Places as the **canonical real-time enrichment source** for sectors where directory coverage is thin (clinics, salons, gyms, training centers).

## 6. LinkedIn 🔴 — DO NOT SCRAPE

LinkedIn explicitly prohibits automated data collection. Dealix uses LinkedIn for:
- Manual research only
- Manual message sending only
- Never for data ingestion

## 7. Paid B2B Vendors (Procurement Channel) 🟡

When you eventually buy data, demand from the vendor:
1. `source_documentation` — where each row came from
2. `collection_method` — how it was gathered
3. `allowed_use` clause in writing
4. `last_updated` timestamp per row
5. Sample of 100 rows for the audit script BEFORE you pay
6. Refund clause if acceptance rate < 80%

Reject vendors who can't answer all 6.

Indicative Saudi/MENA vendors (always vet):
- ZoomInfo (paid; check Saudi coverage)
- Apollo.io (paid; check Saudi coverage; Dealix already has Apollo plugin scaffolding)
- Common Room (paid; check Saudi coverage)
- Local Saudi data brokers (vet very carefully)

## 8. Customer-Owned Data 🟢

Best source. When a Dealix customer signs up:
- Their CRM export
- Their website form submissions
- Their old email lists (with consent record)

Always classify as `source_type=owned` and `consent_status=owned`.

## Ingestion priority order

```
1. Customer-owned (green)
2. Chamber directories (green)
3. Government open data (green)
4. Google Places (green via MapsProvider)
5. Saudi business directory websites (yellow — lookup only)
6. Trade associations (green)
7. Paid vendors (yellow — vet thoroughly)
8. LinkedIn (red — manual only, never ingest)
```

## Anti-patterns

- ❌ Scraping behind login walls
- ❌ Reusing leaked databases
- ❌ Buying lists "without source documentation"
- ❌ Mixing sources in one import without `source_type` per row
- ❌ Treating personal-domain emails (gmail/hotmail) as business contact under PDPL legitimate-interest

## Quarterly review

Every quarter, audit the Data Lake:
1. Sources by `source_type` count
2. Average `data_quality_score` per source
3. Reply rate per source (after first month live)
4. Suppression hits per source (proxy for spam complaints)
5. Drop sources with poor quality or compliance flags
