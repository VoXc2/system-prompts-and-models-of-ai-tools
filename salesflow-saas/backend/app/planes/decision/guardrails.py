"""
Guardrail evaluation engine for the Decision Plane.

Every agent action passes through guardrails before execution.
Maps to Agents SDK tracing + guardrails pattern.
"""

from __future__ import annotations

from typing import Any
from .schemas import (
    ApprovalClass,
    GuardrailResult,
    ReversibilityClass,
    RiskLevel,
    SensitivityClass,
    StructuredDecision,
)


HITL_ACTIONS = frozenset({
    "send_term_sheet",
    "request_signature",
    "activate_strategic_partnership",
    "launch_market_entry",
    "approve_off_policy_discount",
    "send_acquisition_offer",
    "closing_approval",
    "high_sensitivity_data_sharing",
    "production_rollout",
    "external_capital_commitment",
})

AUTO_ALLOWED_ACTIONS = frozenset({
    "lead_capture",
    "enrichment",
    "scoring",
    "routing",
    "follow_up",
    "meeting_reminder",
    "memo_drafting",
    "evidence_pack_assembly",
    "dd_checklist_orchestration",
    "task_assignment",
    "sla_reminder",
    "dashboard_update",
    "telemetry",
    "quality_check",
    "document_extraction",
    "connector_sync",
    "variance_detection",
    "anomaly_alert",
})


def _check_pdpl_compliance(decision: StructuredDecision) -> GuardrailResult:
    """PDPL/NCA-aware control: block if personal data processed without consent metadata."""
    has_consent = decision.metadata.get("pdpl_consent_verified", False)
    involves_pii = decision.sensitivity in (SensitivityClass.CONFIDENTIAL, SensitivityClass.RESTRICTED)
    if involves_pii and not has_consent:
        return GuardrailResult(
            passed=False,
            rule_id="PDPL-001",
            rule_name="PDPL Consent Required",
            rule_name_ar="يتطلب موافقة PDPL",
            message="Action involves sensitive personal data but PDPL consent not verified",
            message_ar="الإجراء يتضمن بيانات شخصية حساسة لكن لم يتم التحقق من موافقة PDPL",
            severity=RiskLevel.CRITICAL,
            blocked=True,
        )
    return GuardrailResult(
        passed=True,
        rule_id="PDPL-001",
        rule_name="PDPL Consent Required",
        rule_name_ar="يتطلب موافقة PDPL",
        message="PDPL check passed",
        message_ar="تم اجتياز فحص PDPL",
    )


def _check_hitl_gate(decision: StructuredDecision) -> GuardrailResult:
    """Block irreversible/high-risk actions that require human approval."""
    if decision.action in HITL_ACTIONS and decision.required_approval == ApprovalClass.AUTO:
        return GuardrailResult(
            passed=False,
            rule_id="HITL-001",
            rule_name="Human-in-the-Loop Required",
            rule_name_ar="يتطلب موافقة بشرية",
            message=f"Action '{decision.action}' requires explicit human approval",
            message_ar=f"الإجراء '{decision.action}' يتطلب موافقة بشرية صريحة",
            severity=RiskLevel.HIGH,
            blocked=True,
        )
    return GuardrailResult(
        passed=True,
        rule_id="HITL-001",
        rule_name="Human-in-the-Loop Required",
        rule_name_ar="يتطلب موافقة بشرية",
        message="No HITL gate needed or approval already assigned",
        message_ar="لا حاجة لبوابة موافقة بشرية أو تم تعيين الموافقة مسبقاً",
    )


def _check_reversibility(decision: StructuredDecision) -> GuardrailResult:
    """Irreversible actions with high financial impact need escalated approval."""
    if (
        decision.reversibility == ReversibilityClass.IRREVERSIBLE
        and decision.financial_impact_sar
        and decision.financial_impact_sar > 100_000
        and decision.required_approval in (ApprovalClass.AUTO, ApprovalClass.MANAGER)
    ):
        return GuardrailResult(
            passed=False,
            rule_id="REV-001",
            rule_name="Irreversible High-Value Action",
            rule_name_ar="إجراء عالي القيمة غير قابل للعكس",
            message="Irreversible action >100K SAR requires Director+ approval",
            message_ar="إجراء غير قابل للعكس بقيمة تتجاوز 100 ألف ريال يتطلب موافقة مدير أو أعلى",
            severity=RiskLevel.HIGH,
            blocked=True,
        )
    return GuardrailResult(
        passed=True,
        rule_id="REV-001",
        rule_name="Irreversible High-Value Action",
        rule_name_ar="إجراء عالي القيمة غير قابل للعكس",
        message="Reversibility check passed",
        message_ar="تم اجتياز فحص قابلية العكس",
    )


def evaluate_guardrails(decision: StructuredDecision) -> list[GuardrailResult]:
    """Run all guardrails against a structured decision. Returns list of results."""
    checks = [
        _check_pdpl_compliance,
        _check_hitl_gate,
        _check_reversibility,
    ]
    return [check(decision) for check in checks]


def is_action_auto_allowed(action: str) -> bool:
    """Check if an action can proceed without any approval gate."""
    return action in AUTO_ALLOWED_ACTIONS


def get_required_approval_for_action(action: str) -> ApprovalClass:
    """Determine minimum approval class for a given action."""
    if action in AUTO_ALLOWED_ACTIONS:
        return ApprovalClass.AUTO
    if action in HITL_ACTIONS:
        return ApprovalClass.DIRECTOR
    return ApprovalClass.MANAGER
