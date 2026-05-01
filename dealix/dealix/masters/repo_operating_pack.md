# Repo Operating Pack

> How we operate this repository day-to-day: branches, reviews, gates, releases, rollback.

---

## 1. Branch model

- `main` — always releasable. No direct pushes. All changes via PR.
- `develop` — integration branch (optional, for parallel feature streams).
- `feat/<slug>` — feature branches, short-lived.
- `fix/<slug>` — bugfix branches.
- `chore/<slug>` — non-functional changes (docs, deps).
- `release/<version>` — release preparation branches.
- `hotfix/<slug>` — emergency fixes to production from `main`.

---

## 2. Required GitHub rulesets

Configured in repo settings → Rules → Rulesets. Apply to `main` and `release/*`:

- Require pull request before merging
- Require approvals: **1 minimum** (2 for `release/*`)
- Dismiss stale approvals when new commits are pushed
- Require review from Code Owners
- Require status checks: `security`, `lint`, `test (3.11)`, `test (3.12)`, `docker`
- Require branches to be up-to-date before merging
- Require conversation resolution before merging
- Require linear history
- Restrict who can push to matching branches
- Block force pushes
- Require deployments to `staging` before merging (optional — enable when staging exists)

---

## 3. PR lifecycle

1. Open PR from feature branch.
2. Auto-assigned reviewers via CODEOWNERS.
3. CI runs: `security` → `lint` → `test` → `docker`.
4. All conversations resolved.
5. At least one approving review (two for release branches).
6. Squash-merge to `main` with a conventional-commit title.

---

## 4. Commit message convention

Loose Conventional Commits:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`.

Scopes (examples): `phase8`, `phase9`, `trust`, `contracts`, `api`, `core`, `deps`.

Breaking changes: add `!` after type, e.g. `feat(contracts)!: …`, and include `BREAKING CHANGE:` in the footer.

---

## 5. CODEOWNERS

Security-critical paths have dedicated owners. See `.github/CODEOWNERS`.

Mandatory: any edit to `dealix/` (the governance layer) requires review from Architecture. Any edit to `.github/`, `Dockerfile`, `core/config/`, `SECURITY.md` requires a security-aware reviewer.

---

## 6. Environments

Four deployment targets, each with its own secrets:
- `dev` — ephemeral, no production data
- `staging` — mirrors production, scrubbed data
- `canary` — 5-10% of production traffic
- `prod` — full traffic

Required reviewers: `canary` and `prod` require manual approval in GitHub Environments (requires GitHub Enterprise Cloud for private repos; otherwise enforce via deploy script + runbook).

---

## 7. Secrets

- **NEVER** store production secrets in GitHub Actions Secrets if avoidable. Use OIDC to cloud KMS / Vault.
- Secrets rotated **quarterly** at minimum.
- Any suspected leak: rotate immediately and file a SECURITY.md report.

---

## 8. Releases

1. Merge to `main`.
2. Update `CHANGELOG.md` under a new `## [x.y.z] — YYYY-MM-DD` heading.
3. Create branch `release/vx.y.z` from `main`.
4. Bump version in `pyproject.toml` and `.env.example` (APP_VERSION).
5. Open PR; require 2 approvals.
6. After merge, tag: `git tag -a vx.y.z -m "vx.y.z" && git push origin vx.y.z`.
7. `release.yml` workflow: creates GitHub Release + pushes Docker image to GHCR.
8. Promote through envs: `dev` → `staging` → `canary` (observe 24h) → `prod`.

---

## 9. Rollback

Any environment can be rolled back to the previous released tag via:

```bash
# Image rollback
docker compose pull ghcr.io/ORG/ai-company-saudi:v<prev>
docker compose up -d

# DB rollback (if migrations regressed)
alembic downgrade -1
```

Rollback window: within 24h of deployment, roll back without blame. After 24h, write a fix-forward unless outage severity demands otherwise.

---

## 10. Security scans

Every PR runs:
- Gitleaks (scan against default branch diff)
- detect-secrets (baseline check)
- Trufflehog (verified secrets only)
- Bandit (Python security linter)
- Hadolint (Dockerfile)

Failure of any scan blocks merge. Escape hatches: must document in PR why the finding is a false positive AND add an allowlist entry to the corresponding tool's config.

---

## 11. Dependency hygiene

- Dependabot weekly for pip, GitHub Actions, Docker.
- Review within 7 days.
- Major version bumps require manual testing + changelog entry.

---

## 12. Documentation expectations

Every PR that adds or changes behavior MUST:
- Update `docs/agents.md` if it adds or changes an agent
- Update `docs/api.md` if it adds or changes an endpoint
- Update `CHANGELOG.md` under `[Unreleased]`
- Update `dealix/registers/no_overclaim.yaml` if it adds a public claim

---

## 13. Quick cheat sheet

```bash
# Start a feature
git switch -c feat/my-feature

# Commit convention
git commit -m "feat(phase8): add priority scoring to intake"

# Open PR
gh pr create

# Release
git switch -c release/v2.1.0
# bump version, update changelog
git commit -am "chore(release): v2.1.0"
gh pr create --base main
# after merge:
git tag -a v2.1.0 -m "v2.1.0"
git push origin v2.1.0
```
