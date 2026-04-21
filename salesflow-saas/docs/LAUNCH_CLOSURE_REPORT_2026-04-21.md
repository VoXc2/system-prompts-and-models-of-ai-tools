# Launch Closure Report — 2026-04-21

## 1) Reality Snapshot

- **Actual project scope:** this repository contains multiple unrelated folders, but the launchable product is `salesflow-saas` (FastAPI backend + Next.js frontend + runbooks/docs).  
- **Launch target:** the implemented runtime target is the Dealix app in `salesflow-saas/backend` and `salesflow-saas/frontend`, not the top-level mono-archive folders.  
- **Scope mismatch found:** documentation/process language mentions PR dependency ordering (`#16` before `#17`) but this local git checkout has **no remote configured**, so open PR state cannot be verified from repository metadata alone.  
- **Critical blockers found during validation:**  
  1. Frontend production build failed in offline/locked environments because `next/font/google` was fetching `Noto Kufi Arabic` at build time.  
  2. CI workflow was not aligned with the real stack (installed Flask deps, launched `backend/main.py`, ran non-existent tests).  
  3. README referenced a non-existent workflow file (`dealix-ci.yml`).  

## 2) Action Log

1. Replaced runtime Google font fetch with local/system stack usage in `frontend/src/app/layout.tsx` to remove network-dependent build failures.  
2. Rebuilt CI workflow (`.github/workflows/ci.yml`) to match the actual stack:
   - Python 3.12 setup
   - install backend requirements + dev requirements
   - run backend `pytest -q` with `PYTHONPATH=.`
   - run frontend `npm ci`, `npm run lint`, `npm run build`
3. Fixed README CI path so docs match implementation.
4. Executed local verification commands (see section 4).

## 3) Blocker Register

| Severity | Blocker | Evidence | Ownership | Status |
|---|---|---|---|---|
| BLOCKER | PR dependency `#16 -> #17` cannot be verified in this checkout | no git remote / no PR metadata in repository | Release manager / maintainer with GitHub access | OPEN (external) |
| HIGH | Backend tests cannot run in this environment due missing pip package fetch (`aiosqlite`) behind proxy | `pip install -r backend/requirements-dev.txt` fails with proxy 403 tunnel error | CI/infrastructure network config | OPEN (environmental) |
| MEDIUM | `npm` warns on unknown `http-proxy` env config | warning shown during frontend lint/build | developer environment hygiene | OPEN (non-blocking) |

## 4) Validation Results

- `frontend`: lint passes.
- `frontend`: build now passes after removing `next/font/google` runtime fetch.
- `backend`: local pytest not fully executable in this container because dependency installation is blocked by outbound proxy constraints.

## 5) Merge / Release Recommendation

- **Repo-fixable launch gaps in this checkout were closed** (CI alignment, build reliability, doc accuracy).  
- **Do not mark fully release-ready until external blockers are closed:**
  1. confirm PR dependency order (`#16` merged before `#17`) in GitHub,
  2. run backend full test suite in a network-enabled CI runner,
  3. attach resulting CI evidence to the launch PR.

