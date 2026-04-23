# Release Gates — Dealix Tier-1

> **Parent**: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)  
> **Plane**: Operating | **Tracks**: Operations, Trust  
> **Version**: 1.0 | **Status**: Canonical

---

## Mandatory Gates

A release candidate (RC) cannot proceed to merge or deploy unless ALL three gates pass:

### Gate 1: Architecture Brief
**Script**: `python scripts/architecture_brief.py`  
**Required**: 40/40 PASS  
**Validates**: All required governance docs, models, services, APIs, and frontend components exist.  
**Exit**: 0 = pass, 1 = fail

### Gate 2: Release Readiness Matrix
**Script**: `python scripts/release_readiness_matrix.py`  
**Required**: 26/26 PASS (or all checks)  
**Validates**: 
- Trust enforcement active (correlation_id)
- Weekly pack endpoint exists
- Auto evidence on deal close
- Saudi workflow live
- Golden path live
- All structured output schemas wired
- Sales pack + customer docs exist

**Exit**: 0 = pass, 1 = fail

### Gate 3: Pytest
**Command**: `python -m pytest tests -q --tb=line`  
**Required**: All tests pass  
**Note**: Currently has dependency drift issue (pre-existing); acceptable for now.

---

## CI Integration

The `.github/workflows/dealix-ci.yml` workflow runs Gate 1 and Gate 3 automatically on every PR. Gate 2 is manually invoked or run as part of release prep.

### Required Repository Settings

For full enforcement (manual GitHub configuration):

1. **Branch protection on `main`**:
   - Require PR reviews (1+ approver)
   - Require status checks: `backend`, `frontend`
   - Require branches up to date before merge

2. **CODEOWNERS enforced** (already in place):
   - `salesflow-saas/MASTER_OPERATING_PROMPT.md` requires owner approval
   - `salesflow-saas/docs/governance/` requires owner approval

3. **Secret scanning enabled** (GitHub setting)

---

## Manual Pre-Release Checklist

Before tagging a release:

```bash
cd salesflow-saas

# Gate 1
python scripts/architecture_brief.py
# Expect: OVERALL SCORE: 100.0% (40/40)

# Gate 2  
python scripts/release_readiness_matrix.py
# Expect: SCORE: 100.0% (X/X) — RELEASE READY: YES

# Gate 3
cd backend && python -m pytest tests -q --tb=line
# Expect: all tests pass
```

If any gate fails:
- Architecture brief fail → file/structure issue, fix before merge
- Release readiness fail → missing component, complete before merge  
- Pytest fail → investigate, fix or document as known issue

---

## Release Candidate (RC) Discipline

| Step | Action |
|------|--------|
| 1 | Create RC branch from main |
| 2 | Run all 3 gates locally |
| 3 | Open PR with `[RC]` prefix |
| 4 | CI runs Gates 1 and 3 automatically |
| 5 | Reviewer runs Gate 2 manually |
| 6 | All gates pass + 1 approval = mergeable |
| 7 | Tag release after merge |

---

## Future Hardening (Roadmap)

| Item | Status | Notes |
|------|--------|-------|
| Block merge on Gate failure | Manual | GitHub branch protection setting |
| OIDC for cloud deploy | Target | Replace long-lived secrets |
| Artifact attestations | Target | Requires Enterprise for private repos |
| Audit log streaming | Target | External retention |
| Canary deployment | Target | Infra-level rollout |
