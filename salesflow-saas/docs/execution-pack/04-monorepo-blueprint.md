# Monorepo Blueprint

## Current Structure (Active Build)

```
salesflow-saas/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/            # API route handlers (37 files)
│   │   ├── models/            # SQLAlchemy models (32 files, 35 tables)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer (22 services)
│   │   ├── workers/           # Celery task workers
│   │   ├── utils/             # Shared utilities (security, etc.)
│   │   ├── migrations/        # Alembic migration versions
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # DB engine + session factory
│   │   └── main.py            # FastAPI app factory
│   ├── tests/                 # Backend test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Next.js 15 application
│   ├── src/
│   │   ├── app/               # App router pages
│   │   │   ├── (dashboard)/   # Authenticated dashboard pages
│   │   │   └── (auth)/        # Login/register pages
│   │   ├── components/        # Reusable React components
│   │   └── lib/               # API client, utilities
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docs/                       # Documentation
│   └── execution-pack/        # Strategic execution documents
├── docker-compose.yml
├── Makefile
└── CLAUDE.md                  # AI assistant context
```

## Target Structure (Evolution Path)

```
dealix/
├── apps/
│   ├── web/                   # Next.js frontend (current frontend/)
│   ├── api/                   # FastAPI backend (current backend/)
│   ├── worker/                # Celery workers (extracted from backend)
│   ├── operator/              # Internal operator console (future)
│   └── docs-site/             # Public documentation site (future)
├── packages/
│   ├── ui/                    # Shared React components
│   ├── schemas/               # Shared Pydantic/Zod schemas
│   ├── shared-types/          # TypeScript type definitions
│   ├── config/                # Shared configuration
│   ├── widgets/               # Embeddable capture widgets
│   ├── workflow-engine/       # Sequence/state machine engine
│   ├── prompt-assets/         # AI prompt templates + eval datasets
│   ├── analytics-models/      # Analytics aggregation logic
│   ├── sdk-js/                # JavaScript SDK for integrations
│   ├── sdk-python/            # Python SDK for integrations
│   └── connector-core/        # Integration connector framework
├── infra/
│   ├── docker/                # Dockerfiles
│   ├── k8s/                   # Kubernetes manifests (future)
│   ├── terraform/             # Infrastructure as code (future)
│   └── scripts/               # Deployment scripts
├── docs/
│   ├── execution-pack/        # Strategic execution docs
│   ├── api/                   # API documentation
│   ├── guides/                # User/developer guides
│   └── runbooks/              # Operational runbooks
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── load/
└── scripts/
    ├── seed/                  # Database seeding
    ├── migrate/               # Migration helpers
    └── dev/                   # Developer tooling
```

## Migration Strategy
1. **Phase 1 (NOW)**: Keep current flat structure, complete core features
2. **Phase 2**: Extract shared schemas and types into packages/
3. **Phase 3**: Extract widgets and SDK into packages/
4. **Phase 4**: Split worker into separate app
5. **Phase 5**: Add operator console as separate app

## Directory Conventions

| Directory | Ownership | Naming |
|-----------|-----------|--------|
| `api/v1/*.py` | Backend team | `{resource}.py` (plural) |
| `models/*.py` | Backend team | `{entity}.py` (singular) |
| `services/*.py` | Backend team | `{service_name}.py` |
| `workers/*.py` | Backend team | `{task_type}_tasks.py` |
| `schemas/*.py` | Backend team | `{entity}.py` matching models |
| `app/(dashboard)/*/page.tsx` | Frontend team | kebab-case directories |
| `components/*.tsx` | Frontend team | PascalCase files |
| `docs/execution-pack/*.md` | Product/arch team | `{NN}-{slug}.md` |

## Artifact Ownership Rules
- Models define the source of truth for data shape
- Schemas define the API contract
- Services own business logic — routes are thin
- Workers own async execution — services dispatch, workers execute
- Frontend API client mirrors backend routes 1:1
- Docs are living artifacts, updated with every architectural decision
