#!/usr/bin/env bash
# Mirror all refs from origin to a backup remote (code backup: all branches + tags).
# Run from CI or a trusted host with SSH key to mirror repo.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

: "${GIT_MIRROR_URL:?Set GIT_MIRROR_URL}"

REPO_ROOT="${1:-.}"
cd "${REPO_ROOT}"

if [[ -n "${GIT_MIRROR_SSH_KEY:-}" ]] && [[ -f "${GIT_MIRROR_SSH_KEY}" ]]; then
  export GIT_SSH_COMMAND="ssh -i ${GIT_MIRROR_SSH_KEY} -o StrictHostKeyChecking=accept-new"
fi

git fetch --all --prune
git push --mirror "${GIT_MIRROR_URL}"

log "Mirror push complete to ${GIT_MIRROR_URL}"
