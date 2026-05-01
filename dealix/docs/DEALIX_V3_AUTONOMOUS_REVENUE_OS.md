# Dealix v3 — Autonomous Saudi Revenue OS

This document defines the next execution layer for Dealix: an autonomous Saudi B2B revenue platform built around Revenue Memory, AI Agent Runtime, Saudi Market Radar, Compliance OS, Revenue Science, Vertical OS, and Executive Command Center.

## Strategic position

Dealix should not compete as a CRM, WhatsApp sender, or generic lead machine. Dealix should operate as the Saudi B2B Revenue OS that watches the market, detects buying signals, recommends the next best action, runs safe agent workflows, proves ROI, and learns from every outcome.

## Core v3 layers

1. Revenue Memory: immutable event timeline for every lead, company, message, reply, meeting, deal, compliance block, customer health event, QBR, and agent action.
2. Agent Runtime: safe orchestration for Prospecting, Signal, Enrichment, Personalization, Compliance, Outreach, Reply, Meeting, Deal Coach, Customer Success, and Executive Analyst agents.
3. Saudi Market Radar: sector, city, website, hiring, tender, event, social, and competitor signals.
4. Compliance OS: PDPL-first contactability, consent ledger, opt-out ledger, RoPA exports, campaign risk scoring, data retention, DSR workflow.
5. Revenue Science: forecast, attribution, causal lift, conversion model, churn model, expansion model, capacity planner, pricing model.
6. Copilot Action Engine: explains numbers, proposes actions, creates campaigns, drafts messages, blocks unsafe actions, and writes executive briefs.
7. Vertical OS: Clinics, Real Estate, Logistics, Hospitality, Training, Agencies, Construction, and Restaurants as productized sector packs.
8. Ecosystem: integrations, webhooks, templates, developer portal, partner marketplace, and public API.

## First implementation commits

- feat(v3): add event-sourced revenue memory
- feat(v3): add safe AI agent runtime
- feat(v3): add Saudi market radar
- feat(v3): add PDPL compliance operating layer
- feat(v3): add revenue science forecasting and attribution
- feat(v3): add command center copilot
- feat(v3): add vertical operating systems
- feat(v3): add autopilot and market radar landing pages

## Required production libraries

Backend: FastAPI, Pydantic v2, SQLAlchemy async, Alembic, Redis, Tenacity, HTTPX, structlog, OpenTelemetry, Sentry, Langfuse, OpenAI SDK, Anthropic SDK, Google Generative AI SDK.

AI quality: promptfoo or DeepEval for regression evaluations, Ragas for RAG quality when knowledge retrieval is added, pytest snapshots for deterministic agent contracts.

Frontend: Next.js, React, Tailwind, shadcn/ui, Recharts, TanStack Query, TanStack Table, Zod, React Hook Form, Framer Motion.

Data and jobs: Postgres, Redis Streams or Celery/RQ, pgvector for embeddings, object storage for exports, optional Kafka later.

Observability: Sentry, OpenTelemetry, Langfuse, structured audit logs, uptime checks.

## Golden rule

Every AI action must have context, policy, approval status, trace ID, cost estimate, and measurable business outcome.
