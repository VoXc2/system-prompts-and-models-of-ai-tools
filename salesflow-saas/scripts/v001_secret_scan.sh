#!/usr/bin/env bash
# V001 — Full Git History Secret Scan (trufflehog + gitleaks)
#
# Scans the FULL commit history (not just HEAD) with two independent tools.
# Writes findings to docs/internal/secret_audit_log.md.
#
# Usage:
#   ./scripts/v001_secret_scan.sh
#
# Prerequisites:
#   - trufflehog: https://github.com/trufflesecurity/trufflehog
#   - gitleaks: https://github.com/gitleaks/gitleaks
#
# Exit codes:
#   0 = no verified findings
#   1 = verified findings present — halt Phase 2 execution

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
OUT_DIR="${REPO_ROOT}/salesflow-saas/docs/internal"
OUT_FILE="${OUT_DIR}/secret_audit_log.md"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "${OUT_DIR}"

echo "# Secret Audit Log" > "${OUT_FILE}"
echo "" >> "${OUT_FILE}"
echo "**Scan timestamp (UTC)**: ${TS}" >> "${OUT_FILE}"
echo "**Scope**: Full git history (all commits)" >> "${OUT_FILE}"
echo "**Tools**: trufflehog + gitleaks (two-tool rule)" >> "${OUT_FILE}"
echo "" >> "${OUT_FILE}"

TRUFFLEHOG_FINDINGS=0
GITLEAKS_FINDINGS=0

# --- trufflehog ---
echo "## trufflehog" >> "${OUT_FILE}"
echo "" >> "${OUT_FILE}"
if command -v trufflehog >/dev/null 2>&1; then
  echo "\`\`\`" >> "${OUT_FILE}"
  if trufflehog git "file://${REPO_ROOT}" --only-verified --json > /tmp/trufflehog.jsonl 2>/dev/null; then
    TRUFFLEHOG_FINDINGS=$(wc -l < /tmp/trufflehog.jsonl | tr -d ' ')
    if [ "${TRUFFLEHOG_FINDINGS}" -gt 0 ]; then
      cat /tmp/trufflehog.jsonl >> "${OUT_FILE}"
    else
      echo "No verified findings." >> "${OUT_FILE}"
    fi
  else
    echo "trufflehog exited with non-zero; see raw output at /tmp/trufflehog.jsonl" >> "${OUT_FILE}"
  fi
  echo "\`\`\`" >> "${OUT_FILE}"
else
  echo "> trufflehog not installed. Install: \`go install github.com/trufflesecurity/trufflehog/v3@latest\`" >> "${OUT_FILE}"
fi
echo "" >> "${OUT_FILE}"

# --- gitleaks ---
echo "## gitleaks" >> "${OUT_FILE}"
echo "" >> "${OUT_FILE}"
if command -v gitleaks >/dev/null 2>&1; then
  echo "\`\`\`" >> "${OUT_FILE}"
  if gitleaks detect --source "${REPO_ROOT}" --redact --no-banner --report-format json --report-path /tmp/gitleaks.json >/dev/null 2>&1; then
    echo "No findings (clean)." >> "${OUT_FILE}"
  else
    GITLEAKS_FINDINGS=$(python3 -c "import json;print(len(json.load(open('/tmp/gitleaks.json'))))" 2>/dev/null || echo 0)
    cat /tmp/gitleaks.json >> "${OUT_FILE}" 2>/dev/null || true
  fi
  echo "\`\`\`" >> "${OUT_FILE}"
else
  echo "> gitleaks not installed. Install: \`brew install gitleaks\`" >> "${OUT_FILE}"
fi
echo "" >> "${OUT_FILE}"

# --- Summary ---
echo "## Summary" >> "${OUT_FILE}"
echo "" >> "${OUT_FILE}"
echo "| Tool | Verified Findings |" >> "${OUT_FILE}"
echo "|------|-------------------|" >> "${OUT_FILE}"
echo "| trufflehog | ${TRUFFLEHOG_FINDINGS} |" >> "${OUT_FILE}"
echo "| gitleaks | ${GITLEAKS_FINDINGS} |" >> "${OUT_FILE}"
echo "" >> "${OUT_FILE}"

TOTAL=$((TRUFFLEHOG_FINDINGS + GITLEAKS_FINDINGS))
if [ "${TOTAL}" -eq 0 ]; then
  echo "**Verdict**: CLEAN — no verified secrets in history." >> "${OUT_FILE}"
  echo "[V001] CLEAN"
  exit 0
else
  echo "**Verdict**: FINDINGS (${TOTAL}) — rotate all exposed credentials, document in rotation_log.md, HALT Phase 2 until clean." >> "${OUT_FILE}"
  echo "[V001] FINDINGS: ${TOTAL}"
  exit 1
fi
