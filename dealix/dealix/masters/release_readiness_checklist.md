# Release Readiness Checklist

> Run this list before tagging any `v*.*.*` release. Any item missing blocks the release.

Release candidate: `v_____________`
Owner: `_____________`
Date: `_____________`

---

## 🔒 Security

- [ ] `gitleaks` full-history scan clean
- [ ] `detect-secrets` baseline clean
- [ ] `trufflehog` verified-secrets scan clean
- [ ] No new `.env*` files other than `.env.example` committed
- [ ] All new dependencies triaged (no CVE in Dependabot >High severity)
- [ ] Any new secret-handling code uses `SecretStr` + `.require_secret(...)` pattern
- [ ] Webhook signature verification in place for any new webhook

## 🧪 Quality gates

- [ ] `make lint` passes
- [ ] `make test` passes on Python 3.11 AND 3.12
- [ ] Coverage has not regressed (within ±2%)
- [ ] `mypy` findings reviewed (non-blocking but tracked)
- [ ] `bandit` findings reviewed (or allowlisted with rationale)

## 📝 Contracts & classifications

- [ ] Every new critical agent emits a `DecisionOutput`
- [ ] Every new action type is registered in `dealix/classifications/ACTION_CLASSIFICATIONS`
- [ ] Any action that is never-auto-executable is added to `NEVER_AUTO_EXECUTE`
- [ ] Every new event type has a defined envelope type + documented data schema
- [ ] JSON Schemas regenerated via `python -m dealix.contracts.dump_schemas`

## 📊 Observability

- [ ] Every new HTTP endpoint emits a span
- [ ] Every new agent emits a span with `agent.name`
- [ ] Every new LLM call uses the router (not bypassed)
- [ ] Every new tool call records to `ToolVerificationLedger`
- [ ] Every new workflow emits `workflow.*` spans and events

## 📚 Documentation

- [ ] `CHANGELOG.md` has a new `## [x.y.z] — YYYY-MM-DD` entry
- [ ] `README.md` / `README.ar.md` reflect any new user-facing claims
- [ ] `docs/agents.md` updated for any new/changed agent
- [ ] `docs/api.md` updated for any new/changed endpoint
- [ ] `dealix/registers/no_overclaim.yaml` has an entry for every new public claim
- [ ] `dealix/registers/technology_radar.yaml` updated if new tech adopted
- [ ] `dealix/registers/compliance_saudi.yaml` updated if compliance posture changed

## 🏛️ Governance

- [ ] `dealix/masters/constitution.md` still holds (no violations)
- [ ] Any new sensitive action has been run past `PolicyEvaluator` in tests
- [ ] Any new S3 data flow has a PDPL lawful basis recorded
- [ ] Any new third-party integration has a DPA in place OR is flagged not-prod
- [ ] CODEOWNERS updated for any new security-critical path

## 🐳 Build & deploy

- [ ] `docker build .` succeeds locally
- [ ] Container runs as non-root user
- [ ] `/health` responds within 5 seconds
- [ ] Healthcheck in Dockerfile still valid
- [ ] `docker-compose.yml` up still works end-to-end

## 🧾 Release mechanics

- [ ] Version bumped in `pyproject.toml`
- [ ] Version bumped in `.env.example` (`APP_VERSION=`)
- [ ] `make requirements` run if dependencies changed
- [ ] `release/vx.y.z` branch created
- [ ] PR opened with 2 approvals
- [ ] Merged squash-commit to `main`
- [ ] Tag `git tag -a vx.y.z -m "vx.y.z"` pushed
- [ ] `release.yml` workflow completed successfully
- [ ] Docker image pushed to GHCR at `:vx.y.z` and `:latest`
- [ ] GitHub Release auto-created with CHANGELOG excerpt

## 🚀 Post-release verification

Within 1 hour of deploy:
- [ ] `/health` green in all envs
- [ ] Error rate unchanged (within noise)
- [ ] Latency p95 unchanged (within noise)
- [ ] No spike in `trust_policy_decisions_total{decision="deny"}`
- [ ] No spike in `trust_tool_contradictions_total`
- [ ] LLM fallback rate unchanged
- [ ] No new Dependabot alerts introduced

Within 24 hours:
- [ ] No incident raised
- [ ] Customer-facing metrics stable
- [ ] No manual override of approval decisions

## 🔙 Rollback plan (if needed)

Previous stable tag: `v_____________`

Rollback command:
```bash
docker compose pull ghcr.io/ORG/ai-company-saudi:v<PREV>
docker compose up -d
```

DB: no migration in this release ☐ | migration included — downgrade with `alembic downgrade -1` ☐

---

**Sign-off**:

| Role | Name | Date |
|---|---|---|
| Release owner | | |
| Architecture reviewer | | |
| Security reviewer | | |
| QA | | |
