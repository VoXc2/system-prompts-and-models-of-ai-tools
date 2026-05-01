# API Reference

**Interactive Swagger UI**: `http://localhost:8000/docs`
**ReDoc**: `http://localhost:8000/redoc`
**OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Authentication

The current version ships **without auth on the public API** — add your own layer (API key header, JWT, OAuth) behind a reverse proxy for production.

Recommended: use a simple API key via middleware, or Cloudflare Access / Auth0 in front.

---

## Endpoints

### Root & Health

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Service info |
| GET | `/health` | Full health including configured LLM providers |
| GET | `/ready` | Readiness probe |
| GET | `/live` | Liveness probe |

---

### Leads (Phase 8)

#### POST `/api/v1/leads`

Run a lead through the **full acquisition pipeline**.

**Request** (`LeadCreateRequest`):
```json
{
  "company": "شركة التقنية المتقدمة",
  "name": "أحمد محمد",
  "email": "ahmed@example.sa",
  "phone": "+966501234567",
  "sector": "technology",
  "company_size": "medium",
  "region": "Saudi Arabia",
  "budget": 50000,
  "message": "نحتاج نظام AI لإدارة المبيعات",
  "source": "website"
}
```

**Query parameters**:
- `auto_book: bool = true`
- `auto_proposal: bool = false`

**Response** (`PipelineResponse`):
```json
{
  "lead": { "id": "lead_...", "fit_score": 0.82, "status": "qualified", ... },
  "fit_score": { "overall_score": 0.82, "tier": "A", "reasons": [...], ... },
  "extraction": { "pain_points": [...], "urgency_score": 0.7, ... },
  "qualification": { "questions": [...], "bant_score": 0.5, ... },
  "crm_sync": { "synced": true, "contact_id": "...", "deal_id": "..." },
  "booking": { "provider": "calendly", "link": "https://calendly.com/...", ... },
  "proposal": null,
  "warnings": []
}
```

---

### Sales

#### POST `/api/v1/sales/script`

Get a bilingual sales script.

**Request** (`SalesScriptRequest`):
```json
{
  "sector": "technology",
  "locale": "ar",
  "script_type": "opener",
  "name": "أحمد",
  "company": "شركتكم"
}
```

**Script types**: `opener`, `follow_up_1`, `follow_up_2`, `demo_confirm`, `proposal_cover`.

#### POST `/api/v1/sales/proposal`

Generate a one-off proposal (outside the pipeline).

---

### Sectors (Phase 9)

#### GET `/api/v1/sectors/{sector}`

Deep intel for a single Saudi sector.

**Path**: `sector` — one of: `technology`, `real_estate`, `healthcare`, `education`, `logistics`, `retail`, `finance`, `manufacturing`, `consulting`, `construction`, `oil_gas`, `tourism`.

**Query**: `enrich_with_llm=true` to add live LLM research on top of baseline.

#### GET `/api/v1/sectors/best/opportunity`

Returns the sector with the highest `growth_rate × ai_readiness`.

#### GET `/api/v1/sectors/target/list`

Top 5 target sectors.

#### POST `/api/v1/sectors/content`

Generate a content piece for a sector topic.

**Request**:
```json
{
  "topic": "أفضل 3 استخدامات AI في قطاع الصحة السعودي",
  "content_type": "article",
  "channel": "blog",
  "locale": "ar",
  "length": 800
}
```

---

### Agents (direct execution, useful for testing)

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/agents/intake` | Run just the Intake agent |
| POST | `/api/v1/agents/pain-extractor` | Run just the Pain extractor |
| POST | `/api/v1/agents/icp-match` | Run Intake + ICP |
| POST | `/api/v1/agents/research` | Run a market research question |

---

### Webhooks

#### GET / POST `/api/v1/webhooks/whatsapp`

Meta WhatsApp Cloud API webhook.
- `GET`: verification handshake (requires `hub.mode`, `hub.verify_token`, `hub.challenge`)
- `POST`: incoming messages — auto-routed through the acquisition pipeline

Verifies `X-Hub-Signature-256` HMAC if `WHATSAPP_APP_SECRET` is configured.

#### POST `/api/v1/webhooks/calendly`

Calendly event lifecycle notifications.

#### POST `/api/v1/webhooks/hubspot`

HubSpot subscription events.

---

## Error format

All `AICompanyError` subclasses map to 400:
```json
{
  "error": "IntegrationError",
  "detail": "HUBSPOT_ACCESS_TOKEN not configured"
}
```

Validation errors return 422 with FastAPI's default format.

---

## Rate limiting

Not enabled by default. Recommended: `slowapi` middleware or an upstream proxy (nginx, Cloudflare).

---

## cURL examples

```bash
# Submit a lead
curl -X POST http://localhost:8000/api/v1/leads \
  -H "Content-Type: application/json" \
  -d @examples/lead_payload.json

# Get Arabic opener script
curl -X POST http://localhost:8000/api/v1/sales/script \
  -H "Content-Type: application/json" \
  -d '{"sector":"healthcare","locale":"ar","script_type":"opener","name":"د. أحمد"}'

# Get healthcare sector intel with LLM enrichment
curl 'http://localhost:8000/api/v1/sectors/healthcare?enrich_with_llm=true'

# Best opportunity
curl http://localhost:8000/api/v1/sectors/best/opportunity
```
