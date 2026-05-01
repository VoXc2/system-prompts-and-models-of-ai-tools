# Provider Adapters

Dealix abstracts external services behind Protocol-based providers with chains.
Each chain falls back gracefully — endpoints never 500 because of a missing API key.

## Chains

| Surface | Chain (priority order) | Always-available fallback |
|---|---|---|
| **SearchProvider** | `GoogleCSEProvider` → `TavilyProvider` → `StaticSearchProvider` | static |
| **MapsProvider** | `GooglePlacesProvider` → `SerpApiMapsProvider`* → `ApifyMapsProvider`* → `StaticMapsProvider` | static |
| **CrawlerProvider** | `FirecrawlProvider` → `RequestsBs4Provider` | bs4 |
| **TechProvider** | `InternalTechProvider` (always) → `WappalyzerProvider` (merge) | internal |
| **EmailIntelProvider** | `HunterProvider` → `AbstractEmailProvider` → `NoopEmailIntelProvider` | noop |

`*` = stub adapters (env-gated, not implemented). They disappear from the chain
when their env vars are unset, so they don't slow anything down.

## Adding a provider

1. Implement the Protocol (e.g. `SearchProvider`) in
   `auto_client_acquisition/providers/<surface>.py`.
2. Implement `is_available()` — return `True` only if env vars exist.
3. Implement the work method (e.g. `async search(...)`) returning a `ProviderResult`.
4. Insert into `get_<surface>_chain()` at the right priority.
5. Document the new env var in `docs/ops/ENV_UNLOCK_MATRIX.md` and `.env.example`.
6. Verify the chain via `/api/v1/prospect/search-diag`.

## ProviderResult contract

```python
ProviderResult(
    provider="google_cse",
    status="ok" | "no_key" | "http_error" | "timeout" | "empty" | "unsupported",
    data={...},          # provider-specific
    error="...",         # only on failure
    fetched_at=ISO-8601,
)
```

`status="ok"` is the only state that stops the chain. Anything else falls through.

## Where chains run

| Endpoint | Chain |
|---|---|
| `POST /api/v1/leads/discover/local` | MapsProvider |
| `POST /api/v1/leads/discover/web` | SearchProvider |
| `POST /api/v1/leads/enrich/full` | Crawler + Tech + EmailIntel |
| `POST /api/v1/data/import/{id}/enrich` | Same as enrich/full |

## Diagnostics

`GET /api/v1/prospect/search-diag` reports which env vars are set (length only,
no values), and emits `tier1_ready` / `tier2_ready` flags so you can see which
chains will actually do real work in production.
