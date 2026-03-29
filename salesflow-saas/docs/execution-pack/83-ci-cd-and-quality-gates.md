# CI/CD & Quality Gates

## Branch Strategy
- `main` — Production-ready, protected
- `develop` — Integration branch
- `feature/*` — Feature branches (from develop)
- `fix/*` — Bug fix branches
- `release/*` — Release preparation

## Protected Branch Rules (main)
- Require pull request review (1+ approvals)
- Require status checks to pass
- No direct pushes
- No force pushes

## CI Pipeline

### On Pull Request
```yaml
steps:
  - lint:
      - python: ruff check + ruff format --check
      - typescript: eslint + prettier --check
  - type-check:
      - python: mypy (gradual)
      - typescript: tsc --noEmit
  - test:
      - backend: pytest -v --cov
      - frontend: vitest (future)
  - security:
      - pip-audit (Python dependencies)
      - npm audit (Node dependencies)
  - build:
      - docker build (verify Dockerfiles)
```

### On Merge to main
```yaml
steps:
  - All PR checks
  - Build Docker images
  - Tag with version
  - Deploy to staging
  - Run smoke tests
  - Deploy to production (manual approval)
```

## Quality Gates

| Gate | Threshold | Blocking? |
|------|-----------|-----------|
| Python lint (ruff) | 0 errors | Yes |
| Python syntax (ast.parse) | 0 errors | Yes |
| Test suite passes | 100% | Yes |
| Test coverage | > 60% | Warning (future) |
| Security vulnerabilities | 0 critical/high | Yes |
| Docker build | Succeeds | Yes |
| TypeScript compile | 0 errors | Yes |

## Migration Discipline
1. Every schema change goes through Alembic
2. Migrations must have both `upgrade()` and `downgrade()`
3. Migrations tested in staging before production
4. Never manually edit the database schema
5. Migration files committed with the code that uses them

## Secrets Handling
- Secrets via environment variables
- `.env` in `.gitignore` (never committed)
- Docker secrets in production
- No secrets in CI logs (masked)

## Release Process
1. Create release branch from develop
2. Version bump in `pyproject.toml` / `package.json`
3. Generate changelog
4. PR to main
5. After merge: tag + deploy
6. Monitor for 30 minutes post-deploy
