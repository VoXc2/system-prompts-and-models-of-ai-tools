# Dealix workflows under `dealix/.github/workflows/`

GitHub Actions **only** loads workflow definitions from the **repository root**:

`.github/workflows/*.yml`

The copies in this folder are **mirrors / references**. The canonical Dealix workflows that run on GitHub are:

| Workflow | Root path |
|----------|-----------|
| API CI (pytest, smoke, evals) | [`.github/workflows/dealix-api-ci.yml`](../../../.github/workflows/dealix-api-ci.yml) |
| Staging smoke (manual) | [`.github/workflows/dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml) |
| Daily revenue machine | [`.github/workflows/dealix-daily-revenue-machine.yml`](../../../.github/workflows/dealix-daily-revenue-machine.yml) |

Branch track **AI Company** → use Git branch `ai-company` (see [`docs/ops/GITHUB_AI_COMPANY_TRACK.md`](../../docs/ops/GITHUB_AI_COMPANY_TRACK.md)).
