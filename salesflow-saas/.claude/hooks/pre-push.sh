#!/usr/bin/env bash
# Dealix Pre-Push Hook
# Runs full test suite, checks migrations, and verifies no .env files are staged.
set -euo pipefail

# ── Path Resolution ───────────────────────────────
_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
_LIB_DIR="$(cd "${_SCRIPT_DIR}/../../scripts/lib" 2>/dev/null && pwd || true)"
if [[ -n "${_LIB_DIR}" && -f "${_LIB_DIR}/resolve-paths.sh" ]]; then
  . "${_LIB_DIR}/resolve-paths.sh"
else
  # Inline fallback when lib is unreachable
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  if [[ -f "${REPO_ROOT}/salesflow-saas/CLAUDE.md" ]]; then
    PROJECT_ROOT="${REPO_ROOT}/salesflow-saas"
  else
    PROJECT_ROOT="${REPO_ROOT}"
  fi
  BACKEND_DIR="${PROJECT_ROOT}/backend"
  HAS_BACKEND=$([[ -d "$BACKEND_DIR" ]] && echo 1 || echo 0)
fi

echo "============================================"
echo "  Dealix Pre-Push Checks"
echo "============================================"

# ── 1. Full Test Suite ──────────────────────────
echo ""
echo "[1/3] Running full test suite..."

if [[ "${HAS_BACKEND}" -eq 1 ]] && [ -d "${BACKEND_DIR}/tests" ]; then
    cd "${BACKEND_DIR}"
    if ! pytest -x -q --tb=short 2>&1; then
        echo ""
        echo "FAIL: Test suite failed. Fix all tests before pushing."
        exit 1
    fi
    echo "PASS: Full test suite passed."
    cd "${REPO_ROOT}"
else
    echo "[SKIP] Backend not found in this layout. Skipping test suite."
fi

# ── 2. Uncommitted Migrations ──────────────────
echo ""
echo "[2/3] Checking for uncommitted migrations..."

if [[ "${HAS_BACKEND}" -eq 1 ]]; then
    UNTRACKED_MIGRATIONS=$(git ls-files --others --exclude-standard "${BACKEND_DIR}/alembic/versions/" 2>/dev/null | grep '\.py$' || true)
    MODIFIED_MIGRATIONS=$(git diff --name-only "${BACKEND_DIR}/alembic/versions/" 2>/dev/null | grep '\.py$' || true)

    if [ -n "${UNTRACKED_MIGRATIONS}" ]; then
        echo "FAIL: Found untracked migration files:"
        echo "${UNTRACKED_MIGRATIONS}"
        echo "  Commit these migrations before pushing."
        exit 1
    fi

    if [ -n "${MODIFIED_MIGRATIONS}" ]; then
        echo "WARN: Found modified but uncommitted migration files:"
        echo "${MODIFIED_MIGRATIONS}"
        echo "  Consider committing these changes."
    fi

    MODEL_CHANGES=$(git diff HEAD --name-only "${BACKEND_DIR}/app/models/" 2>/dev/null | grep '\.py$' || true)
    if [ -n "${MODEL_CHANGES}" ]; then
        MIGRATION_CHANGES=$(git diff HEAD --name-only "${BACKEND_DIR}/alembic/versions/" 2>/dev/null | grep '\.py$' || true)
        if [ -z "${MIGRATION_CHANGES}" ]; then
            echo "WARN: Model files changed but no new migrations detected:"
            echo "${MODEL_CHANGES}"
            echo "  Run: cd backend && alembic revision --autogenerate -m 'description'"
        fi
    fi

    echo "PASS: Migration check complete."
else
    echo "[SKIP] Backend not found in this layout. Skipping migration check."
fi

# ── 3. No .env Files ───────────────────────────
echo ""
echo "[3/3] Verifying no .env files are being pushed..."

TRACKED_ENV=$(git ls-files | grep -E '\.env$|\.env\.local$|\.env\.production$' | grep -v '\.env\.example$' || true)
if [ -n "${TRACKED_ENV}" ]; then
    echo "CRITICAL: .env files are tracked in the repository:"
    echo "${TRACKED_ENV}"
    echo ""
    echo "FAIL: Never push .env files to the repository."
    echo "  Remove them: git rm --cached <file>"
    echo "  Add to .gitignore if missing"
    exit 1
fi

STAGED_ENV=$(git diff --cached --name-only | grep -E '\.env$|\.env\.' | grep -v '\.env\.example$' || true)
if [ -n "${STAGED_ENV}" ]; then
    echo "CRITICAL: .env files staged for commit:"
    echo "${STAGED_ENV}"
    echo ""
    echo "FAIL: Unstage .env files: git reset HEAD <file>"
    exit 1
fi

echo "PASS: No .env files in push."

echo ""
echo "============================================"
echo "  All pre-push checks passed"
echo "============================================"
