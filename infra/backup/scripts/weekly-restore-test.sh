#!/usr/bin/env bash
# Weekly restore drill: restore pg_dump to a disposable database and run health SQL.
# Requires: createdb empty DB, same Postgres major version as production.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

DUMP="${1:?Usage: weekly-restore-test.sh /path/to/latest.dump}"
: "${PGHOST:-localhost}"
: "${PGUSER:?}"
RESTORE_DB="${RESTORE_TEST_DBNAME:-dealix_restore_test}"

require_cmd pg_restore
require_cmd dropdb
require_cmd createdb

log "Recreating ${RESTORE_DB}"
dropdb -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER}" --if-exists "${RESTORE_DB}" || true
createdb -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER}" "${RESTORE_DB}"

log "pg_restore (dry-run connections only — use --no-owner for cross-cluster)"
pg_restore -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER}" -d "${RESTORE_DB}" --no-owner --jobs=4 "${DUMP}"

psql -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER}" -d "${RESTORE_DB}" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"

log "Restore test OK — drop test DB when done"
slack_notify ":white_check_mark: Weekly DB restore test passed on $(hostname)"
exit 0
