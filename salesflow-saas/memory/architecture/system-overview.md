# Dealix System Architecture Overview

**Type**: architecture
**Date**: 2026-04-11
**Status**: active
**Confidence**: high

## Summary
Dealix is evolving from a multi-tenant AI CRM into a sovereign enterprise growth operating system built around decision, execution, trust, data, and operating planes.

## Components
```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                  │
├──────────────────────┬──────────────────────────────────┤
│   Next.js Frontend   │         FastAPI Backend           │
│   (Port 3000)        │         (Port 8000)               │
│   - Dashboard        │   ┌─────────────────────────┐    │
│   - Landing          │   │   API Layer (v1)         │    │
│   - Auth             │   │   - Auth, Leads, Deals   │    │
│   - Pipeline         │   │   - Inbox, Sequences     │    │
│                      │   │   - Compliance, Proposals │    │
│                      │   ├─────────────────────────┤    │
│                      │   │   Services Layer          │    │
│                      │   │   - AI Engine (Arabic)    │    │
│                      │   │   - PDPL Compliance       │    │
│                      │   │   - Sequence Engine       │    │
│                      │   │   - CPQ System            │    │
│                      │   │   - Agent Orchestrator    │    │
│                      │   ├─────────────────────────┤    │
│                      │   │   Integration Layer       │    │
│                      │   │   - WhatsApp, Email, SMS  │    │
│                      │   │   - Stripe, ZATCA         │    │
├──────────────────────┴───┴─────────────────────────┤    │
│        Celery Workers (4)    │    Celery Beat        │    │
├──────────────────────────────┴──────────────────────┤    │
│   PostgreSQL 16     │     Redis 7                    │    │
└─────────────────────┴───────────────────────────────┘
```

## Key Design Decisions
- **Multi-tenant isolation**: tenant_id on every table, enforced at query level
- **Arabic-first**: RTL layout, Arabic NLP, Saudi dialect support
- **WhatsApp-first**: Primary communication channel (85% Saudi penetration)
- **PDPL-native**: Consent checked before every outbound message
- **LLM fallback chain**: Groq → OpenAI for cost optimization
- **Async everything**: asyncpg, async SQLAlchemy, async HTTP clients

## Sovereign Operating Model
- **Decision Plane**: detection, triage, scenarios, memos, forecasting, evidence-backed recommendations
- **Execution Plane**: durable workflows, resumable approvals, retries, compensation, cross-system commitments
- **Trust Plane**: approval routing, policy evaluation, authorization, secrets governance, tool verification
- **Data Plane**: Postgres + pgvector source of truth, data contracts, quality checks, telemetry
- **Operating Plane**: GitHub release controls, provenance, protected deployments, external audit posture

## Business Tracks
- **Revenue OS**
- **Partnership OS**
- **M&A / CorpDev OS**
- **Expansion OS**
- **PMI / PMO OS**
- **Executive / Board OS**

## Required Product Surfaces
- Executive Room, Approval Center, Evidence Pack Viewer
- Partner Room, DD Room, M&A Pipeline Board
- Revenue Funnel Control Center, Actual vs Forecast Dashboard
- PMI 30/60/90 Engine, Policy Violations Board, Connector Health Board
- Saudi Compliance Matrix, Model Routing Dashboard, Release Gate Dashboard

## Related Topics
- [ADR-001: Multi-tenant architecture](../adr/001-multi-tenant.md)
- [ADR-002: WhatsApp as primary channel](../adr/002-whatsapp-first.md)
- [Provider routing strategy](../providers/routing-strategy.md)
- [Sovereign enterprise operating model](../../docs/SOVEREIGN_ENTERPRISE_GROWTH_OS_AR.md)
