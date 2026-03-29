# Decision Log

All architectural and product decisions are recorded here with rationale.

## D-001: Multi-Tenant via tenant_id Column
**Date**: 2026-03-01
**Decision**: Use shared-database, tenant_id-per-row isolation (not schema-per-tenant or database-per-tenant).
**Rationale**: Simpler operations, easier migration, sufficient for current scale. PostgreSQL Row-Level Security can be added later.
**Consequences**: Every query must filter by tenant_id. Indexes on tenant_id required everywhere.

## D-002: JWT Dict-Based Auth (not ORM User object)
**Date**: 2026-03-01
**Decision**: `get_current_user` returns a `dict` with `user_id`, `tenant_id`, `role` — not an ORM User object.
**Rationale**: Avoids lazy-loading issues with async sessions. Faster. Simpler dependency injection.
**Consequences**: Access via `current_user["tenant_id"]`, not `current_user.tenant_id`.

## D-003: Arabic-First RTL Design
**Date**: 2026-03-01
**Decision**: All UI is Arabic-first with `<html lang="ar" dir="rtl">`. English support secondary.
**Rationale**: Saudi market is primary. Arabic UX must be native, not an afterthought.
**Consequences**: All labels, error messages, and notifications default to Arabic. Bilingual fields on models (name + name_ar).

## D-004: Async SQLAlchemy with Auto-Commit Sessions
**Date**: 2026-03-01
**Decision**: `get_db()` dependency auto-commits on success, auto-rollbacks on exception.
**Rationale**: Eliminates manual commit/rollback in every endpoint. Consistent transaction boundaries.
**Consequences**: No explicit `await db.commit()` in routes. Use `await db.flush()` to get IDs before commit.

## D-005: AI Governance via AITrace Model
**Date**: 2026-03-15
**Decision**: Every AI call is logged to `ai_traces` table with provider, model, tokens, cost, latency, status.
**Rationale**: Cost control, quality monitoring, compliance audit trail, regression detection.
**Consequences**: AI wrapper (`ai_brain.think()`) must always create a trace record.

## D-006: PDPL Compliance — Suppression Before Outreach
**Date**: 2026-03-15
**Decision**: All outreach channels check suppression list before sending. Consent required before first contact.
**Rationale**: Saudi PDPL requires consent for marketing communications. Legal compliance is non-negotiable.
**Consequences**: `SuppressionEntry` model, `check_suppression()` called in sequence_worker and messaging services.

## D-007: Human-in-the-Loop for Social Engagement
**Date**: 2026-03-20
**Decision**: AI drafts social comments but humans must approve before publishing.
**Rationale**: Public-facing content carries brand risk. No autonomous public posting.
**Consequences**: `CommentDraft` model with `status=pending` → human review → `approved`/`rejected`.

## D-008: Industry Playbooks as First-Class Entity
**Date**: 2026-03-29
**Decision**: Playbooks are tenant-scoped models (not just config files) with revenue model, KPI targets, and outreach sequences.
**Rationale**: Enables productized offers (Revenue Engine Setup, Managed Pipeline Growth) with sector-specific templates.
**Consequences**: `Playbook` model with `industry`, `product_type`, `setup_fee`, `monthly_fee`, `kpi_targets`.

## D-009: SLA Tracking with Breach Detection
**Date**: 2026-03-29
**Decision**: SLA policies define time limits per entity type/stage. Breaches are tracked and escalated.
**Rationale**: Pipeline hygiene requires measurable accountability. Managed service clients expect SLA reporting.
**Consequences**: `SLAPolicy` and `SLABreach` models. Worker checks for breaches periodically.

## D-010: Pipeline Velocity as Core Metric
**Date**: 2026-03-29
**Decision**: Pipeline velocity (SAR/day) = (deals x avg_size x win_rate) / avg_cycle_days. Calculated in real-time.
**Rationale**: This is the north star metric. Every optimization should improve velocity.
**Consequences**: `/analytics/velocity` endpoint with 30/60/90 day forecasting.
