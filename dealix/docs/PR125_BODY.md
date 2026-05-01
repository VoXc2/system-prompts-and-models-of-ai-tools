# PR #125 — نص مقترح لجسم الـ PR (للنسخ إلى GitHub)

## Summary

Autonomous Saudi **Revenue OS** foundation: v3 APIs (radar, compliance, revenue science, safe agents), **Arabic Personal Strategic Operator**, **business/GTM** deterministic APIs, project intelligence + Supabase migration, WhatsApp **payload** helpers (no send), docs, scripts, CI, and expanded tests.

## Major modules

- `api/routers/v3.py`, `api/routers/personal_operator.py`, `api/routers/business.py`
- `auto_client_acquisition/v3/*`, `auto_client_acquisition/personal_operator/*`, `auto_client_acquisition/business/*`, `auto_client_acquisition/ai/model_router.py`
- `supabase/migrations/202605010001_v3_project_memory.sql`
- `docs/*` (business, security, Supabase, WhatsApp, staging, PR review)
- `.github/workflows/ci.yml`

## Safety guarantees

- No cold WhatsApp; drafts and **approval_required** on outbound paths.
- No PAT or API keys committed; use env + secret managers.
- Gmail/Calendar integrations module: **draft-only** abstractions.

## Tests

- `pytest -q --no-cov` (see stabilization report for latest counts).
- e2e skipped unless server on `127.0.0.1:8001`.

## How to review

1. Read `docs/PR125_REVIEW_GUIDE.md` + `docs/PR125_FINAL_STABILIZATION_REPORT.md`
2. Run `python scripts/print_routes.py`
3. Run compileall + pytest locally

## How to run

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
python -m compileall api auto_client_acquisition
pytest -q --no-cov
uvicorn api.main:app --host 127.0.0.1 --port 8001
```

## Known limitations

- Staging/prod WhatsApp/Gmail OAuth not wired in this PR.
- Moyasar checkout requires provider keys in env for live calls.
- Local HEAD may differ from remote; `git pull` before final verify.

## Next steps after merge

- Revoke any exposed PATs; use `gh auth login` / fine-grained tokens.
- Apply Supabase migration on staging; run `scripts/verify_supabase_project_memory.sql`.
- Deploy staging (Railway/Render) and run `scripts/smoke_local_api.py`.
