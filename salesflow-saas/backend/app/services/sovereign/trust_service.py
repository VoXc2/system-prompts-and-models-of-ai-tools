"""Sovereign Trust Plane — Policy rules, evaluations, tool verification, compliance."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class TrustService:
    """Manages policy rules, evaluations, tool verification, and compliance mappings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Policy Rules ───────────────────────────────

    async def create_policy_rule(
        self, tenant_id: str, data: dict,
    ) -> "PolicyRule":
        from app.models.sovereign_trust import PolicyRule

        rule = PolicyRule(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            rule_code=data["rule_code"],
            rule_name=data["rule_name"],
            rule_name_ar=data.get("rule_name_ar"),
            description=data.get("description"),
            description_ar=data.get("description_ar"),
            policy_category=data["policy_category"],
            rule_definition=data["rule_definition"],
            severity=data.get("severity", "info"),
            is_active=data.get("is_active", True),
            applies_to_roles=data.get("applies_to_roles"),
            applies_to_entities=data.get("applies_to_entities"),
        )
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def list_policy_rules(
        self,
        tenant_id: str,
        category: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_trust import PolicyRule

        query = select(PolicyRule).where(
            PolicyRule.tenant_id == uuid.UUID(tenant_id),
        )
        if category:
            query = query.where(PolicyRule.policy_category == category)

        query = query.order_by(PolicyRule.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ── Policy Evaluation ──────────────────────────

    async def evaluate_policy(
        self,
        tenant_id: str,
        rule_id: str,
        action_type: str,
        actor_id: str,
        context: Optional[dict] = None,
    ) -> "PolicyEvaluation":
        from app.models.sovereign_trust import PolicyRule, PolicyEvaluation

        tid = uuid.UUID(tenant_id)

        rule_result = await self.db.execute(
            select(PolicyRule).where(
                PolicyRule.id == uuid.UUID(rule_id),
                PolicyRule.tenant_id == tid,
            )
        )
        rule = rule_result.scalar_one_or_none()

        if not rule or not rule.is_active:
            evaluation_result = "denied"
            violation_details = "Rule not found or inactive"
        else:
            rule_def = rule.rule_definition or {}
            allowed_actions = rule_def.get("allowed_actions", [])
            blocked_actions = rule_def.get("blocked_actions", [])
            allowed_roles = rule.applies_to_roles or []

            if action_type in blocked_actions:
                evaluation_result = "denied"
                violation_details = f"Action '{action_type}' is explicitly blocked by rule {rule.rule_code}"
            elif allowed_actions and action_type not in allowed_actions:
                evaluation_result = "denied"
                violation_details = f"Action '{action_type}' is not in the allowed list for rule {rule.rule_code}"
            else:
                evaluation_result = "allowed"
                violation_details = None

        evaluation = PolicyEvaluation(
            id=uuid.uuid4(),
            tenant_id=tid,
            rule_id=uuid.UUID(rule_id),
            action_type=action_type,
            actor_id=uuid.UUID(actor_id),
            target_entity_type=context.get("target_entity_type") if context else None,
            target_entity_id=uuid.UUID(context["target_entity_id"]) if context and context.get("target_entity_id") else None,
            evaluation_result=evaluation_result,
            input_context=context,
            violation_details=violation_details,
        )
        self.db.add(evaluation)
        await self.db.flush()
        return evaluation

    async def list_policy_violations(self, tenant_id: str) -> list:
        from app.models.sovereign_trust import PolicyEvaluation

        query = (
            select(PolicyEvaluation)
            .where(
                PolicyEvaluation.tenant_id == uuid.UUID(tenant_id),
                PolicyEvaluation.evaluation_result == "denied",
            )
            .order_by(PolicyEvaluation.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ── Tool Verification ──────────────────────────

    async def log_tool_verification(
        self, tenant_id: str, data: dict,
    ) -> "ToolVerification":
        from app.models.sovereign_trust import ToolVerification

        verification = ToolVerification(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            tool_name=data["tool_name"],
            tool_version=data.get("tool_version"),
            invocation_id=data.get("invocation_id", str(uuid.uuid4())),
            invoked_by=data["invoked_by"],
            input_hash=data.get("input_hash"),
            output_hash=data.get("output_hash"),
            execution_time_ms=data.get("execution_time_ms"),
            success=data["success"],
            error_message=data.get("error_message"),
            side_effects=data.get("side_effects"),
            audit_trail=data.get("audit_trail"),
        )
        self.db.add(verification)
        await self.db.flush()
        return verification

    async def list_tool_verifications(
        self,
        tenant_id: str,
        tool_name: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_trust import ToolVerification

        query = select(ToolVerification).where(
            ToolVerification.tenant_id == uuid.UUID(tenant_id),
        )
        if tool_name:
            query = query.where(ToolVerification.tool_name == tool_name)

        query = query.order_by(ToolVerification.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ── Compliance Mappings ────────────────────────

    async def create_compliance_mapping(
        self, tenant_id: str, data: dict,
    ) -> "ComplianceMapping":
        from app.models.sovereign_trust import ComplianceMapping

        mapping = ComplianceMapping(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            framework=data["framework"],
            control_id=data["control_id"],
            control_name=data["control_name"],
            control_name_ar=data.get("control_name_ar"),
            description=data.get("description"),
            description_ar=data.get("description_ar"),
            status=data.get("status", "not_started"),
            evidence_refs=data.get("evidence_refs"),
            owner_id=uuid.UUID(data["owner_id"]) if data.get("owner_id") else None,
            last_assessed_at=data.get("last_assessed_at"),
            next_review_at=data.get("next_review_at"),
            risk_level=data.get("risk_level", "medium"),
        )
        self.db.add(mapping)
        await self.db.flush()
        return mapping

    async def list_compliance_mappings(
        self,
        tenant_id: str,
        framework: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_trust import ComplianceMapping

        query = select(ComplianceMapping).where(
            ComplianceMapping.tenant_id == uuid.UUID(tenant_id),
        )
        if framework:
            query = query.where(ComplianceMapping.framework == framework)

        query = query.order_by(ComplianceMapping.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ── Saudi Compliance Matrix ────────────────────

    async def get_compliance_matrix(self, tenant_id: str) -> dict:
        from app.models.sovereign_trust import ComplianceMapping, PolicyEvaluation, ToolVerification

        tid = uuid.UUID(tenant_id)

        mappings_result = await self.db.execute(
            select(ComplianceMapping).where(ComplianceMapping.tenant_id == tid)
        )
        mappings = mappings_result.scalars().all()

        frameworks: dict = {}
        for m in mappings:
            fw = m.framework
            if fw not in frameworks:
                frameworks[fw] = {"total": 0, "by_status": {}, "by_risk": {}}
            frameworks[fw]["total"] += 1
            frameworks[fw]["by_status"][m.status] = frameworks[fw]["by_status"].get(m.status, 0) + 1
            frameworks[fw]["by_risk"][m.risk_level] = frameworks[fw]["by_risk"].get(m.risk_level, 0) + 1

        total_evaluations = (await self.db.execute(
            select(func.count()).where(PolicyEvaluation.tenant_id == tid)
        )).scalar() or 0

        total_violations = (await self.db.execute(
            select(func.count()).where(
                PolicyEvaluation.tenant_id == tid,
                PolicyEvaluation.evaluation_result == "denied",
            )
        )).scalar() or 0

        total_verifications = (await self.db.execute(
            select(func.count()).where(ToolVerification.tenant_id == tid)
        )).scalar() or 0

        failed_verifications = (await self.db.execute(
            select(func.count()).where(
                ToolVerification.tenant_id == tid,
                ToolVerification.success == False,  # noqa: E712
            )
        )).scalar() or 0

        return {
            "frameworks": frameworks,
            "total_controls": sum(f["total"] for f in frameworks.values()),
            "total_evaluations": total_evaluations,
            "total_violations": total_violations,
            "total_verifications": total_verifications,
            "failed_verifications": failed_verifications,
        }
