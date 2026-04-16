"""
Trust Plane — Policy Engine.

Central evaluator that combines governance rules with actor identity
and resource context to produce a gate decision.

محرك السياسات — تقييم الإجراءات وفقًا لسياسات الحوكمة والامتثال
"""
from __future__ import annotations

from app.planes.trust.approval_classes import (
    ACTION_POLICY_MAP,
    ApprovalClass,
    PolicyGateResult,
    ReversibilityClass,
    SensitivityClass,
)


class PolicyEngine:
    """Stateless policy evaluator for the Trust Plane."""

    # Roles that receive automatic approval regardless of action class.
    _PRIVILEGED_ROLES: set[str] = {"admin", "ceo"}

    def evaluate(
        self,
        action: str,
        actor: dict,
        resource: dict,
        context: dict | None = None,
    ) -> PolicyGateResult:
        """Evaluate whether *actor* may perform *action* on *resource*."""
        default = (
            ApprovalClass.R2_APPROVE,
            ReversibilityClass.PARTIALLY_REVERSIBLE,
            SensitivityClass.CONFIDENTIAL,
        )
        approval, reversibility, sensitivity = ACTION_POLICY_MAP.get(action, default)

        allowed = approval == ApprovalClass.R0_AUTO
        metadata: dict = {"resource": resource}

        actor_role = actor.get("role", "")
        if actor_role in self._PRIVILEGED_ROLES:
            allowed = True
            metadata["auto_approved_by_role"] = actor_role

        if context and context.get("override_reason"):
            metadata["override_reason"] = context["override_reason"]

        return PolicyGateResult(
            allowed=allowed,
            approval_class=approval,
            reversibility=reversibility,
            sensitivity=sensitivity,
            metadata=metadata,
        )

    # ── Saudi regulatory helpers ─────────────────────────────────

    def check_pdpl_compliance(
        self,
        data_type: str,
        processing_purpose: str,
        has_consent: bool,
    ) -> dict:
        """Check alignment with Saudi Personal Data Protection Law (PDPL / نظام حماية البيانات الشخصية).

        Returns a dict with *compliant*, *violations*, and *recommendations*.
        """
        violations: list[str] = []
        recommendations: list[str] = []

        if not has_consent:
            violations.append(
                "معالجة بدون موافقة — Processing without data-subject consent"
            )

        sensitive_types = {"health", "financial", "biometric", "religious", "political"}
        if data_type.lower() in sensitive_types:
            recommendations.append(
                "بيانات حساسة — تتطلب موافقة صريحة ومعالجة مشددة — "
                "Sensitive data requires explicit consent and enhanced safeguards"
            )
            if not has_consent:
                violations.append(
                    "بيانات حساسة بدون موافقة صريحة — "
                    "Sensitive data processed without explicit consent"
                )

        valid_purposes = {
            "service_delivery",
            "legal_obligation",
            "vital_interest",
            "public_interest",
            "legitimate_interest",
        }
        if processing_purpose not in valid_purposes:
            recommendations.append(
                f"غرض المعالجة '{processing_purpose}' غير معياري — "
                f"Processing purpose '{processing_purpose}' is non-standard"
            )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
        }

    def check_nca_compliance(
        self,
        data_classification: str,
        storage_location: str,
    ) -> dict:
        """Check alignment with NCA (الهيئة الوطنية للأمن السيبراني) Essential Cybersecurity Controls.

        Returns a dict with *compliant*, *violations*, and *recommendations*.
        """
        violations: list[str] = []
        recommendations: list[str] = []

        restricted_classifications = {"restricted", "top_secret"}
        if data_classification.lower() in restricted_classifications:
            if storage_location.lower() not in ("sa", "saudi_arabia", "ksa"):
                violations.append(
                    "بيانات مقيدة مخزنة خارج المملكة — "
                    "Restricted data stored outside Saudi Arabia"
                )
            recommendations.append(
                "بيانات مقيدة — تتطلب تشفير وتحكم وصول مشدد — "
                "Restricted data requires encryption and strict access controls"
            )

        if data_classification.lower() == "confidential":
            recommendations.append(
                "بيانات سرية — يُنصح بالتخزين داخل المملكة — "
                "Confidential data — in-Kingdom storage recommended"
            )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
        }
