# Post-merge verification — Dealix

Run this checklist **after** PR #125 is merged into `main` (or when validating the release branch). Record fresh numbers below.

## Preconditions

1. Revoke any exposed GitHub PAT (see [`SECURITY_INCIDENT_PAT_EXPOSURE.md`](SECURITY_INCIDENT_PAT_EXPOSURE.md)).
2. Merge completed **only** from GitHub UI (no `--force` on shared branches).
3. Local checkout updated: `git checkout main && git pull`.

## Commands (reference)

نفّذ من مجلد `dealix` (جذر حزمة التطبيق) بعد `cd dealix`:

```bash
python -m compileall api auto_client_acquisition integrations db core
pytest -q --no-cov
python scripts/print_routes.py
python scripts/smoke_inprocess.py
```

**بوابة الإطلاق:** بعد الدمج، شغّل أيضاً `scripts/smoke_staging.py` على staging مع `STAGING_BASE_URL` — انظر [`LAUNCH_DAY_RUNBOOK_AR.md`](LAUNCH_DAY_RUNBOOK_AR.md).

Optional secret-pattern scan (adapt to your environment):

```bash
rg "ghp_|github_pat_|sk_live_" --glob '!htmlcov/**' --glob '!.venv/**'
```

## Last recorded run (workspace snapshot)

| Step | Result |
|------|--------|
| Git HEAD | `2d776cb` on branch `dealix-v3-autonomous-revenue-os` (re-run on `main` after merge) |
| compileall | OK (`api`, `auto_client_acquisition`, `integrations`, `dealix`) |
| pytest | `516 passed`, `6 skipped`, `0 failed` (`APP_ENV=test`, dummy LLM keys) — re-run after your merge |
| `print_routes.py` | `ROUTE_CHECK_OK no duplicate method+path` |
| `smoke_inprocess.py` | `SMOKE_INPROCESS_OK` |

## CI

Confirm GitHub Actions workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) is green on the merged commit.

## Manual follow-ups (not automated)

- Merge PR #125 on GitHub when checks pass.
- Deploy staging and run [`scripts/smoke_staging.py`](../scripts/smoke_staging.py) with `STAGING_BASE_URL` set.
