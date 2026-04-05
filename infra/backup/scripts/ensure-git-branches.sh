#!/usr/bin/env bash
# Ensure main, staging, development exist locally (tracking origin when present).
# Does not push — run in CI or developer machine after cloning.

set -euo pipefail

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repo"; exit 1; }

for b in staging development; do
  if git show-ref --verify --quiet "refs/heads/${b}"; then
    echo "Branch ${b} already exists"
  elif git show-ref --verify --quiet "refs/remotes/origin/${b}"; then
    git branch --track "${b}" "origin/${b}"
    echo "Created local ${b} from origin/${b}"
  else
    git branch "${b}" main 2>/dev/null || git branch "${b}" master
    echo "Created ${b} from main/master"
  fi
done

echo "Done. Push with: git push -u origin staging development"
