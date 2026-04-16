"""Operating Plane — Release governance, environment protection, compliance gates."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ReleaseStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class ReleaseGate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    gate_type: str  # "test_pass", "security_scan", "code_review", "deployment_protection", "smoke_test", "compliance_check"
    required: bool = True
    passed: bool = False
    checked_at: datetime | None = None
    checked_by: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ReleaseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    release_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str
    environment: EnvironmentType
    status: ReleaseStatus = ReleaseStatus.DRAFT
    gates: list[ReleaseGate] = Field(default_factory=list)
    canary_percentage: int = 0
    rollback_plan: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: datetime | None = None
    deployed_by: str | None = None
    commit_sha: str = ""
    attestation_digest: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)


class ComplianceMatrix(BaseModel):
    """Saudi regulatory compliance tracking."""
    model_config = ConfigDict(from_attributes=True)
    matrix_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    pdpl_controls: list[dict[str, Any]] = Field(default_factory=list)
    nca_ecc_controls: list[dict[str, Any]] = Field(default_factory=list)
    ai_governance_controls: list[dict[str, Any]] = Field(default_factory=list)
    last_assessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assessed_by: str = ""
    overall_score: float = 0.0
    
    @classmethod
    def default_saudi_matrix(cls, tenant_id: str = "") -> "ComplianceMatrix":
        return cls(
            tenant_id=tenant_id,
            pdpl_controls=[
                {"id": "PDPL-1", "name": "Consent Management", "name_ar": "إدارة الموافقة", "status": "implemented", "evidence": "consent_service.py"},
                {"id": "PDPL-2", "name": "Data Subject Rights", "name_ar": "حقوق أصحاب البيانات", "status": "implemented", "evidence": "data_request model"},
                {"id": "PDPL-3", "name": "Purpose Limitation", "name_ar": "تحديد الغرض", "status": "implemented", "evidence": "consent.purpose field"},
                {"id": "PDPL-4", "name": "Data Minimization", "name_ar": "تقليل البيانات", "status": "partial", "evidence": ""},
                {"id": "PDPL-5", "name": "Retention Policy", "name_ar": "سياسة الاحتفاظ", "status": "implemented", "evidence": "12-month auto-expire"},
                {"id": "PDPL-6", "name": "Cross-border Transfer", "name_ar": "النقل عبر الحدود", "status": "partial", "evidence": ""},
                {"id": "PDPL-7", "name": "Breach Notification", "name_ar": "إشعار الاختراق", "status": "planned", "evidence": ""},
                {"id": "PDPL-8", "name": "DPO Appointment", "name_ar": "تعيين مسؤول حماية البيانات", "status": "planned", "evidence": ""},
            ],
            nca_ecc_controls=[
                {"id": "ECC-1", "name": "Asset Management", "name_ar": "إدارة الأصول", "status": "partial"},
                {"id": "ECC-2", "name": "Identity & Access", "name_ar": "الهوية والوصول", "status": "implemented"},
                {"id": "ECC-3", "name": "Data Protection", "name_ar": "حماية البيانات", "status": "implemented"},
                {"id": "ECC-4", "name": "Network Security", "name_ar": "أمن الشبكات", "status": "partial"},
                {"id": "ECC-5", "name": "Incident Management", "name_ar": "إدارة الحوادث", "status": "planned"},
                {"id": "ECC-6", "name": "Business Continuity", "name_ar": "استمرارية الأعمال", "status": "planned"},
            ],
            ai_governance_controls=[
                {"id": "NIST-AI-1", "name": "AI Risk Assessment", "name_ar": "تقييم مخاطر الذكاء الاصطناعي", "status": "partial", "framework": "NIST AI RMF 1.0"},
                {"id": "NIST-AI-2", "name": "Model Transparency", "name_ar": "شفافية النموذج", "status": "implemented", "framework": "NIST AI RMF 1.0"},
                {"id": "OWASP-LLM-1", "name": "Prompt Injection Prevention", "name_ar": "منع حقن الأوامر", "status": "partial", "framework": "OWASP Top 10 LLM"},
                {"id": "OWASP-LLM-2", "name": "Output Validation", "name_ar": "التحقق من المخرجات", "status": "implemented", "framework": "OWASP Top 10 LLM"},
                {"id": "OWASP-LLM-3", "name": "Training Data Poisoning", "name_ar": "تسميم بيانات التدريب", "status": "planned", "framework": "OWASP Top 10 LLM"},
            ],
        )


class ReleaseGovernance:
    """Manages release lifecycle with gates and compliance checks."""
    
    DEFAULT_GATES = [
        ReleaseGate(name="Unit Tests", gate_type="test_pass"),
        ReleaseGate(name="Integration Tests", gate_type="test_pass"),
        ReleaseGate(name="Security Scan", gate_type="security_scan"),
        ReleaseGate(name="Code Review", gate_type="code_review"),
        ReleaseGate(name="PDPL Compliance Check", gate_type="compliance_check"),
        ReleaseGate(name="Smoke Test (AR+EN)", gate_type="smoke_test"),
    ]
    
    def __init__(self):
        self._releases: dict[str, ReleaseRecord] = {}
    
    def create_release(self, version: str, environment: EnvironmentType, commit_sha: str = "") -> ReleaseRecord:
        release = ReleaseRecord(
            version=version,
            environment=environment,
            commit_sha=commit_sha,
            gates=[g.model_copy() for g in self.DEFAULT_GATES],
        )
        if environment == EnvironmentType.PRODUCTION:
            release.gates.append(ReleaseGate(name="Canary Deployment", gate_type="deployment_protection"))
            release.canary_percentage = 10
        self._releases[release.release_id] = release
        return release
    
    def pass_gate(self, release_id: str, gate_id: str, checked_by: str) -> ReleaseRecord:
        release = self._releases.get(release_id)
        if not release:
            raise ValueError(f"Release {release_id} not found")
        for gate in release.gates:
            if gate.gate_id == gate_id:
                gate.passed = True
                gate.checked_at = datetime.now(timezone.utc)
                gate.checked_by = checked_by
                break
        if all(g.passed for g in release.gates if g.required):
            release.status = ReleaseStatus.APPROVED
        else:
            release.status = ReleaseStatus.PENDING_REVIEW
        return release
    
    def get_release(self, release_id: str) -> ReleaseRecord | None:
        return self._releases.get(release_id)
    
    def list_releases(self) -> list[ReleaseRecord]:
        return list(self._releases.values())


release_governance = ReleaseGovernance()
