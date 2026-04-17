# DEALIX — Tier-1 Company Execution Blueprint

> **This is the authoritative execution blueprint for Dealix.**
> **Version**: 1.0.0
> **Last updated**: 2026-04-17
> **Execution status**: See `docs/execution_log.md`

---

## How to Use This Blueprint

1. Read `docs/internal/STATE_AUDIT.md` first — honest current state
2. Check `docs/execution_log.md` — what's done, what's next
3. Consult `docs/registry/TRUTH.yaml` — canonical capability status
4. Check `commercial/claims_registry.yaml` — what you can/can't claim publicly
5. Run gates:
   - `python scripts/architecture_brief.py` — 40/40 governance check
   - `python scripts/release_readiness_matrix.py` — 41/41 runtime check
   - `python scripts/release_readiness_gate.py` — blueprint-spec gate
   - `python scripts/validate_truth_registry.py` — truth/claims alignment

---

## Executive Summary

Dealix is the Arabic-first, PDPL-native, decision-grade Revenue OS for enterprises in Saudi Arabia and the GCC. This blueprint defines Tier-1 quantitatively and provides execution tasks to reach it.

**Current state** (from State Audit):
- Pre-revenue, pre-production
- Strong architecture (~103 files, 11,731 lines, 28 commits)
- Golden path, trust enforcement, structured outputs, Saudi workflow: LIVE
- RLS, idempotency, durable execution, OTel: CODE READY, not yet in production
- Repository separation and dependency drift: BLOCKERS

**Tier-1 definition** — 11 quantitative thresholds:
- Availability ≥ 99.95%
- p95 API latency < 300ms
- p95 Golden path latency < 5s
- Deployment frequency ≥ 5/week
- Lead time for changes < 1 business day
- Change failure rate < 15%
- MTTR < 30 minutes
- SOC 2 Type II + PDPL-compliant
- KSA data residency available
- NPS ≥ 40 after 3 months
- NRR ≥ 110% after 18 months

---

## Immutable Guardrails

1. Never merge PR that fails Release Readiness Gate
2. Never expose UI capability without runtime evidence
3. Never mark task "done" without passing Acceptance + Verification
4. Never introduce dependencies without pinning + SBOM
5. Never commit secrets — use AWS Secrets Manager / Vault / Doppler
6. Never deploy on Friday after 14:00 KSA time

---

## TASK INDEX (P0 first)

### P0 — Blockers
- **TASK-001**: Extract Dealix into own repo → `scripts/extract_dealix_repo.sh` ready
- **TASK-002**: Monorepo restructure (depends on 001)
- **TASK-003**: Fix Python dependency drift → `pyproject.toml` ready for uv
- **TASK-004**: Fix Node dependency drift → `package.json` pinned, needs pnpm-lock
- **TASK-005**: Secrets audit + rotation → `rotation_log.md` + `.pre-commit-config.yaml` ready
- **TASK-006**: Legal foundation → tracker at `docs/internal/legal_status.md`

### P1 — Foundation
- **TASK-010**: Canonical truth registry → `TRUTH.yaml` + `claims_registry.yaml` DONE
- **TASK-020**: RLS enforcement → migration `20260417_0002_add_rls.py` DONE
- **TASK-022**: Idempotency coverage → middleware + service DONE
- **TASK-030**: Golden path E2E → `services/golden_path.py` DONE
- **TASK-050**: LLM router with cost guards → `services/model_router.py` exists
- **TASK-080**: OTel instrumentation → `observability/otel.py` + gateway span DONE
- **TASK-100**: CI workflow → `dealix-ci.yml` exists with architecture + release matrix
- **TASK-101**: Release Readiness Gate → `release_readiness_gate.py` DONE

### P2 — Productization
- **TASK-102**: Feature flags (future)
- **TASK-110**: Approval Center surface → DONE (backend + frontend)
- **TASK-120**: Sales enablement assets → one-pager + marketer hub DONE

### P0 Special
- **TASK-999**: State Audit → `docs/internal/STATE_AUDIT.md` DONE

---

## Blueprint-Execution Progress

| Task | Status | Evidence |
|------|--------|----------|
| TASK-999 | DONE | `docs/internal/STATE_AUDIT.md` |
| TASK-001 (prep) | READY | `scripts/extract_dealix_repo.sh` — founder decision pending |
| TASK-003 (pyproject) | DONE | `backend/pyproject.toml` |
| TASK-004 (pin) | PARTIAL | `frontend/package.json` pinned; `pnpm-lock.yaml` needs generation |
| TASK-005 (pre-commit) | DONE | `.pre-commit-config.yaml` + `rotation_log.md` |
| TASK-006 | DONE | `docs/internal/legal_status.md` |
| TASK-010 | DONE | TRUTH.yaml + claims_registry.yaml + validator + CI |
| TASK-020 (RLS) | DONE | migration + middleware + helpers |
| TASK-022 (idempotency) | DONE | middleware + service + model |
| TASK-030 (golden path) | DONE | golden_path service + API |
| TASK-080 (OTel) | DONE | observability/otel.py + gateway span |
| TASK-100 (CI) | DONE | `.github/workflows/dealix-ci.yml` |
| TASK-101 (gate) | DONE | `scripts/release_readiness_gate.py` |
| TASK-110 (Approval Center) | DONE | `api/v1/approval_center.py` + frontend |
| TASK-120 (sales pack) | DONE | `revenue-activation/sales-pack/*` |

---

## Red Flags That HALT Execution

1. Credential found in git history still active
2. Test claimed to pass but actually skipped
3. TODO in security-critical code paths
4. LLM prompt with absolute claims ("always", "never", "100%")
5. UI capability not backed by feature flag or telemetry
6. Customer-facing claim not in `claims_registry.yaml`
7. Dependency with CVE ≥ 7.0
8. Infrastructure not tagged `project=dealix`

---

## Next Actions for Founder

1. **TASK-001**: Decide GitHub org name (`dealix-io`?) and run `scripts/extract_dealix_repo.sh`
2. **TASK-006**: Engage Saudi counsel for privacy/ToS review
3. **TASK-006**: Decide entity structure (MISA vs DIFC)
4. **TASK-006**: File trademark in KSA

Everything else in this blueprint can be executed by coding agents without founder intervention.
