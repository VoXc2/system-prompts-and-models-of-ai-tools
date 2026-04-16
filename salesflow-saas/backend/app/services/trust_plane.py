"""
Trust Plane Service — Dealix Sovereign OS

Provides:
  1. OPA-style policy evaluation (policy_engine)
  2. OpenFGA-style relationship-based authorization (fine-grained authz)
  3. Policy violation recording
  4. Evidence-native action gates

Architecture note:
  - Full OPA integration: deploy OPA sidecar, send decisions via HTTP to
    http://opa:8181/v1/data/<policy_path>
  - Full OpenFGA integration: connect to OpenFGA server, send check() calls
    with authorization_model_id pinned per environment
  - This service provides the interface + fallback logic that works without
    those external services running (dev/test mode)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sovereign import PolicyViolation
from app.config import get_settings

logger = logging.getLogger("dealix.trust_plane")
settings = get_settings()


# ─── Policy Engine (OPA facade) ───────────────────────────────────

class PolicyEngine:
    """
    OPA-compatible policy evaluation.
    In production: forward to OPA sidecar at OPA_URL.
    In dev: applies built-in rule set.
    """

    OPA_URL = getattr(settings, "OPA_URL", None) or "http://opa:8181"

    BUILTIN_RULES: dict[str, set[str]] = {
        # role → allowed approval classes
        "admin":         {"A", "B"},
        "founder":       {"A", "B"},
        "sales":         {"A"},
        "partner_mgr":   {"A"},
        "corp_dev":      {"A", "B"},
        "board":         {"A", "B"},
        "compliance":    {"A"},
        "readonly":      set(),
    }

    async def evaluate(
        self,
        policy_path: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate a policy.
        Returns {"allow": bool, "reason": str, ...}
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(
                    f"{self.OPA_URL}/v1/data/{policy_path}",
                    json={"input": input_data},
                )
                if resp.status_code == 200:
                    return resp.json().get("result", {"allow": False})
        except Exception:
            pass
        # Fallback: built-in rules
        return self._builtin_evaluate(input_data)

    def _builtin_evaluate(self, input_data: dict) -> dict[str, Any]:
        role = input_data.get("role", "readonly")
        approval_class = input_data.get("approval_class", "B")
        allowed_classes = self.BUILTIN_RULES.get(role, set())
        allow = approval_class in allowed_classes
        return {
            "allow": allow,
            "reason": f"Built-in: role={role} approval_class={approval_class}",
            "source": "builtin_fallback",
        }

    async def is_action_allowed(
        self,
        role: str,
        approval_class: str,
        action: str,
    ) -> bool:
        result = await self.evaluate(
            "dealix/actions/allow",
            {"role": role, "approval_class": approval_class, "action": action},
        )
        return bool(result.get("allow", False))


# ─── Fine-grained Authorization (OpenFGA facade) ─────────────────

class AuthorizationEngine:
    """
    OpenFGA-compatible relationship-based authorization.
    In production: connect to OpenFGA server at OPENFGA_URL with
    authorization_model_id pinned (models are immutable in OpenFGA).
    In dev: applies simplified RBAC.
    """

    OPENFGA_URL = getattr(settings, "OPENFGA_URL", None) or "http://openfga:8080"
    AUTH_MODEL_ID = getattr(settings, "OPENFGA_MODEL_ID", None) or ""

    # Simplified relation map for dev fallback
    # {relation: [roles_that_have_it]}
    RELATION_ROLE_MAP: dict[str, list[str]] = {
        "viewer":           ["readonly", "sales", "partner_mgr", "corp_dev", "compliance", "admin", "founder", "board"],
        "editor":           ["sales", "partner_mgr", "corp_dev", "admin", "founder"],
        "approver":         ["admin", "founder", "board", "corp_dev"],
        "dd_room_access":   ["corp_dev", "admin", "founder"],
        "board_pack_viewer": ["board", "admin", "founder"],
        "evidence_approver": ["admin", "founder", "board"],
        "policy_reviewer":  ["compliance", "admin", "founder"],
    }

    async def check(
        self,
        user: str,
        relation: str,
        object_type: str,
        object_id: str,
        role: str = "readonly",
    ) -> bool:
        """
        Check if user has relation to object.
        e.g. check(user="user:alice", relation="dd_room_access", object_type="ma_target", object_id="...")
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                body: dict[str, Any] = {
                    "tuple_key": {
                        "user": user,
                        "relation": relation,
                        "object": f"{object_type}:{object_id}",
                    }
                }
                if self.AUTH_MODEL_ID:
                    body["authorization_model_id"] = self.AUTH_MODEL_ID
                resp = await client.post(
                    f"{self.OPENFGA_URL}/stores/{object_type}/check",
                    json=body,
                )
                if resp.status_code == 200:
                    return resp.json().get("allowed", False)
        except Exception:
            pass
        # Dev fallback
        allowed_roles = self.RELATION_ROLE_MAP.get(relation, [])
        return role in allowed_roles


# ─── Trust Plane Orchestrator ─────────────────────────────────────

class TrustPlaneService:
    """
    Main trust plane coordinator.
    Combines policy evaluation + authorization + violation recording.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.policy = PolicyEngine()
        self.authz = AuthorizationEngine()

    async def gate_action(
        self,
        tenant_id: str,
        user_id: str,
        role: str,
        action: str,
        approval_class: str,
        resource_type: str = "",
        resource_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Gate an action through both OPA policy check and OpenFGA authz check.
        Returns {"allowed": bool, "reason": str, "violation_id": str|None}
        """
        policy_result = await self.policy.evaluate(
            "dealix/actions/allow",
            {
                "user_id": user_id,
                "role": role,
                "action": action,
                "approval_class": approval_class,
                "resource_type": resource_type,
            },
        )

        authz_allowed = await self.authz.check(
            user=f"user:{user_id}",
            relation="editor" if approval_class == "A" else "approver",
            object_type=resource_type or "platform",
            object_id=resource_id or "global",
            role=role,
        )

        allowed = policy_result.get("allow", False) and authz_allowed
        violation_id = None

        if not allowed:
            violation = PolicyViolation(
                tenant_id=tenant_id,
                violation_type="unauthorized_action",
                severity="high" if approval_class == "C" else "medium",
                resource_type=resource_type,
                resource_id=resource_id,
                triggered_by_id=user_id,
                policy_ref=f"dealix/actions/{action}",
                description_ar=f"تم رفض الإجراء: {action} للمستخدم {user_id}",
                description_en=f"Action denied: {action} for user {user_id}",
                remediation_ar="تحقق من صلاحياتك أو اطلب الاعتماد من المدير",
            )
            self.db.add(violation)
            await self.db.commit()
            await self.db.refresh(violation)
            violation_id = str(violation.id)

        return {
            "allowed": allowed,
            "reason": policy_result.get("reason", ""),
            "violation_id": violation_id,
        }

    async def record_violation(
        self,
        tenant_id: str,
        violation_type: str,
        severity: str,
        description_ar: str,
        resource_type: str = "",
        resource_id: str | None = None,
        triggered_by_id: str | None = None,
        policy_ref: str = "",
        remediation_ar: str = "",
    ) -> str:
        violation = PolicyViolation(
            tenant_id=tenant_id,
            violation_type=violation_type,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            triggered_by_id=triggered_by_id,
            policy_ref=policy_ref,
            description_ar=description_ar,
            remediation_ar=remediation_ar,
        )
        self.db.add(violation)
        await self.db.commit()
        await self.db.refresh(violation)
        return str(violation.id)

    async def list_violations(
        self,
        tenant_id: str,
        resolved: bool = False,
        severity: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = select(PolicyViolation).where(
            PolicyViolation.tenant_id == tenant_id,
            PolicyViolation.resolved.is_(resolved),
        )
        if severity:
            query = query.where(PolicyViolation.severity == severity)
        query = query.order_by(PolicyViolation.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        rows = result.scalars().all()
        return [
            {
                "id": str(r.id),
                "violation_type": r.violation_type,
                "severity": r.severity,
                "description_ar": r.description_ar,
                "policy_ref": r.policy_ref,
                "resource_type": r.resource_type,
                "resolved": r.resolved,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    async def resolve_violation(
        self,
        tenant_id: str,
        violation_id: str,
        resolver_id: str,
    ) -> dict[str, Any]:
        result = await self.db.execute(
            select(PolicyViolation).where(
                PolicyViolation.id == violation_id,
                PolicyViolation.tenant_id == tenant_id,
            )
        )
        v = result.scalar_one_or_none()
        if not v:
            raise ValueError("Violation not found")
        v.resolved = True
        v.resolved_at = datetime.now(timezone.utc)
        v.resolved_by_id = resolver_id
        await self.db.commit()
        return {"id": violation_id, "resolved": True}
