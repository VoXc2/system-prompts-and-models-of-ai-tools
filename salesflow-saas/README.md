# Dealix — AI Revenue Operating System

نظام تشغيل الإيرادات بالذكاء الاصطناعي للمنشآت السعودية الصغيرة والمتوسطة

## Architecture

```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  Nginx  │────▶│ Next.js  │     │ PostgreSQL│
│  :80    │     │  :3000   │     │  :5432    │
│  :443   │     └──────────┘     └───────────┘
│         │                            ▲
│         │     ┌──────────┐           │
│         │────▶│ FastAPI  │───────────┘
│         │     │  :8000   │───┐
└─────────┘     └──────────┘   │  ┌───────┐
                    ▲          └──│ Redis │
                    │             │ :6379 │
              ┌─────┴────┐       └───────┘
              │  Celery   │          ▲
              │ Worker(s) │──────────┘
              │  + Beat   │
              └──────────┘
```

**Stack:**
- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL 16 + Redis 7
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS
- **Workers**: Celery + Redis (queues: default, ai, sequences)
- **Proxy**: Nginx with security headers
- **AI**: OpenAI / Anthropic / Gemini (configurable)
- **Messaging**: WhatsApp Business API + Email (SMTP/SendGrid) + SMS (Unifonic)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/VoXc2/system-prompts-and-models-of-ai-tools.git
cd system-prompts-and-models-of-ai-tools/salesflow-saas

# 2. Configure
cp .env.example .env
# Edit .env — set DB_PASSWORD, SECRET_KEY, and API keys

# 3. Launch
docker compose up -d --build

# 4. Verify
curl http://localhost:8000/api/v1/health
```

## Project Structure

```
salesflow-saas/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 25 API route modules
│   │   ├── models/          # 27 SQLAlchemy models
│   │   ├── services/        # 18 business logic services
│   │   ├── workers/         # Celery async tasks
│   │   ├── integrations/    # WhatsApp, Email, SMS, Social
│   │   ├── utils/           # Hijri calendar, phone, security
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings (100+ vars)
│   │   └── database.py      # SQLAlchemy async engine
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages (App Router)
│   │   ├── components/      # Reusable UI components
│   │   └── lib/api.ts       # Type-safe API client
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf           # Reverse proxy + security headers
├── docker-compose.yml        # 7 services orchestration
├── Makefile                  # Dev shortcuts
└── .env.example              # 87 environment variables
```

## Key Features

- **Multi-tenant CRM** — leads, deals, contacts, pipeline
- **AI Sales Agents** — auto-discover, qualify, outreach
- **WhatsApp Business** — two-way messaging with templates
- **Voice AI** — Saudi Arabic voice profiles (Khalid/Noura)
- **Appointment Booking** — with WhatsApp reminders
- **Proposals & Contracts** — AI-generated with e-sign
- **Analytics** — pipeline, revenue, conversion tracking
- **PDPL Compliance** — consent ledger, data subject rights

## API Documentation

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI: `http://localhost:8000/api/openapi.json`

## Development

```bash
make up              # Start all services
make down            # Stop all services
make logs            # View logs
make logs-backend    # Backend + Celery logs
make test            # Run pytest
make migrate         # Run Alembic migrations
make migration msg="add_new_table"  # Create migration
make shell           # Interactive Python shell
make health          # Check API health
```

## Environment Variables

See `.env.example` for all 87 configurable variables covering:
- Database, Redis, Security
- WhatsApp, Email, SMS providers
- AI providers (OpenAI, Anthropic, Gemini)
- Lead generation APIs (Apollo, Hunter)
- Voice AI (VAPI)
- Social media integrations
- Agent rate limits

## Security

- JWT authentication with configurable expiry
- Rate limiting (slowapi)
- Non-root Docker containers
- Nginx security headers (CSP, X-Frame-Options, etc.)
- No hardcoded secrets — all via environment variables
- PDPL consent management
