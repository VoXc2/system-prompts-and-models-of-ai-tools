# Dealix GTM OS — Data Sources Policy

## Allowed Sources

| Source | Type | Usage | Risk |
|--------|------|-------|------|
| Uploaded company files (Excel/CSV) | User data | Primary targeting | Low |
| Public company websites | Public | Research + enrichment | Low |
| Google Programmable Search | Official API | Web search | Low |
| Tavily | AI search API | Structured web results | Low |
| Official social media APIs | Official | Inbound + public data | Low |
| CRM data | Internal | Lead tracking | Low |
| Inbound messages | Opt-in | Customer conversations | Low |
| Manual imports by Sami | User action | Ad-hoc targeting | Low |
| Public business directories | Public | Company discovery | Low |

## Prohibited Sources

| Source | Reason |
|--------|--------|
| LinkedIn scraping/crawling | Platform ToS violation |
| Instagram profile scraping | Platform ToS violation |
| Purchased email/phone lists | Privacy + spam risk |
| Unauthorized data brokers | Legal risk |
| Scraping restricted websites | ToS violation |
| Personal data without consent | PDPL violation |

## Rules
1. Every data point must have a traceable source
2. No invented/hallucinated company data
3. No personal data collection without legitimate basis
4. All enrichment from public or API-approved sources only
5. User can request deletion of their data
