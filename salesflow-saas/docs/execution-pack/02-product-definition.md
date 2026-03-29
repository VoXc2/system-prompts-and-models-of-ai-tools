# Product Definition

## Product Name
**Dealix Revenue OS**

## Product Modes

### 1. SaaS Mode (Self-Serve)
- Tenant signs up, configures pipeline, imports leads
- AI agents available based on plan tier
- Self-serve onboarding checklist
- Usage-based limits on AI calls, messages, seats

### 2. Managed Service Mode
- Dealix operator configures and operates the tenant
- Client gets read-only dashboards + approval queues
- Operator has elevated permissions within client tenant
- SLA tracking between Dealix and client

### 3. White-Label Mode
- Partner gets their own branding (logo, colors, domain)
- Partner manages their own clients (sub-tenants)
- Partner sees aggregate dashboards across clients
- Dealix invisible to end clients

### 4. API/Embedded Mode
- Headless API access
- Embeddable widgets (forms, booking, chat)
- Webhook-driven integration
- SDK for custom frontends

## Core Modules

| Module | Description | Priority |
|--------|-------------|----------|
| Auth & Tenancy | Multi-tenant, RBAC, entitlements | P0 |
| Lead Management | Capture, score, qualify, route | P0 |
| Pipeline & Deals | Stages, velocity, forecasting | P0 |
| Conversations | Multi-channel messaging hub | P0 |
| Sequences | Automated follow-up workflows | P0 |
| AI Agents | 20+ governed revenue agents | P0 |
| Analytics | Attribution, velocity, forecasting | P0 |
| Appointments | Booking, reminders, calendar sync | P1 |
| Proposals & Contracts | Generate, send, track, sign | P1 |
| Social Listening | Monitor, draft, approve, engage | P1 |
| Content Engine | AI-assisted content creation | P1 |
| Integrations | WhatsApp, calendars, CRMs, webhooks | P0 |
| Compliance | Consent, suppression, PDPL, audit | P0 |
| Operator Console | Internal management dashboard | P0 |
| Widget SDK | Embeddable capture components | P1 |
| White-Label | Branding, custom domains | P2 |

## System Layers

```
┌─────────────────────────────────────────────┐
│              Frontend Layer                  │
│    Next.js 15 / React 19 / Tailwind RTL     │
├─────────────────────────────────────────────┤
│              API Layer                       │
│         FastAPI / REST + WebSocket           │
├─────────────────────────────────────────────┤
│            Service Layer                     │
│   Business logic, state machines, policies   │
├─────────────────────────────────────────────┤
│           AI Governance Layer                │
│  Agent registry, prompts, evals, approvals   │
├─────────────────────────────────────────────┤
│            Worker Layer                      │
│     Celery tasks, sequences, schedulers      │
├─────────────────────────────────────────────┤
│            Data Layer                        │
│   PostgreSQL 16 / Redis 7 / S3-compatible    │
├─────────────────────────────────────────────┤
│          Integration Layer                   │
│  WhatsApp, calendars, webhooks, connectors   │
├─────────────────────────────────────────────┤
│          Observability Layer                 │
│     Traces, metrics, logs, alerts            │
└─────────────────────────────────────────────┘
```

## Architectural Principles
1. **Tenant isolation** — Every query filters by tenant_id. No exceptions.
2. **Event-driven** — State changes emit events. Side effects are async.
3. **AI governance** — Every AI call logged, costed, and auditable.
4. **Consent-first** — No outreach without consent. Suppression enforced pre-send.
5. **Arabic-first** — RTL layout, Arabic labels, bilingual data fields.
6. **API-first** — Every feature accessible via API before UI.
7. **Operator-grade** — Built for people who manage revenue engines professionally.
