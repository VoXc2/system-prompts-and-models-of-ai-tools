# API Reference — Dealix v3.0.0

Base URL (prod): `https://api.dealix.sa`

## المصادقة
```
X-API-Key: <your-key>
```
عدا مسارات `/health*`, `/docs`, `/redoc`, `/openapi.json`, `/api/v1/webhooks/*`.

---

## Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + providers |
| GET | `/live` | Liveness probe |
| GET | `/ready` | Readiness probe |
| GET | `/health/deep` | Deep check (Postgres + Redis + LLM) |

## Leads
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/leads` | Create new lead (10/min) |
| GET | `/api/v1/leads` | List leads |
| GET | `/api/v1/leads/{id}` | Get one |
| PATCH | `/api/v1/leads/{id}` | Update status |

## Sales
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/sales/quote` | Generate proposal (30/min) |
| POST | `/api/v1/sales/book` | Book demo |
| POST | `/api/v1/sales/follow-up` | Trigger follow-up |

## Sectors
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/sectors` | List supported sectors |
| GET | `/api/v1/sectors/{slug}/playbook` | Sector playbook |

## Agents
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/agents/run` | Execute an agent |
| GET | `/api/v1/agents/list` | Available agents |

## Webhooks
| Method | Path | Verification |
|--------|------|--------------|
| POST | `/api/v1/webhooks/hubspot` | HMAC-SHA256 (X-HubSpot-Signature-v3) |
| POST | `/api/v1/webhooks/calendly` | HMAC-SHA256 (Calendly-Webhook-Signature) |
| POST | `/api/v1/webhooks/n8n` | HMAC-SHA256 (X-N8N-Signature) |
| POST | `/api/v1/webhooks/whatsapp` | WhatsApp token verify |

## Admin
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/admin/costs?window_hours=24&group_by=model` | Cost aggregation |
| GET | `/api/v1/admin/cache/stats` | Semantic cache hit/miss |
| GET | `/api/v1/admin/audit?limit=200` | Connector audit log |

## Rate Limits
ارجع إلى `docs/SECURITY_GUIDE.md`.
