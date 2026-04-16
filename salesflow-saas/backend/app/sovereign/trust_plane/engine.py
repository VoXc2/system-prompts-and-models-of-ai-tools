"""Trust Plane — authorization, policy, audit, and AI governance."""

from __future__ import annotations

import logging
import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.sovereign.schemas import ContradictionRecord

logger = logging.getLogger("dealix.sovereign.trust_plane")


class PolicyVerdict(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


class PolicyDecision(BaseModel):
    """Outcome of policy evaluation."""

    verdict: PolicyVerdict
    reasons_en: list[str] = Field(default_factory=list)
    reasons_ar: list[str] = Field(default_factory=list)
    policy_version: str = "stub-v0"


class AuthorizationResult(BaseModel):
    """Authorization check result."""

    allowed: bool
    roles_matched: list[str] = Field(default_factory=list)
    explanation_en: str
    explanation_ar: str


class RoutedApproval(BaseModel):
    """Approval request routed to a reviewer."""

    request_id: str
    approval_class: str
    assigned_reviewer_id: str
    route_reason_en: str
    route_reason_ar: str


class ToolVerificationResult(BaseModel):
    """Governed verification of an agent tool invocation."""

    approved: bool
    sanitized_parameters: dict[str, Any] = Field(default_factory=dict)
    warnings_en: list[str] = Field(default_factory=list)
    warnings_ar: list[str] = Field(default_factory=list)


class AuditEntryPayload(BaseModel):
    """Minimal audit entry accepted by the trust plane (caller-defined)."""

    action: str
    actor_id: str
    resource: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIGovernanceResult(BaseModel):
    """Model/task governance decision."""

    permitted: bool
    model_id: str
    task_type: str
    constraints_en: list[str] = Field(default_factory=list)
    constraints_ar: list[str] = Field(default_factory=list)


class SecretsGovernanceResult(BaseModel):
    """Secret reference governance check."""

    secret_ref: str
    allowed: bool
    rotation_due: bool = False
    detail_en: str
    detail_ar: str


class TrustPlaneEngine:
    """Async stubs for policy, authZ, approvals, and AI governance."""

    async def evaluate_policy(
        self,
        tenant_id: str,
        action: str,
        context: dict[str, Any],
    ) -> PolicyDecision:
        logger.info(
            "trust_plane.evaluate_policy tenant_id=%s action=%s",
            tenant_id,
            action,
        )
        _ = context
        return PolicyDecision(
            verdict=PolicyVerdict.ALLOW,
            reasons_en=["Stub policy: no violations detected in context keys."],
            reasons_ar=["سياسة تجريبية: لا مخالفات في مفاتيح السياق."],
        )

    async def check_authorization(
        self,
        tenant_id: str,
        user_id: str,
        resource: str,
        action: str,
    ) -> AuthorizationResult:
        logger.info(
            "trust_plane.check_authorization tenant_id=%s user_id=%s resource=%s action=%s",
            tenant_id,
            user_id,
            resource,
            action,
        )
        return AuthorizationResult(
            allowed=True,
            roles_matched=["tenant_member"],
            explanation_en="Stub: user may perform action on resource within tenant.",
            explanation_ar="وضع تجريبي: المستخدم مخوّل داخل نطاق المستأجر.",
        )

    async def route_approval(
        self,
        tenant_id: str,
        request: dict[str, Any],
        approval_class: str,
    ) -> RoutedApproval:
        logger.info(
            "trust_plane.route_approval tenant_id=%s approval_class=%s",
            tenant_id,
            approval_class,
        )
        rid = str(request.get("id", uuid.uuid4()))
        return RoutedApproval(
            request_id=str(rid),
            approval_class=approval_class,
            assigned_reviewer_id=str(request.get("default_reviewer", "reviewer_stub")),
            route_reason_en=f"Routed to sovereign reviewer for class {approval_class}.",
            route_reason_ar=f"توجيه إلى مراجع سيادي لفئة الموافقة {approval_class}.",
        )

    async def verify_tool_call(
        self,
        tenant_id: str,
        agent_id: str,
        tool_name: str,
        parameters: dict[str, Any],
    ) -> ToolVerificationResult:
        logger.info(
            "trust_plane.verify_tool_call tenant_id=%s agent_id=%s tool=%s",
            tenant_id,
            agent_id,
            tool_name,
        )
        return ToolVerificationResult(
            approved=True,
            sanitized_parameters=dict(parameters),
            warnings_en=["Stub: enforce allowlists before production."],
            warnings_ar=["تنبيه تجريبي: طبّق قوائم السماح قبل الإنتاج."],
        )

    async def log_audit_entry(self, tenant_id: str, entry: AuditEntryPayload) -> None:
        logger.info(
            "trust_plane.log_audit_entry tenant_id=%s action=%s actor=%s",
            tenant_id,
            entry.action,
            entry.actor_id,
        )

    async def detect_contradiction(
        self,
        tenant_id: str,
        intended: dict[str, Any],
        claimed: dict[str, Any],
        actual: dict[str, Any],
    ) -> ContradictionRecord:
        logger.info("trust_plane.detect_contradiction tenant_id=%s", tenant_id)
        mismatch = set(claimed.keys()) ^ set(actual.keys())
        return ContradictionRecord(
            agent_id=str(intended.get("agent_id", "unknown")),
            intended_action=str(intended.get("action", "unknown")),
            claimed_action=str(claimed.get("action", "unknown")),
            actual_tool_call=str(actual.get("tool", "unknown")),
            side_effects=[f"key_diff={list(mismatch)}"] if mismatch else [],
            contradiction_detected=bool(mismatch),
        )

    async def evaluate_ai_governance(
        self,
        tenant_id: str,
        model_id: str,
        task_type: str,
    ) -> AIGovernanceResult:
        logger.info(
            "trust_plane.evaluate_ai_governance tenant_id=%s model=%s task=%s",
            tenant_id,
            model_id,
            task_type,
        )
        return AIGovernanceResult(
            permitted=True,
            model_id=model_id,
            task_type=task_type,
            constraints_en=["No PII in prompts", "Log tool receipts"],
            constraints_ar=["منع البيانات الشخصية في المطالبات", "تسجيل إيصالات الأدوات"],
        )

    async def check_secrets_governance(
        self,
        tenant_id: str,
        secret_ref: str,
    ) -> SecretsGovernanceResult:
        logger.info(
            "trust_plane.check_secrets_governance tenant_id=%s ref=%s",
            tenant_id,
            secret_ref,
        )
        return SecretsGovernanceResult(
            secret_ref=secret_ref,
            allowed=True,
            rotation_due=False,
            detail_en="Stub: secret reference format accepted.",
            detail_ar="وضع تجريبي: مرجع السر مقبول شكليًا.",
        )


class TrustPlane(TrustPlaneEngine):
    """Sovereign Trust Plane — public entry type."""

    pass
