# Autonomous Upgrade Director — Operating Model (Dealix)

**Role:** Ruthless, evidence-driven CTO + Staff Engineer + SRE. **Not** a novelty chaser.  
**Implementation:** `app/models/upgrade_director.py`, `app/services/upgrade_director/`, `app/api/v1/upgrade_director.py`, `app/workers/upgrade_director_tasks.py`.

---

## Hard rules (non-negotiable)

1. **No production integration** without Phases 3–9 completed offline and tests green.
2. **Official sources first:** release notes, docs, GitHub releases, PyPI/npm, migration guides.
3. **Stable subsystems** are not rewritten unless a replacement is clearly superior *and* validated in staging.
4. **Automated hourly job** in this repo performs **local filesystem snapshot only** (`requirements.txt` + `package.json` pins). It does **not** crawl the public internet (avoids hype feeds, supply-chain noise, and uncontrolled egress).

---

## Twelve phases (each human/CI “cycle”)

| Phase | Name | Owner | Automation in-repo |
|-------|------|--------|---------------------|
| 1 | Scan | Human / CI | Partial: `collect_local_dependency_snapshot()` |
| 2 | Filter | Human | — |
| 3 | Deep research | Human | — |
| 4 | Relevance scoring | Human | Optional spreadsheet using weights below |
| 5 | Risk review | Human | — |
| 6 | Integration planning | Human | Stored in candidate `implementation_plan` |
| 7 | Sandbox | Branch / feature flag | — |
| 8 | Test | CI | pytest, Playwright, load tests |
| 9 | Decision | Human | `recommended_action` |
| 10 | Merge / Reject / Defer | Human | Git + changelog |
| 11 | Memory update | API | `POST .../complete` + optional `system_memory_records` |
| 12 | Executive summary | Human | `executive_summary` + `machine_summary` JSON |

---

## Scoring weights (0–100 each, then weighted total)

Suggested weights for **weighted_total** (tune per quarter):

| Dimension | Weight % |
|-----------|----------|
| Strategic value | 12 |
| Immediate usefulness | 10 |
| Ease of integration | 10 |
| Production readiness | 12 |
| Security confidence | 12 |
| Maintenance confidence | 10 |
| Performance upside | 8 |
| Cost upside | 8 |
| Differentiation | 6 |
| Arabic / regional relevance | 6 |
| Multi-agent / memory relevance | 6 |

**Confidence** (0–100): certainty in scores given evidence quality.

**Recommended action:** `ignore` | `watchlist` | `sandbox` | `staging` | `promote`

---

## API (admin JWT)

Base path: `/api/v1/admin/upgrade-director`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/local-snapshot` | Current local pin snapshot |
| POST | `/cycles/start` | Draft cycle + snapshot |
| POST | `/cycles/{id}/complete` | Finalize with `machine_summary`, `candidates[]`, narratives |
| GET | `/cycles` | Recent cycles |
| GET | `/cycles/{id}` | Detail + candidates |

JSON contracts: `docs/schemas/upgrade-candidate.schema.json`, `docs/schemas/upgrade-cycle-end.schema.json`.

---

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `DEALIX_UPGRADE_DIRECTOR_HOURLY` | `false` | When `true`, Celery runs hourly local snapshot task |
| `DEALIX_PLATFORM_TENANT_ID` | empty | UUID string; if set, hourly + completed cycles mirror to `system_memory_records` |

---

## Celery

- Task: `app.workers.upgrade_director_tasks.upgrade_director_hourly_tick`
- Beat: every hour at **:15** (staggered vs other jobs)
- If `DEALIX_UPGRADE_DIRECTOR_HOURLY=false`, task **no-ops** immediately (safe default)

---

## Anti-hype checklist (reject if any)

- No changelog / no semver discipline.
- Single maintainer + months of silence.
- “Revolutionary” with no benchmark vs current stack.
- License incompatible with SaaS distribution.
- Requires broad data egress to unknown endpoints.
- Breaks reproducible builds or audit trail.

---

## Next evolution (optional, not default)

- Wire CI to POST `/cycles/{id}/complete` after nightly research job **you control** (e.g. RSS of official release feeds only).
- Prometheus gauge from `upgrade_director_cycles` counts by `recommended_action`.
- Dedupe table for rejected tools (`name`+`version`) to avoid re-litigation.

---

## Relation to Brain OS

Completed cycles can land in **`system_memory_records`** (when `DEALIX_PLATFORM_TENANT_ID` is set) so the intelligence layer can retrieve past decisions. This does **not** auto-upgrade dependencies.
