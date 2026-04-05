# SEO Intelligence Engine (Dealix)

**Routes:** `/api/v1/seo-engine/*` (JWT + role `owner` | `admin` | `manager`).  
**Flags:** `DEALIX_SEO_ENGINE_ENABLED`, `DEALIX_SEO_PUBLIC_BASE_URLS`, `DEALIX_SEO_SCHEDULE_ENABLED`.

## Subsystems (implementation map)

| Subsystem | Module | Storage |
|-----------|--------|---------|
| Audit | `services/seo_engine/runner.py` + `http_fetch.py` | `SeoEngineRun`, `SeoSchemaFinding` |
| Competitor | `runner.run_competitor_refresh` | `SeoCompetitor.snapshot_json` |
| Keywords / gaps | `runner.run_keyword_and_gap_scan` | `SeoKeywordOpportunity`, `SeoContentGap` |
| Schema | `schema_builder.py` | `SeoSchemaFinding.proposed_jsonld` |
| Local SEO | city on drafts + gaps evidence | `SeoContentDraft.city` |
| Drafts | `create_content_brief_draft` | `SeoContentDraft` (`status=draft`) |
| Memory / events | `emit_domain_event` | `DomainEvent` + unified memory |
| Schedule | `workers/seo_tasks.py` | Celery beat 07:20 (no-op until schedule flag) |

## Safety

- No auto-publish; drafts only.
- No fake Review/AggregateRating in JSON-LD helpers.
- Competitor fetch uses short timeouts + identifiable User-Agent.

## Operations

```http
POST /api/v1/seo-engine/runs
{"run_kind": "full_pipeline", "options": {"seed_keywords": ["CRM", "مبيعات"]}}

POST /api/v1/seo-engine/competitors
{"domain": "example.com", "display_name": "Competitor A"}

POST /api/v1/seo-engine/drafts/brief
{"target_keyword": "أتمتة المبيعات", "city": "الرياض"}
```

## Follow-up

- Dedupe gaps/keywords by hash on repeated runs.
- Optional LLM layer behind feature flag for richer briefs.
- Frontend admin page under `/dashboard` when product prioritizes.
