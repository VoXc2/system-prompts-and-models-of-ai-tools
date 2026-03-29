# Master Architecture Map

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js 15 + React 19 + Tailwind CSS | SSR, RTL-native, rapid iteration |
| API | FastAPI (Python 3.12+) | Async-first, type-safe, OpenAPI auto-docs |
| ORM | SQLAlchemy 2.0 (async) | Mature, migration-friendly, PostgreSQL-native |
| Database | PostgreSQL 16 | JSONB, full-text search, PITR, partitioning |
| Cache/Queue | Redis 7 | Pub/sub, rate limiting, session cache, Celery broker |
| Workers | Celery + Redis | Distributed task execution, scheduling |
| Migrations | Alembic | Versioned, reversible schema changes |
| Auth | JWT (access + refresh tokens) | Stateless, multi-tenant claims |
| File Storage | S3-compatible (MinIO local, AWS S3 prod) | Scalable object storage |
| AI | OpenAI / Anthropic (multi-provider) | Best-in-class models, provider fallback |
| Messaging | WhatsApp Business API, email (SMTP/SES) | Saudi market primary channels |
| Observability | Structured logging + traces | Production visibility |

## Multi-Tenant Architecture

```
Organization (billing entity)
  └── Tenant (isolated data boundary)
       ├── Users (with roles/permissions)
       ├── Leads, Deals, Customers (tenant-scoped)
       ├── AI Agents (tenant-configured)
       ├── Integrations (tenant credentials)
       ├── Sequences, Templates (tenant-owned)
       └── Workspace settings, branding
```

### Tenant Isolation Rules
- Every model with business data inherits `TenantModel` (includes `tenant_id`)
- Every DB query MUST filter by `tenant_id`
- Cross-tenant queries are NEVER allowed in application code
- Operator access uses elevated permissions, not cross-tenant queries
- Background workers receive `tenant_id` in task payload

## API Architecture

```
/api/v1/
├── auth/           # Login, register, refresh, me
├── tenant/         # Tenant settings, branding
├── users/          # User management
├── leads/          # Lead CRUD, scoring, assignment
├── customers/      # Customer management
├── deals/          # Deal CRUD, pipeline
├── activities/     # Activity timeline
├── conversations/  # Multi-channel messaging
├── messages/       # Message management
├── appointments/   # Booking, calendar
├── sequences/      # Automated workflows
├── ai/             # AI agents, traces, governance
├── analytics/      # Reports, velocity, forecasting
├── campaigns/      # Marketing campaigns
├── contracts/      # Contract management
├── proposals/      # Proposal management
├── notifications/  # User notifications
├── integrations/   # Connected services
├── webhooks/       # Incoming webhooks
├── social/         # Social listening
├── suppression/    # Do-not-contact list
├── consents/       # PDPL consent management
├── growth-events/  # Attribution tracking
├── audit-logs/     # Audit trail
├── subscription/   # Plan management
├── playbooks/      # Industry playbooks
├── sla/            # SLA policies and breaches
├── files/          # File uploads
├── branding/       # White-label settings
├── tags/           # Tags and segments
├── custom-fields/  # Custom field definitions
├── forms/          # Public forms (no auth)
└── voice/          # Voice AI
```

## Worker Architecture

| Worker | Responsibility | Schedule |
|--------|---------------|----------|
| sequence_worker | Execute sequence steps, check enrollments | Every 60s |
| social_listener | Check listening streams, draft comments | Per stream interval |
| reminder_worker | Send appointment/follow-up reminders | Every 5min |
| analytics_worker | Aggregate metrics, compute velocity | Every 15min |
| cleanup_worker | Expire tokens, archive old data | Daily |

## Data Flow

```
Capture (forms/widgets/API/webhook/import)
  → Dedupe + Enrich
    → Score + Qualify (AI)
      → Route + Assign
        → Sequence enrollment
          → Follow-up execution
            → Meeting/Proposal
              → Close (won/lost)
                → Attribution + Analytics
```

## Security Boundaries
1. **Auth boundary** — JWT validation on every request
2. **Tenant boundary** — tenant_id filter on every query
3. **Role boundary** — RBAC check on mutation endpoints
4. **Rate limit boundary** — slowapi on auth + public endpoints
5. **Consent boundary** — Suppression check before any outreach
6. **AI boundary** — Every AI call logged with cost and approval status
