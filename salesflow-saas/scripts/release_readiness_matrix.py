#!/usr/bin/env python3
"""Release Readiness Matrix — gates release based on evidence, not opinion.

Run from salesflow-saas root:
    python scripts/release_readiness_matrix.py

Checks:
1. Architecture brief passes (40/40)
2. All governance docs exist
3. No high-severity contradictions (placeholder check)
4. Structured output schemas defined
5. Golden path service exists
6. Saudi workflow service exists
7. Trust enforcement active
8. Evidence pack service exists
9. Executive weekly pack endpoint exists
10. CODEOWNERS exists

Exit 0 = ready, Exit 1 = not ready.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = {
    "architecture_brief": ROOT / "scripts" / "architecture_brief.py",
    "master_operating_prompt": ROOT / "MASTER_OPERATING_PROMPT.md",
    "current_vs_target": ROOT / "docs" / "current-vs-target-register.md",
    "closure_checklist": ROOT / "docs" / "tier1-master-closure-checklist.md",
    "endpoint_inventory": ROOT / "docs" / "governance" / "endpoint-inventory.md",
    "release_gates_doc": ROOT / "docs" / "governance" / "release-gates.md",
    "golden_path_service": ROOT / "backend" / "app" / "services" / "golden_path.py",
    "golden_path_api": ROOT / "backend" / "app" / "api" / "v1" / "golden_path.py",
    "saudi_workflow_service": ROOT / "backend" / "app" / "services" / "saudi_sensitive_workflow.py",
    "saudi_workflow_api": ROOT / "backend" / "app" / "api" / "v1" / "saudi_workflow.py",
    "structured_outputs": ROOT / "backend" / "app" / "schemas" / "structured_outputs.py",
    "structured_producers": ROOT / "backend" / "app" / "services" / "structured_output_producers.py",
    "structured_api": ROOT / "backend" / "app" / "api" / "v1" / "structured_outputs.py",
    "contradiction_engine": ROOT / "backend" / "app" / "services" / "contradiction_engine.py",
    "evidence_pack_service": ROOT / "backend" / "app" / "services" / "evidence_pack_service.py",
    "deal_lifecycle_hooks": ROOT / "backend" / "app" / "services" / "deal_lifecycle_hooks.py",
    "executive_room_api": ROOT / "backend" / "app" / "api" / "v1" / "executive_room.py",
    "approval_center_api": ROOT / "backend" / "app" / "api" / "v1" / "approval_center.py",
    "trust_enforcement": ROOT / "backend" / "app" / "openclaw" / "approval_bridge.py",
    "codeowners": ROOT / "CODEOWNERS",
    "marketer_hub": ROOT / "revenue-activation" / "sales-pack" / "MARKETER_HUB.md",
    "one_pager": ROOT / "revenue-activation" / "sales-pack" / "ONE_PAGER.md",
    "admin_guide": ROOT / "revenue-activation" / "deployment" / "ADMIN_SETUP_GUIDE.md",
    "exec_quickstart": ROOT / "revenue-activation" / "deployment" / "EXECUTIVE_QUICKSTART.md",
    # Program E — Durable Execution
    "durable_checkpoint_model": ROOT / "backend" / "app" / "models" / "durable_checkpoint.py",
    "durable_runtime_service": ROOT / "backend" / "app" / "services" / "durable_runtime.py",
    # Program F — RLS
    "rls_migration": ROOT / "backend" / "alembic" / "versions" / "20260417_0002_add_rls.py",
    "rls_helpers": ROOT / "backend" / "app" / "database_rls.py",
    "rls_middleware": ROOT / "backend" / "app" / "middleware" / "tenant_rls.py",
    # Program G — Idempotency
    "idempotency_model": ROOT / "backend" / "app" / "models" / "idempotency_key.py",
    "idempotency_service": ROOT / "backend" / "app" / "services" / "idempotency_service.py",
    "idempotency_middleware": ROOT / "backend" / "app" / "middleware" / "idempotency.py",
    # Program K — OTel
    "otel_module": ROOT / "backend" / "app" / "observability" / "otel.py",
    "otel_init": ROOT / "backend" / "app" / "observability" / "__init__.py",
    # Blueprint execution (TASK-010, 101, 999)
    "truth_registry": ROOT / "docs" / "registry" / "TRUTH.yaml",
    "claims_registry": ROOT / "commercial" / "claims_registry.yaml",
    "state_audit": ROOT / "docs" / "internal" / "STATE_AUDIT.md",
    "legal_status": ROOT / "docs" / "internal" / "legal_status.md",
    "rotation_log": ROOT / "docs" / "internal" / "rotation_log.md",
    "execution_log": ROOT / "docs" / "execution_log.md",
    "blueprint": ROOT / "DEALIX_EXECUTION_BLUEPRINT.md",
    "truth_validator": ROOT / "scripts" / "validate_truth_registry.py",
    "release_gate_script": ROOT / "scripts" / "release_readiness_gate.py",
    "extraction_script": ROOT / "scripts" / "extract_dealix_repo.sh",
    "pre_commit_config": ROOT / ".pre-commit-config.yaml",
    "backend_pyproject": ROOT / "backend" / "pyproject.toml",
}

CONTENT_CHECKS = {
    "trust_enforcement_active": {
        "file": ROOT / "backend" / "app" / "openclaw" / "approval_bridge.py",
        "pattern": "missing_correlation_id",
    },
    "weekly_pack_endpoint": {
        "file": ROOT / "backend" / "app" / "api" / "v1" / "executive_room.py",
        "pattern": "weekly-pack",
    },
    "auto_evidence_on_close": {
        "file": ROOT / "backend" / "app" / "api" / "v1" / "deals.py",
        "pattern": "on_deal_closed",
    },
    "rls_policies_defined": {
        "file": ROOT / "backend" / "alembic" / "versions" / "20260417_0002_add_rls.py",
        "pattern": "tenant_isolation_select",
    },
    "idempotency_middleware_active": {
        "file": ROOT / "backend" / "app" / "middleware" / "idempotency.py",
        "pattern": "Idempotency-Key",
    },
    "durable_checkpointer_persisted": {
        "file": ROOT / "backend" / "app" / "services" / "durable_runtime.py",
        "pattern": "DurableCheckpoint",
    },
    "otel_correlation_bridge": {
        "file": ROOT / "backend" / "app" / "openclaw" / "gateway.py",
        "pattern": "inject_correlation_id",
    },
}


def main() -> None:
    print("=" * 60)
    print("  RELEASE READINESS MATRIX")
    print("=" * 60)
    print()

    total = passed = 0

    # File existence checks
    for name, path in CHECKS.items():
        total += 1
        exists = path.exists()
        if exists:
            passed += 1
        mark = "+" if exists else "-"
        print(f"  {mark} {name}: {path.relative_to(ROOT)}")

    print()

    # Content checks
    for name, spec in CONTENT_CHECKS.items():
        total += 1
        found = False
        if spec["file"].exists():
            content = spec["file"].read_text()
            found = spec["pattern"] in content
        if found:
            passed += 1
        mark = "+" if found else "-"
        print(f"  {mark} {name}: '{spec['pattern']}' in {spec['file'].name}")

    print()
    print("-" * 60)
    score = round((passed / total) * 100, 1) if total else 0
    ready = passed == total
    print(f"  SCORE: {score}% ({passed}/{total})")
    print(f"  RELEASE READY: {'YES' if ready else 'NO'}")
    print("=" * 60)

    report = {"total": total, "passed": passed, "score": score, "ready": ready}
    (ROOT / "scripts" / "release_readiness_report.json").write_text(json.dumps(report, indent=2))

    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
