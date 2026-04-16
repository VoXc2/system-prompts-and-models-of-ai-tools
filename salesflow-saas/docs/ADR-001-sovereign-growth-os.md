# ADR-001: Sovereign Growth OS Architecture

**Status:** Accepted
**Date:** 2026-04-16
**Decision Makers:** Founder

## Context

Dealix started as an AI-powered CRM for the Saudi market. As the platform matures, the need arose to evolve from "sales automation" to a full **Company Growth Operating System** that manages:
- Revenue operations
- Strategic partnerships
- M&A (mergers & acquisitions)
- Market expansion
- Governance and compliance
- Executive decision support

## Decision

We will extend Dealix with a **Layer 8 (Strategic Operations)** consisting of:
1. **10 autonomous agents** organized into 3 families (Growth Intelligence, Corporate Development, Governance & Execution)
2. **A typed event system** (`StrategicEventBus`) with domain-specific Pydantic events
3. **A governance engine** implementing policy-as-code with an approval matrix
4. **A sovereign growth dashboard** providing board-level intelligence

### Architecture Principles

| Principle | Implementation |
|---|---|
| Autonomy in execution, control in capital and risk | Agents auto-execute within boundaries; HITL for sensitive decisions |
| No silent decisions | Every action produces an auditable event |
| Policy-as-code | Governance checks run programmatically, not manually |
| Immutable events | Events are frozen Pydantic models; history is append-only |
| State machines over ad-hoc status fields | Partnership, M&A, and Expansion have defined state machines |

### Key Design Choices

1. **BaseAgent inheritance** (not LangGraph nodes) — consistent with existing 27 agents in Layers 1–7. Strategic agents use the same `think()`, `send_message()`, and `handle_message()` patterns.

2. **In-process event bus first** — `StrategicEventBus` runs in-memory for Phase 1. Migration to Redis/Kafka is planned for Phase 3 (group-scale).

3. **Governance as a service, not middleware** — agents call `governance_engine.evaluate()` explicitly before sensitive actions. This is intentional: agents must know they're being governed (no magic interception).

4. **Decision Memo as the universal output** — every agent can produce a `DecisionMemo` with standardized fields (financial impact, risk register, confidence score, next actions).

## Consequences

### Positive
- Clear separation between tactical (Layers 1–7) and strategic (Layer 8) operations
- Governance is enforceable from Day 1
- Board can see a single dashboard aggregating all strategic activity
- Event history enables causal learning (forecast vs actual)

### Negative / Risks
- In-memory event bus means state is lost on restart (mitigated by periodic DB flush in Phase 2)
- Agent quality depends on LLM output quality (mitigated by confidence scoring + HITL gates)
- 10 new agents add complexity to testing and monitoring

### Migration Path
- Phase 1: In-process bus + SQLite → Phase 2: Redis event stream → Phase 3: Kafka + data warehouse
- Phase 1: Manual approval via API → Phase 2: Slack/WhatsApp approval workflow → Phase 3: Decision room UI

## References

- `backend/app/agents/strategic/events.py` — Event taxonomy + bus
- `backend/app/agents/strategic/__init__.py` — Agent registry
- `backend/app/services/governance_engine.py` — Policy-as-code engine
- `backend/app/api/v1/strategic_dashboard.py` — Dashboard API
- `docs/EXECUTION-MATRIX.md` — Full agent-to-KPI mapping
