#!/usr/bin/env bash
# Dealix — shared path resolution library.
# Source from any script:  . "$(dirname "$0")/lib/resolve-paths.sh"
# From hooks:              . "${_LIB_DIR}/resolve-paths.sh"
#
# Exports:
#   REPO_ROOT, PROJECT_ROOT,
#   BACKEND_DIR, FRONTEND_DIR, SALES_ASSETS_DIR,
#   HAS_BACKEND, HAS_FRONTEND, HAS_SALES_ASSETS  (1 | 0)
#   require_component <name>  — returns 0 if present, 1 + warning if absent

# ── 1. Repository root ────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export REPO_ROOT

# ── 2. Project root detection ─────────────────────
#   Probe for the salesflow-saas project directory using marker files.
_PROJECT_CANDIDATES=(
  "${REPO_ROOT}/salesflow-saas"
  "${REPO_ROOT}"
)
PROJECT_ROOT=""
for _candidate in "${_PROJECT_CANDIDATES[@]}"; do
  # CLAUDE.md is a unique marker for the Dealix project root
  if [[ -f "${_candidate}/CLAUDE.md" ]]; then
    PROJECT_ROOT="${_candidate}"
    break
  fi
  # Fallback: docker-compose.yml + backend/ is also a strong signal
  if [[ -f "${_candidate}/docker-compose.yml" && -d "${_candidate}/backend" ]]; then
    PROJECT_ROOT="${_candidate}"
    break
  fi
done
if [[ -z "${PROJECT_ROOT}" ]]; then
  echo "[WARN] Could not detect Dealix project root. Falling back to repo root." >&2
  PROJECT_ROOT="${REPO_ROOT}"
fi
export PROJECT_ROOT

# ── 3. Component detection ────────────────────────
_detect_dir() {
  for _path in "$@"; do
    if [[ -d "${_path}" ]]; then
      echo "${_path}"
      return 0
    fi
  done
  return 1
}

BACKEND_DIR="$(_detect_dir \
  "${PROJECT_ROOT}/backend" \
  "${REPO_ROOT}/backend" \
)" && HAS_BACKEND=1 || HAS_BACKEND=0
export BACKEND_DIR HAS_BACKEND

FRONTEND_DIR="$(_detect_dir \
  "${PROJECT_ROOT}/frontend" \
  "${REPO_ROOT}/frontend" \
)" && HAS_FRONTEND=1 || HAS_FRONTEND=0
export FRONTEND_DIR HAS_FRONTEND

SALES_ASSETS_DIR="$(_detect_dir \
  "${PROJECT_ROOT}/sales_assets" \
  "${REPO_ROOT}/sales_assets" \
  "${REPO_ROOT}/salesflow-saas/sales_assets" \
)" && HAS_SALES_ASSETS=1 || HAS_SALES_ASSETS=0
export SALES_ASSETS_DIR HAS_SALES_ASSETS

# ── 4. Helper: require a component or skip ────────
require_component() {
  local component="$1"
  local var_name="HAS_${component^^}"
  if [[ "${!var_name}" != "1" ]]; then
    echo "[SKIP] ${component} not found in this layout." >&2
    return 1
  fi
  return 0
}
export -f require_component
