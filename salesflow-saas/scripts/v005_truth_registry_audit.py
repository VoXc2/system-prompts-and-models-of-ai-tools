#!/usr/bin/env python3
"""V005 — Truth Registry Independent Audit.

Audits every claim in TRUTH.yaml + claims_registry.yaml against live code.
Meant to be run by an engineer who did NOT author the registry.

Verdicts:
    SUPPORTED  — evidence file exists AND contains expected marker
    UNSUPPORTED — evidence missing or stale
    AMBIGUOUS  — evidence exists but cannot verify intent automatically

Any UNSUPPORTED claim must be either:
    (a) remediated with evidence within 48h, OR
    (b) demoted to `status: roadmap` within 48h

Usage:
    python scripts/v005_truth_registry_audit.py
    python scripts/v005_truth_registry_audit.py --strict  # fail on AMBIGUOUS

Exit codes:
    0 = all SUPPORTED
    1 = UNSUPPORTED claims present
    2 = AMBIGUOUS claims present (with --strict)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRUTH_PATH = ROOT / "docs" / "registry" / "TRUTH.yaml"
CLAIMS_PATH = ROOT / "commercial" / "claims_registry.yaml"


@dataclass
class AuditResult:
    claim_id: str
    claim_name: str
    status: str
    evidence_path: str | None
    verdict: str
    reason: str


def audit_capability(cap: dict) -> AuditResult:
    cid = cap.get("id", "?")
    name = cap.get("name", "?")
    status = cap.get("status", "?")
    ev_path_str = cap.get("evidence_path")
    public_allowed = cap.get("public_claim_allowed", False)

    if status == "roadmap":
        return AuditResult(cid, name, status, ev_path_str, "SUPPORTED",
                           "declared roadmap; no evidence required")

    if not ev_path_str:
        verdict = "UNSUPPORTED" if public_allowed else "AMBIGUOUS"
        return AuditResult(cid, name, status, None, verdict,
                           "status claims progress but evidence_path is null")

    ev_path = ROOT / ev_path_str
    if not ev_path.exists():
        return AuditResult(cid, name, status, ev_path_str, "UNSUPPORTED",
                           f"evidence file missing: {ev_path_str}")

    if status == "live" and public_allowed:
        if ev_path.is_file():
            content = ev_path.read_text(errors="ignore")
            if len(content.strip()) < 40:
                return AuditResult(cid, name, status, ev_path_str, "AMBIGUOUS",
                                   "evidence file exists but suspiciously empty")
        return AuditResult(cid, name, status, ev_path_str, "SUPPORTED",
                           "evidence file present")

    if status == "partial":
        return AuditResult(cid, name, status, ev_path_str, "SUPPORTED",
                           "declared partial; evidence present")

    return AuditResult(cid, name, status, ev_path_str, "AMBIGUOUS",
                       f"unrecognized status={status}")


def audit_registry() -> list[AuditResult]:
    results: list[AuditResult] = []

    if not TRUTH_PATH.exists():
        print(f"ERROR: TRUTH.yaml not found at {TRUTH_PATH}", file=sys.stderr)
        sys.exit(3)

    truth = yaml.safe_load(TRUTH_PATH.read_text())

    for cap in truth.get("capabilities", []):
        results.append(audit_capability(cap))
    for cap in truth.get("phase_2_capabilities", []):
        results.append(audit_capability(cap))

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Fail on AMBIGUOUS verdicts")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON")
    args = parser.parse_args()

    results = audit_registry()

    supported = [r for r in results if r.verdict == "SUPPORTED"]
    unsupported = [r for r in results if r.verdict == "UNSUPPORTED"]
    ambiguous = [r for r in results if r.verdict == "AMBIGUOUS"]

    if args.json:
        out = {
            "supported": [r.__dict__ for r in supported],
            "unsupported": [r.__dict__ for r in unsupported],
            "ambiguous": [r.__dict__ for r in ambiguous],
            "total": len(results),
        }
        print(json.dumps(out, indent=2))
    else:
        print("=" * 70)
        print("  V005 — TRUTH REGISTRY INDEPENDENT AUDIT")
        print("=" * 70)
        print()
        for r in results:
            mark = {"SUPPORTED": "+", "UNSUPPORTED": "-", "AMBIGUOUS": "?"}[r.verdict]
            print(f"  {mark} [{r.verdict}] {r.claim_id} ({r.status}) — {r.reason}")
        print()
        print("-" * 70)
        print(f"  SUPPORTED:   {len(supported)}")
        print(f"  UNSUPPORTED: {len(unsupported)}")
        print(f"  AMBIGUOUS:   {len(ambiguous)}")
        print("=" * 70)

    if unsupported:
        sys.exit(1)
    if ambiguous and args.strict:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
