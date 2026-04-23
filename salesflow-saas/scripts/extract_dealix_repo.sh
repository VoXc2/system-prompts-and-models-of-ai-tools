#!/usr/bin/env bash
# extract_dealix_repo.sh — TASK-001 automation
#
# Extracts Dealix into a clean repository, preserving commit history.
# Usage:
#   ./scripts/extract_dealix_repo.sh <target_repo_url>
#
# Example:
#   ./scripts/extract_dealix_repo.sh git@github.com:dealix-io/platform.git
#
# Prerequisites:
#   - git-filter-repo installed (pip install git-filter-repo)
#   - SSH key configured for target org
#   - New empty GitHub repo created at <target_repo_url>

set -euo pipefail

TARGET_URL="${1:-}"
if [[ -z "$TARGET_URL" ]]; then
  echo "Usage: $0 <target_repo_url>"
  echo "Example: $0 git@github.com:dealix-io/platform.git"
  exit 1
fi

WORKDIR="${TMPDIR:-/tmp}/dealix-extraction-$$"
SOURCE_REPO="$(git rev-parse --show-toplevel)"

echo "→ Creating fresh clone at $WORKDIR"
git clone "$SOURCE_REPO" "$WORKDIR"
cd "$WORKDIR"

echo "→ Filtering repository to Dealix-only paths..."
git filter-repo \
  --path salesflow-saas/ \
  --path personal-brand-engine/ \
  --path sales_assets/ \
  --path-rename salesflow-saas/:

echo "→ Setting up target remote: $TARGET_URL"
git remote add origin "$TARGET_URL" 2>/dev/null || git remote set-url origin "$TARGET_URL"

echo "→ Pushing to new repo..."
git push -u origin main

echo ""
echo "✓ Extraction complete"
echo "  Working tree: $WORKDIR"
echo "  Target: $TARGET_URL"
echo ""
echo "Next steps (manual):"
echo "  1. Verify on GitHub: $(echo $TARGET_URL | sed 's|git@github.com:|https://github.com/|' | sed 's|\.git$||')"
echo "  2. Archive old fork OR make it private"
echo "  3. Rotate ALL secrets (see docs/internal/rotation_log.md)"
echo "  4. Update CI/CD to point to new repo"
echo "  5. Notify team + update README on old fork"
