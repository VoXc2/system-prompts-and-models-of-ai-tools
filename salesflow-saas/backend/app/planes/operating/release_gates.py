"""
Release Gate System — environment protection, deployment gates, provenance.

Ensures every release has rulesets + environment protection + OIDC + provenance.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class Environment(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"


class GateStatus(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BYPASSED = "bypassed"


class ReleaseGate(BaseModel):
    gate_id: str
    name: str
    name_ar: str
    environment: Environment
    status: GateStatus = GateStatus.PENDING
    required: bool = True
    checked_at: Optional[datetime] = None
    checked_by: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)


class ReleaseManifest(BaseModel):
    release_id: str
    version: str
    environment: Environment
    gates: list[ReleaseGate] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    deployed_by: Optional[str] = None
    rollback_plan: Optional[str] = None
    artifact_checksum: Optional[str] = None
    oidc_verified: bool = False
    attestation_ref: Optional[str] = None

    @property
    def all_gates_passed(self) -> bool:
        return all(
            g.status == GateStatus.PASSED
            for g in self.gates
            if g.required
        )


DEFAULT_GATES: dict[Environment, list[dict[str, str]]] = {
    Environment.STAGING: [
        {"name": "Unit Tests", "name_ar": "اختبارات الوحدة"},
        {"name": "Integration Tests", "name_ar": "اختبارات التكامل"},
        {"name": "Security Scan", "name_ar": "فحص أمني"},
        {"name": "PDPL Compliance Check", "name_ar": "فحص امتثال PDPL"},
    ],
    Environment.CANARY: [
        {"name": "Staging Smoke Test", "name_ar": "اختبار Staging"},
        {"name": "Arabic UI Validation", "name_ar": "تحقق واجهة عربية"},
        {"name": "Performance Baseline", "name_ar": "خط أساس الأداء"},
    ],
    Environment.PRODUCTION: [
        {"name": "Canary Health (30min)", "name_ar": "صحة Canary (30 دقيقة)"},
        {"name": "Rollback Plan Documented", "name_ar": "خطة التراجع موثقة"},
        {"name": "OIDC Verification", "name_ar": "تحقق OIDC"},
        {"name": "Artifact Attestation", "name_ar": "تصديق القطع"},
    ],
}
