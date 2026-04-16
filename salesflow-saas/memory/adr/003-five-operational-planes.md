# ADR-003: Five Operational Planes — الطبقات التشغيلية الخمس

**Date**: 2026-04-16  
**Status**: proposed  
**Deciders**: CTO, Architect, AI Lead, Security Lead  

## Context

Dealix's MASTER-BLUEPRINT defines "Five Architecture Layers" (Experience, Orchestration, Intelligence, Data & Memory, Integration). These layers describe the *technical* stack but do not map to *operational* concerns that enterprises evaluate: policy decisions, execution durability, trust, data governance, and release engineering.

The Completion Program audit (2026-04-16) identified that documentation is stronger than implementation (Gap #1) and that no single operational framework ties the 250+ backend modules to enterprise readiness gates.

## Decision

We adopt **Five Operational Planes** as the canonical framework for measuring Dealix's enterprise readiness. Each plane has clear subsystems, ownership, and acceptance gates.

### The Five Planes

| # | Plane | Scope | Primary Technologies |
|---|-------|-------|---------------------|
| 1 | **Decision** | Agent outputs, structured decisions, evidence, provenance | OpenAI Structured Outputs, LangGraph, Pydantic schemas |
| 2 | **Execution** | Workflow durability, compensation, idempotency | Celery (short), OpenClaw (medium), Temporal (long) |
| 3 | **Trust** | Policy, authorization, secrets, identity, tool verification | OPA, OpenFGA, Vault, Keycloak, verification ledger |
| 4 | **Data** | Operational DB, semantic memory, connectors, quality, events | PostgreSQL, pgvector, connector facades, Great Expectations |
| 5 | **Operating** | CI/CD, environments, observability, release gates, audit | GitHub Actions, OTel, rulesets, OIDC, attestations |

### Relationship to Existing Architecture Layers

| Architecture Layer (MASTER-BLUEPRINT) | Operational Plane(s) |
|---------------------------------------|---------------------|
| Experience | Operating (release gates) + Data (semantic metrics for dashboards) |
| Orchestration | Decision + Execution |
| Intelligence | Decision (typed outputs) + Trust (tool verification) |
| Data & Memory | Data |
| Integration | Data (connector facades) + Trust (connector audit) |

### What This Replaces

- Ad-hoc references to "fabrics" in planning discussions
- Undefined "governance layer" concept
- Scattered policy points across services

### What This Does NOT Replace

- The Five Architecture Layers in MASTER-BLUEPRINT (those describe technical structure)
- The agent/crew/service code organization (that follows technical layers)

## Consequences

### Positive
- Every subsystem maps to exactly one operational plane
- Enterprise readiness is measurable per plane
- Workstreams align to planes for clear ownership
- Cross-cutting concerns (Saudi compliance, security) map to specific plane intersections

### Negative
- Requires updating module-map.md and system-overview.md
- Teams must learn new vocabulary alongside existing architecture layers
- Risk of confusion between "architecture layers" and "operational planes" — mitigated by clear naming

### Neutral
- Does not change code organization; planes are an operational overlay on the existing codebase

## Related

- [COMPLETION_PROGRAM.md](../../docs/completion-program/COMPLETION_PROGRAM.md) — Master program document
- [CURRENT_VS_TARGET_REGISTER.md](../../docs/completion-program/CURRENT_VS_TARGET_REGISTER.md) — Status per subsystem
- [ADR-001: Multi-tenant](001-multi-tenant.md) — Data isolation decision
- [ADR-002: WhatsApp-first](002-whatsapp-first.md) — Channel priority decision
