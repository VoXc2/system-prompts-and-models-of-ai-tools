# §1 — Verification Protocol

> Convert self-reported completion into externally-validated reality.
> **NO Wave task starts until all 7 return green.**

| ID | Task | Owner | Automation | Status |
|----|------|-------|------------|--------|
| V001 | Full git history secret scan | CTO | `scripts/v001_secret_scan.sh` | scripted |
| V002 | Runtime RLS fuzz test (10K queries) | Backend | `backend/tests/security/test_rls_fuzz.py` | scripted |
| V003 | External pentest | Founder | [V003_pentest_engagement.md](V003_pentest_engagement.md) | pending engagement |
| V004 | No-founder customer demo test | Founder | [V004_no_founder_demo_test.md](V004_no_founder_demo_test.md) | pending sessions |
| V005 | Truth Registry independent audit | 2nd engineer | `scripts/v005_truth_registry_audit.py` | scripted |
| V006 | Performance baseline (k6) | Backend | `infra/load-tests/baseline.js` → `docs/baselines/perf_YYYYMMDD.json` | scripted |
| V007 | Accessibility baseline (axe) | Frontend | `frontend/tests/a11y/baseline.spec.ts` → `docs/baselines/a11y_YYYYMMDD.json` | scripted |

## Execution order (by week)

**Week 1**
- V001 (secret scan) — run locally, fix any verified leak, THEN commit
- V005 (registry audit) — independent engineer
- V002 (RLS fuzz) — add to nightly CI

**Week 2**
- V006 (perf baseline) — requires staging with prod-like data
- V007 (a11y baseline) — requires frontend routes stable
- V003 (pentest) — send RFP to 3 vendors, sign SOW

**Week 4–6**
- V004 (no-founder demo) — 3 testers

**Week 10**
- V003 (pentest) — report received, 0 Critical + ≤2 High

## Gate

- All 7 Green → Verification complete, proceed to §2 + §3.
- Any Red → HALT. Do not start Wave A. Do not claim production-ready.

## Reporting

Each V-task writes to:
- **Internal**: `docs/internal/` (private — secret_audit_log, pentest_report, rotation_log)
- **Baselines**: `docs/baselines/` (perf + a11y snapshots)
- **Public registry**: updates propagated to `TRUTH.yaml` + `claims_registry.yaml`
