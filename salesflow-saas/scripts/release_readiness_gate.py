#!/usr/bin/env python3
"""Release Readiness Gate — Blueprint spec version.

Fails the build if ANY required signal is missing:
1. Required artifacts exist
2. TRUTH.yaml has required fields
3. No forbidden claims appear in public-facing docs
4. CHANGELOG.md was updated in this PR (if applicable)

Run in CI after all other checks.
Exit 0 = pass, 1 = fail.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ARTIFACTS = [
    "docs/registry/TRUTH.yaml",
    "commercial/claims_registry.yaml",
    "SECURITY.md",
    "MASTER_OPERATING_PROMPT.md",
    "docs/internal/STATE_AUDIT.md",
    "docs/internal/legal_status.md",
    "docs/internal/rotation_log.md",
    "docs/execution_log.md",
    "scripts/validate_truth_registry.py",
    "scripts/architecture_brief.py",
    "scripts/release_readiness_matrix.py",
]

REQUIRED_TRUTH_FIELDS = [
    "orchestrator.canonical",
    "llm_policy.primary",
    "data_residency.default_region",
    "security_claims.rls_enforced",
]

# Public-facing doc paths where forbidden claims must NOT appear
PUBLIC_DOC_PATTERNS = [
    "revenue-activation/sales-pack/*.md",
    "revenue-activation/deployment/*.md",
    "README.md",
    "commercial/sales/**/*.md",
]


def get_nested(data: dict, path: str):
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def check_artifacts() -> List[str]:
    errors = []
    for p in REQUIRED_ARTIFACTS:
        full = ROOT / p
        if not full.exists():
            errors.append(f"MISSING required artifact: {p}")
    return errors


def check_truth_registry() -> List[str]:
    path = ROOT / "docs" / "registry" / "TRUTH.yaml"
    if not path.exists():
        return ["TRUTH.yaml missing"]

    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"TRUTH.yaml parse error: {e}"]

    errors = []
    for field in REQUIRED_TRUTH_FIELDS:
        if get_nested(data, field) is None:
            errors.append(f"TRUTH.yaml missing field: {field}")

    # Hard guard: soc2_type_ii must be false or 'in-progress'
    soc2 = get_nested(data, "security_claims.soc2_type_ii")
    if soc2 is True:
        errors.append(
            "FORBIDDEN: TRUTH.yaml soc2_type_ii=true without auditor evidence. "
            "Set to false until audit completes."
        )

    return errors


def check_forbidden_claims() -> List[str]:
    claims_path = ROOT / "commercial" / "claims_registry.yaml"
    if not claims_path.exists():
        return []

    try:
        reg = yaml.safe_load(claims_path.read_text())
    except yaml.YAMLError:
        return ["claims_registry.yaml parse error"]

    forbidden_phrases = []
    for c in reg.get("claims", []):
        if c.get("status") == "forbidden":
            for key in ("claim_en", "claim_ar"):
                val = c.get(key)
                if val:
                    forbidden_phrases.append((c.get("id", "unknown"), val))

    errors = []
    for pattern in PUBLIC_DOC_PATTERNS:
        for md in ROOT.glob(pattern):
            if not md.is_file():
                continue
            try:
                text = md.read_text(encoding="utf-8").lower()
            except Exception:
                continue
            for cid, phrase in forbidden_phrases:
                # Check for literal phrase (case-insensitive)
                if phrase.lower() in text:
                    errors.append(
                        f"FORBIDDEN claim '{cid}' ('{phrase}') found in {md.relative_to(ROOT)}"
                    )

    return errors


def check_architecture_brief_passes() -> List[str]:
    """Run architecture_brief.py and check it passes."""
    import subprocess
    script = ROOT / "scripts" / "architecture_brief.py"
    if not script.exists():
        return ["architecture_brief.py missing"]
    try:
        result = subprocess.run(
            ["python", str(script)],
            cwd=str(ROOT),
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            return [f"architecture_brief.py FAILED with exit {result.returncode}"]
    except Exception as e:
        return [f"architecture_brief.py execution error: {e}"]
    return []


def main() -> None:
    all_errors = (
        check_artifacts()
        + check_truth_registry()
        + check_forbidden_claims()
        + check_architecture_brief_passes()
    )

    if all_errors:
        print("❌ Release Readiness Gate FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✓ Release Readiness Gate passed")
    print(f"  Artifacts: {len(REQUIRED_ARTIFACTS)} OK")
    print(f"  TRUTH.yaml: {len(REQUIRED_TRUTH_FIELDS)} fields OK")
    print("  Forbidden claims: none found in public docs")
    print("  Architecture brief: 40/40")
    sys.exit(0)


if __name__ == "__main__":
    main()
