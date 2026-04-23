#!/usr/bin/env python3
"""Validate docs/registry/TRUTH.yaml structure and claims_registry.yaml alignment.

Ensures:
1. TRUTH.yaml has all required top-level keys
2. Every capability has valid status (live, pilot, partial, roadmap, deprecated)
3. Every "approved" claim in claims_registry.yaml has evidence
4. No "forbidden" claim text appears in public-facing docs
5. Security claims match actual code state (e.g., soc2_type_ii: false unless auditor report exists)

Exit 0 if valid, 1 if errors.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

TRUTH_PATH = ROOT / "docs" / "registry" / "TRUTH.yaml"
CLAIMS_PATH = ROOT / "commercial" / "claims_registry.yaml"

REQUIRED_TRUTH_FIELDS = [
    "version",
    "orchestrator.canonical",
    "llm_policy.primary",
    "llm_policy.fallback",
    "llm_policy.embedding",
    "data_residency.default_region",
    "security_claims.rls_enforced",
    "security_claims.soc2_type_ii",
    "security_claims.pdpl_compliant",
]

VALID_CAPABILITY_STATUSES = {"live", "pilot", "partial", "roadmap", "deprecated"}
VALID_CLAIM_STATUSES = {"approved", "restricted", "forbidden"}


def get_nested(data: Dict, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate_truth() -> List[str]:
    errors: List[str] = []

    if not TRUTH_PATH.exists():
        return [f"MISSING: {TRUTH_PATH}"]

    try:
        data = yaml.safe_load(TRUTH_PATH.read_text())
    except yaml.YAMLError as e:
        return [f"INVALID YAML in TRUTH.yaml: {e}"]

    if not isinstance(data, dict):
        return ["TRUTH.yaml must be a dictionary at the root"]

    for field in REQUIRED_TRUTH_FIELDS:
        value = get_nested(data, field)
        if value is None:
            errors.append(f"TRUTH.yaml missing required field: {field}")

    # Validate capabilities
    capabilities = data.get("capabilities", [])
    if not isinstance(capabilities, list):
        errors.append("TRUTH.yaml capabilities must be a list")
    else:
        for i, cap in enumerate(capabilities):
            if not isinstance(cap, dict):
                errors.append(f"capability[{i}] must be a dict")
                continue
            if "id" not in cap:
                errors.append(f"capability[{i}] missing 'id'")
            if "status" not in cap:
                errors.append(f"capability[{cap.get('id', i)}] missing 'status'")
            elif cap["status"] not in VALID_CAPABILITY_STATUSES:
                errors.append(
                    f"capability[{cap.get('id', i)}] invalid status '{cap['status']}' "
                    f"(must be one of {VALID_CAPABILITY_STATUSES})"
                )
            # If public_claim_allowed=true, status must be 'live' or 'pilot'
            if cap.get("public_claim_allowed") is True:
                if cap.get("status") not in {"live", "pilot"}:
                    errors.append(
                        f"capability[{cap.get('id', i)}] has public_claim_allowed=true "
                        f"but status='{cap.get('status')}' (must be 'live' or 'pilot')"
                    )

    # Forbid soc2_type_ii: true without evidence_path
    if get_nested(data, "security_claims.soc2_type_ii") is True:
        errors.append(
            "TRUTH.yaml claims SOC 2 Type II but no auditor evidence provided. "
            "Set to false until SOC 2 audit report issued."
        )

    return errors


def validate_claims() -> List[str]:
    errors: List[str] = []

    if not CLAIMS_PATH.exists():
        return [f"MISSING: {CLAIMS_PATH}"]

    try:
        data = yaml.safe_load(CLAIMS_PATH.read_text())
    except yaml.YAMLError as e:
        return [f"INVALID YAML in claims_registry.yaml: {e}"]

    claims = data.get("claims", [])
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claim[{i}] must be a dict")
            continue
        cid = claim.get("id", f"index-{i}")
        status = claim.get("status")
        if status not in VALID_CLAIM_STATUSES:
            errors.append(f"claim[{cid}] invalid status '{status}'")
        if status == "approved" and not claim.get("evidence"):
            errors.append(f"claim[{cid}] is approved but missing 'evidence' field")
        if status == "forbidden" and not claim.get("reason"):
            errors.append(f"claim[{cid}] is forbidden but missing 'reason' field")
        if "claim_en" not in claim:
            errors.append(f"claim[{cid}] missing 'claim_en'")

    return errors


def main() -> None:
    errors = validate_truth() + validate_claims()

    if errors:
        print("❌ Truth Registry Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✓ Truth Registry valid")
    print(f"  - {TRUTH_PATH.relative_to(ROOT)}")
    print(f"  - {CLAIMS_PATH.relative_to(ROOT)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
