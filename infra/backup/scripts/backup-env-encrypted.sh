#!/usr/bin/env bash
# Backs up .env-style files and TLS material into an encrypted tarball (GPG).
# Never store plaintext secrets in object storage. Rotate keys periodically.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

require_cmd gpg
require_cmd tar

TS="$(backup_timestamp)"
BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
COMPOSE_PROJECT_DIR="${COMPOSE_PROJECT_DIR:?Set COMPOSE_PROJECT_DIR}"
OUT_DIR="${BACKUP_ROOT}/config/${TS}"
ensure_dir "${OUT_DIR}"

STAGE="${OUT_DIR}/stage"
ensure_dir "${STAGE}"

i=0
while IFS= read -r -d '' candidate; do
  [[ -f "${candidate}" ]] || continue
  safe_name="$(echo "${candidate}" | tr '/ ' '__')"
  cp -a "${candidate}" "${STAGE}/${i}_${safe_name}"
  i=$((i + 1))
done < <(find "${COMPOSE_PROJECT_DIR}" \( -name ".env" -o -name ".env.*" \) -print0 2>/dev/null)

for extra in /etc/dealix/ssl/fullchain.pem /etc/dealix/ssl/privkey.pem; do
  [[ -f "${extra}" ]] && cp -a "${extra}" "${STAGE}/ssl_${i}_$(basename "${extra}")" && i=$((i + 1))
done

PLAIN_TAR="${OUT_DIR}/config-${TS}.tar.gz"
if [[ "${i}" -eq 0 ]]; then
  log "WARN: no config files found; writing placeholder tarball"
  touch "${STAGE}/.placeholder"
fi
tar -czf "${PLAIN_TAR}" -C "${OUT_DIR}" stage

ENC_OUT="${PLAIN_TAR}.gpg"
if [[ -n "${BACKUP_GPG_RECIPIENT:-}" ]]; then
  gpg --batch --yes -e -r "${BACKUP_GPG_RECIPIENT}" -o "${ENC_OUT}" "${PLAIN_TAR}"
elif [[ -n "${BACKUP_GPG_PASSPHRASE_FILE:-}" ]] && [[ -f "${BACKUP_GPG_PASSPHRASE_FILE}" ]]; then
  gpg --batch --yes --cipher-algo AES256 -c --passphrase-file "${BACKUP_GPG_PASSPHRASE_FILE}" -o "${ENC_OUT}" "${PLAIN_TAR}"
else
  die "Set BACKUP_GPG_RECIPIENT or BACKUP_GPG_PASSPHRASE_FILE for encryption"
fi

shred -u "${PLAIN_TAR}" 2>/dev/null || rm -f "${PLAIN_TAR}"
rm -rf "${STAGE}"

sha256sum "${ENC_OUT}" > "${ENC_OUT}.sha256"
echo "{\"kind\":\"config_encrypted\",\"timestamp\":\"${TS}\",\"path\":\"${ENC_OUT}\"}" > "${OUT_DIR}/manifest.json"
log "Encrypted config backup: ${ENC_OUT}"
echo "${OUT_DIR}"
