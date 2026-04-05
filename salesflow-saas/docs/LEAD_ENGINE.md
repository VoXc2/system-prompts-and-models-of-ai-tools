# Revenue Lead Engine (Dealix)

**Integration:** Extends existing `Lead` (`score`, `extra_metadata.lead_engine`) without breaking CRM APIs.  
**Compliance:** Lawful business signals only; buying committee rows are **role templates**, not fabricated people.

## Existing assets (pre-upgrade)

- `Lead`, `Prospect`, `TrustScore`
- `lead_intelligence_engine.py` (Places, SerpAPI, CSE, dedupe)
- `ProspectingService` / `/prospecting/hunt`, `/prospector/*`

## New modules

| Area | Location |
|------|----------|
| Persistence | `app/models/lead_engine.py` |
| ICP presets | `services/lead_engine/icp.py` |
| Scoring / routing | `scoring.py`, `playbooks.py` |
| Stakeholders | `stakeholders.py` (roles only) |
| Orchestrator | `orchestrator.py` |
| API | `/api/v1/lead-engine/*` |
| Schedule | `workers/lead_engine_tasks.py` (opt-in) |

## API (JWT + owner|admin|manager)

- `POST /lead-engine/recompute/{lead_id}` — full pipeline
- `GET /lead-engine/intel/{lead_id}` — latest score + routing
- `GET /lead-engine/summary` — top accounts by score
- `POST /lead-engine/icp/seed-defaults` — tenant ICP profiles
- `POST /lead-engine/source-events` — audit trail for lawful ingestion
- `POST /lead-engine/learning/outcome` — won/lost/meeting…

## Flags

- `DEALIX_LEAD_ENGINE_ENABLED` (default true)
- `DEALIX_LEAD_ENGINE_SCHEDULE_ENABLED` (default false) — daily batch rescore

## Events

`lead.engine.scored` via `emit_domain_event` for Brain/memory.

## Next steps

- Wire enrichment facts from vendor APIs into `LeadEngineEnrichmentFact`.
- Tune weights from `LeadEngineLearningEvent` aggregates.
- Dashboard UI under `/dashboard` when prioritized.
