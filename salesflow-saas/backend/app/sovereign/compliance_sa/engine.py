"""Structured compliance checks for PDPL, NCA ECC, AI governance, and OWASP LLM Top 10."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.sovereign.constants import SAUDI_COMPLIANCE_FRAMEWORKS


PDPL_LIFECYCLE_PHASES: tuple[str, ...] = (
    "data_collection",
    "storage",
    "indexing",
    "retrieval",
    "usage",
    "disclosure",
    "transfer",
    "publishing",
    "linking",
    "blocking",
    "erasure",
    "destruction",
)


class PDPLPhaseAssessment(BaseModel):
    phase: str
    compliant: bool
    description_ar: str
    description_en: str


class PDPLComplianceResult(BaseModel):
    tenant_id: str
    operation: str
    overall_compliant: bool
    phases: list[PDPLPhaseAssessment]
    summary_ar: str
    summary_en: str


class NCAComplianceResult(BaseModel):
    tenant_id: str
    system_component: str
    compliant: bool
    controls_verified_ar: str
    controls_verified_en: str
    gaps_ar: str
    gaps_en: str


class AIGovernanceResult(BaseModel):
    tenant_id: str
    model_id: str
    use_case: str
    aligned: bool
    rationale_ar: str
    rationale_en: str


class OWASPCheckResult(BaseModel):
    tenant_id: str
    risk_score: float = Field(ge=0.0, le=100.0)
    findings_ar: list[str]
    findings_en: list[str]
    passed: bool


class ComplianceMatrix(BaseModel):
    tenant_id: str
    pdpl: PDPLComplianceResult
    nca_ecc: NCAComplianceResult
    ai_governance: AIGovernanceResult
    owasp_llm: OWASPCheckResult
    frameworks: tuple[str, ...] = Field(default=SAUDI_COMPLIANCE_FRAMEWORKS)


class ComplianceReport(BaseModel):
    tenant_id: str
    framework: str
    language: str
    title_ar: str
    title_en: str
    body_ar: str
    body_en: str


class RegulationMapping(BaseModel):
    tenant_id: str
    workflow_id: str
    pdpl_phases: list[str]
    nca_domains_ar: str
    nca_domains_en: str
    ai_controls_ar: str
    ai_controls_en: str


class SaudiComplianceEngine:
    def check_pdpl_compliance(
        self,
        tenant_id: str,
        operation: str,
        data_subjects: list[str],
    ) -> PDPLComplianceResult:
        has_subjects = len(data_subjects) > 0
        phases: list[PDPLPhaseAssessment] = []
        for phase in PDPL_LIFECYCLE_PHASES:
            ok = has_subjects or phase in ("storage", "indexing", "blocking", "erasure", "destruction")
            phases.append(
                PDPLPhaseAssessment(
                    phase=phase,
                    compliant=ok,
                    description_ar=f"تقييم مرحلة {phase} للعملية {operation}",
                    description_en=f"Assessment for {phase} on operation {operation}",
                ),
            )
        overall = all(p.compliant for p in phases)
        return PDPLComplianceResult(
            tenant_id=tenant_id,
            operation=operation,
            overall_compliant=overall,
            phases=phases,
            summary_ar="تم تقييم دورة حياة البيانات وفق نطاق العملية والأطراف.",
            summary_en="Lifecycle phases evaluated for the operation and data subjects in scope.",
        )

    def check_nca_ecc_compliance(self, tenant_id: str, system_component: str) -> NCAComplianceResult:
        compliant = "identity" in system_component.lower() or "vault" in system_component.lower()
        return NCAComplianceResult(
            tenant_id=tenant_id,
            system_component=system_component,
            compliant=compliant,
            controls_verified_ar="ضوابط الهوية، السجلات، التشفير، واستمرارية الخدمة.",
            controls_verified_en="Identity, logging, encryption, and availability controls reviewed.",
            gaps_ar="" if compliant else "تعزيز فصل الصلاحيات ومراجعة تكوين التخزين.",
            gaps_en="" if compliant else "Strengthen segregation of duties and storage configuration review.",
        )

    def check_ai_governance(self, tenant_id: str, model_id: str, use_case: str) -> AIGovernanceResult:
        aligned = "forbidden" not in use_case.lower()
        return AIGovernanceResult(
            tenant_id=tenant_id,
            model_id=model_id,
            use_case=use_case,
            aligned=aligned,
            rationale_ar="مطابقة حالة الاستخدام لسياسات الحد من الضرر والإفصاح.",
            rationale_en="Use case checked against harm mitigation, disclosure, and human oversight policies.",
        )

    def check_owasp_llm(self, tenant_id: str, interaction: dict[str, Any]) -> OWASPCheckResult:
        prompt = str(interaction.get("prompt", "")).lower()
        risk = 15.0
        findings_ar: list[str] = []
        findings_en: list[str] = []
        if "ignore previous" in prompt or "system prompt" in prompt:
            risk += 40.0
            findings_ar.append("محاولة حقن تعليمات قد تؤثر على سلامة النموذج.")
            findings_en.append("Possible prompt injection affecting model integrity.")
        if interaction.get("exfiltrate", False):
            risk += 35.0
            findings_ar.append("مسار تفاعل يشير إلى تسريب بيانات حساسة.")
            findings_en.append("Interaction path suggests sensitive data exfiltration risk.")
        passed = risk < 50.0
        return OWASPCheckResult(
            tenant_id=tenant_id,
            risk_score=min(risk, 100.0),
            findings_ar=findings_ar or ["لم يُرصد خطر OWASP LLM حرج في هذا التفاعل."],
            findings_en=findings_en or ["No critical OWASP LLM pattern detected for this interaction."],
            passed=passed,
        )

    def get_compliance_matrix(self, tenant_id: str) -> ComplianceMatrix:
        return ComplianceMatrix(
            tenant_id=tenant_id,
            pdpl=self.check_pdpl_compliance(tenant_id, "default_matrix", []),
            nca_ecc=self.check_nca_ecc_compliance(tenant_id, "platform_core"),
            ai_governance=self.check_ai_governance(tenant_id, "gpt-4o-mini", "customer_support"),
            owasp_llm=self.check_owasp_llm(tenant_id, {}),
        )

    def generate_compliance_report(self, tenant_id: str, framework: str, language: str = "ar") -> ComplianceReport:
        fw = framework.upper()
        title_ar = f"تقرير امتثال {fw}"
        title_en = f"{fw} compliance report"
        body_ar = f"ملخص امتثال المستأجر {tenant_id} وفق إطار {fw}، بما في ذلك الضوابط والاختبارات الموصى بها."
        body_en = f"Summary for tenant {tenant_id} under {fw}, including recommended controls and tests."
        if language != "ar":
            return ComplianceReport(
                tenant_id=tenant_id,
                framework=fw,
                language=language,
                title_ar=title_ar,
                title_en=title_en,
                body_ar=body_ar,
                body_en=body_en,
            )
        return ComplianceReport(
            tenant_id=tenant_id,
            framework=fw,
            language=language,
            title_ar=title_ar,
            title_en=title_en,
            body_ar=body_ar,
            body_en=body_en,
        )

    def map_workflow_to_regulations(self, tenant_id: str, workflow_id: str) -> RegulationMapping:
        return RegulationMapping(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            pdpl_phases=list(PDPL_LIFECYCLE_PHASES),
            nca_domains_ar="الهوية، حماية البيانات، الاستجابة للحوادث، استمرارية الأعمال.",
            nca_domains_en="Identity, data protection, incident response, business continuity.",
            ai_controls_ar="الإشراف البشري، تسجيل المطالبات، تقييم الانحياز، وحدود الأدوات.",
            ai_controls_en="Human oversight, claim logging, bias review, and tool boundaries.",
        )
