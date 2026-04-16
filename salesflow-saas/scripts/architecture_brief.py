#!/usr/bin/env python3
"""
Dealix Architecture Spine Check — architecture_brief.py

Run before any development work to verify project integrity:
    python scripts/architecture_brief.py
    py -3 scripts/architecture_brief.py   # Windows

Checks:
  1. Required governance docs exist
  2. Claude commands are intact
  3. No stale path assumptions
  4. Docs cross-reference consistency
  5. Key code directories present
"""

import os
import sys
import re
from pathlib import Path

# ── Detect project root ──────────────────────────────
def find_project_root():
    """Find the Dealix project root (contains CLAUDE.md)."""
    # Try script directory first
    script_dir = Path(__file__).resolve().parent.parent
    if (script_dir / "CLAUDE.md").exists():
        return script_dir
    # Try repo root / salesflow-saas
    repo_root = script_dir.parent
    candidate = repo_root / "salesflow-saas"
    if (candidate / "CLAUDE.md").exists():
        return candidate
    # Fallback: walk up from cwd
    cwd = Path.cwd()
    for p in [cwd, cwd.parent, cwd.parent.parent]:
        if (p / "CLAUDE.md").exists():
            return p
        if (p / "salesflow-saas" / "CLAUDE.md").exists():
            return p / "salesflow-saas"
    print("ERROR: Cannot find Dealix project root (CLAUDE.md)")
    sys.exit(1)

ROOT = find_project_root()
PASS = 0
WARN = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")

def warn(msg):
    global WARN
    WARN += 1
    print(f"  ⚠ {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")

def check_exists(path, label, required=True):
    full = ROOT / path
    if full.exists():
        ok(f"{label}: {path}")
        return True
    elif required:
        fail(f"{label}: {path} — MISSING")
        return False
    else:
        warn(f"{label}: {path} — missing (optional)")
        return False

# ── 1. Governance Docs ────────────────────────────────
print("\n[1/5] Governance Documents")
print("─" * 40)

GOVERNANCE_DOCS = [
    ("MASTER_OPERATING_PROMPT.md", "Operating Constitution"),
    ("MASTER-BLUEPRINT.mdc", "Architecture Blueprint"),
    ("docs/ai-operating-model.md", "AI Operating Model"),
    ("docs/dealix-six-tracks.md", "Six Tracks"),
    ("docs/governance/planes-and-runtime.md", "Planes & Runtime"),
    ("docs/governance/execution-fabric.md", "Execution Fabric"),
    ("docs/governance/trust-fabric.md", "Trust Fabric"),
    ("docs/governance/saudi-compliance-and-ai-governance.md", "Saudi Compliance"),
    ("docs/governance/technology-radar-tier1.md", "Technology Radar"),
    ("docs/execution-matrix-90d-tier1.md", "90-Day Execution Matrix"),
    ("docs/adr/0001-tier1-execution-policy-spikes.md", "ADR-0001 Policy Spikes"),
]

for path, label in GOVERNANCE_DOCS:
    check_exists(path, label)

# ── 2. Claude Commands ────────────────────────────────
print("\n[2/5] Claude Commands")
print("─" * 40)

COMMANDS = [
    ".claude/commands/architecture-review.md",
    ".claude/commands/security-check.md",
    ".claude/commands/release-prep.md",
    ".claude/commands/review-pr.md",
    ".claude/commands/generate-tests.md",
]

for path in COMMANDS:
    check_exists(path, "Command")

# Verify commands reference PROJECT_ROOT
for path in COMMANDS:
    full = ROOT / path
    if full.exists():
        content = full.read_text(encoding="utf-8", errors="replace")
        if "PROJECT_ROOT" in content or "$PROJECT_ROOT" in content:
            ok(f"  └─ {path} uses PROJECT_ROOT")
        else:
            warn(f"  └─ {path} does NOT reference PROJECT_ROOT")

# ── 3. Path Assumptions ──────────────────────────────
print("\n[3/5] Path Assumptions (checking hooks & scripts)")
print("─" * 40)

SCRIPTS_TO_CHECK = [
    ".claude/hooks/pre-commit.sh",
    ".claude/hooks/pre-push.sh",
    "scripts/grand_launch_verify.sh",
    "scripts/grand_launch_verify.ps1",
    "scripts/package_dealix_marketing_assets.sh",
    "scripts/package_dealix_marketing_assets.ps1",
    "scripts/run_local.ps1",
]

BAD_PATTERNS = [
    # Old patterns that assume backend at repo root
    (r'\$\{?ROOT_DIR\}?/backend', "Uses ROOT_DIR/backend (should use resolve-paths.sh)"),
    (r'git rev-parse --show-toplevel.*\n.*backend', "git toplevel + backend (potential path bug)"),
]

for path in SCRIPTS_TO_CHECK:
    full = ROOT / path
    if not full.exists():
        warn(f"Script missing: {path}")
        continue
    ok(f"Script exists: {path}")
    content = full.read_text(encoding="utf-8", errors="replace")
    for pattern, msg in BAD_PATTERNS:
        if re.search(pattern, content, re.MULTILINE):
            fail(f"  └─ {path}: {msg}")

# Check resolve-paths.sh exists
check_exists("scripts/lib/resolve-paths.sh", "Shared path resolver")
check_exists("scripts/lib/Resolve-DealixPaths.ps1", "Shared PS path resolver")

# ── 4. Key Code Directories ──────────────────────────
print("\n[4/5] Key Code Directories")
print("─" * 40)

CODE_DIRS = [
    ("backend/app/services/", "Backend Services"),
    ("backend/app/models/", "Database Models"),
    ("backend/app/api/v1/", "API Routes"),
    ("backend/app/workers/", "Celery Workers"),
    ("backend/app/integrations/", "Integrations"),
    ("backend/app/services/pdpl/", "PDPL Compliance"),
    ("backend/app/services/ai/", "AI Engine"),
    ("backend/app/openclaw/", "OpenClaw Runtime"),
    ("backend/tests/", "Tests"),
    ("frontend/src/", "Frontend Source"),
    ("ai-agents/prompts/", "Agent Prompts"),
]

for path, label in CODE_DIRS:
    check_exists(path, label, required=False)

# ── 5. Cross-Reference Consistency ───────────────────
print("\n[5/5] Cross-Reference Consistency")
print("─" * 40)

# Check ARCHITECTURE.md agent count
arch_file = ROOT / "docs/ARCHITECTURE.md"
if arch_file.exists():
    content = arch_file.read_text(encoding="utf-8", errors="replace")
    if "18 specialized agents" in content:
        warn("ARCHITECTURE.md says '18 agents' — should be 19 (see AGENT-MAP.md)")
    elif "19 specialized agents" in content:
        ok("ARCHITECTURE.md agent count matches AGENT-MAP.md")
    else:
        ok("ARCHITECTURE.md agent count (no specific number found)")

# Check module-map completion claim
module_map = ROOT / "memory/architecture/module-map.md"
if module_map.exists():
    content = module_map.read_text(encoding="utf-8", errors="replace")
    if "~90%" in content and "Completion" in content:
        warn("module-map.md claims ~90% completion — verify against saas-readiness-audit.md (45%)")

# ── Summary ──────────────────────────────────────────
print("\n" + "═" * 50)
print(f"  Architecture Spine Check Summary")
print(f"  ✓ Pass: {PASS}")
print(f"  ⚠ Warn: {WARN}")
print(f"  ✗ Fail: {FAIL}")
print("═" * 50)

if FAIL > 0:
    print(f"\n  {FAIL} critical issues found. Fix before proceeding.")
    sys.exit(1)
elif WARN > 0:
    print(f"\n  {WARN} warnings. Review and address when possible.")
    sys.exit(0)
else:
    print("\n  All checks passed. Architecture is consistent.")
    sys.exit(0)
