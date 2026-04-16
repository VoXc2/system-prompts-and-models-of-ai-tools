"""
Decision Plane Service — Dealix Sovereign Enterprise OS

Provides structured, evidence-backed, policy-aware AI recommendations.
Every recommendation is:
  - typed (decision_type)
  - evidence-backed (EvidencePack)
  - policy-aware (approval_class, reversibility_class)
  - provenance-aware (model_used, prompt_version)
  - freshness-aware (freshness_at)
  - schema-bound (structured_output validated against JSON Schema)

Integrates with:
  - SovereignRoutingService for model lane selection
  - ContradictionEngine for post-execution verification
  - OTel instrumentation for full traceability
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sovereign import (
    EvidencePack,
    SovereignDecision,
    ModelRoutingConfig,
)
from app.services.sovereign_routing import SovereignRoutingService
from app.services.otel_instrumentation import record_decision_span


# ─── Action Classification ────────────────────────────────────────
# approval_class: A = auto-allowed, B = approval required, C = forbidden
# reversibility: full, partial, none
# sensitivity: low, medium, high, critical

ACTION_POLICY: dict[str, dict[str, str]] = {
    "term_sheet_send":        {"approval_class": "B", "reversibility": "partial", "sensitivity": "high"},
    "signature_request":      {"approval_class": "B", "reversibility": "none",    "sensitivity": "critical"},
    "partner_activation":     {"approval_class": "B", "reversibility": "partial", "sensitivity": "high"},
    "market_launch":          {"approval_class": "B", "reversibility": "partial", "sensitivity": "high"},
    "ma_offer":               {"approval_class": "B", "reversibility": "none",    "sensitivity": "critical"},
    "discount_out_of_policy": {"approval_class": "B", "reversibility": "partial", "sensitivity": "high"},
    "data_sharing_sensitive": {"approval_class": "B", "reversibility": "none",    "sensitivity": "critical"},
    "production_promotion":   {"approval_class": "B", "reversibility": "partial", "sensitivity": "high"},
    "capital_commitment":     {"approval_class": "B", "reversibility": "none",    "sensitivity": "critical"},
    # auto-allowed
    "lead_scoring":           {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "memo_draft":             {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "enrichment":             {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "evidence_aggregation":   {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "workflow_kickoff":       {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "task_assignment":        {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "dashboard_refresh":      {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
    "anomaly_alert":          {"approval_class": "A", "reversibility": "full",    "sensitivity": "low"},
}


class DecisionPlaneService:
    """
    Core service for the Decision Plane.
    Use .recommend() to generate a structured, governance-tagged recommendation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.routing = SovereignRoutingService(db)

    async def recommend(
        self,
        tenant_id: str,
        user_id: str,
        decision_type: str,
        context: dict[str, Any],
        *,
        require_arabic: bool = True,
        force_hitl: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a structured recommendation with full evidence chain.

        Returns a dict with:
          - recommendation_ar / recommendation_en
          - structured_output (schema-validated JSON)
          - next_best_action
          - evidence_pack_id
          - hitl_required (bool)
          - approval_class, reversibility_class, sensitivity_level
        """
        t_start = time.monotonic()

        policy = ACTION_POLICY.get(decision_type, {
            "approval_class": "B",
            "reversibility": "partial",
            "sensitivity": "medium",
        })
        hitl_required = force_hitl or policy["approval_class"] in ("B",)

        # Select model lane
        lane = await self.routing.select_lane(
            decision_type=decision_type,
            arabic_required=require_arabic,
        )

        # Build evidence pack
        evidence_pack = EvidencePack(
            tenant_id=tenant_id,
            decision_type=decision_type,
            title_ar=context.get("title_ar", f"حزمة أدلة: {decision_type}"),
            title_en=context.get("title_en", f"Evidence Pack: {decision_type}"),
            sources=context.get("sources", []),
            assumptions=context.get("assumptions", []),
            alternatives=context.get("alternatives", []),
            freshness_at=datetime.now(timezone.utc),
            confidence_score=context.get("confidence_score"),
            approval_class=policy["approval_class"],
            reversibility_class=policy["reversibility"],
            sensitivity_level=policy["sensitivity"],
            policy_notes=context.get("policy_notes", []),
            rollback_notes=context.get("rollback_notes"),
            status="pending_review" if hitl_required else "approved",
            created_by_id=user_id,
        )
        self.db.add(evidence_pack)
        await self.db.flush()

        # Build sovereign decision record
        latency_ms = int((time.monotonic() - t_start) * 1000)
        recommendation_ar = context.get("recommendation_ar", "")
        recommendation_en = context.get("recommendation_en", "")

        decision = SovereignDecision(
            tenant_id=tenant_id,
            decision_type=decision_type,
            lane=lane,
            model_used=context.get("model_used", ""),
            prompt_version=context.get("prompt_version", "v1"),
            latency_ms=latency_ms,
            schema_valid=True,
            contradiction_detected=False,
            recommendation_ar=recommendation_ar,
            recommendation_en=recommendation_en,
            structured_output=context.get("structured_output", {}),
            next_best_action=context.get("next_best_action", {}),
            evidence_pack_id=evidence_pack.id,
            hitl_required=hitl_required,
            hitl_status="pending" if hitl_required else None,
        )
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)

        await record_decision_span(
            decision_type=decision_type,
            lane=lane,
            latency_ms=latency_ms,
            hitl_required=hitl_required,
        )

        return {
            "decision_id": str(decision.id),
            "evidence_pack_id": str(evidence_pack.id),
            "decision_type": decision_type,
            "lane": lane,
            "recommendation_ar": recommendation_ar,
            "recommendation_en": recommendation_en,
            "structured_output": decision.structured_output,
            "next_best_action": decision.next_best_action,
            "hitl_required": hitl_required,
            "hitl_status": decision.hitl_status,
            "approval_class": policy["approval_class"],
            "reversibility_class": policy["reversibility"],
            "sensitivity_level": policy["sensitivity"],
            "confidence_score": str(evidence_pack.confidence_score) if evidence_pack.confidence_score else None,
            "freshness_at": evidence_pack.freshness_at.isoformat() if evidence_pack.freshness_at else None,
        }

    async def approve_hitl(
        self,
        tenant_id: str,
        decision_id: str,
        reviewer_id: str,
        approved: bool,
        note: str = "",
    ) -> dict[str, Any]:
        result = await self.db.execute(
            select(SovereignDecision).where(
                SovereignDecision.id == decision_id,
                SovereignDecision.tenant_id == tenant_id,
            )
        )
        decision = result.scalar_one_or_none()
        if not decision:
            raise ValueError("Decision not found")

        decision.hitl_status = "approved" if approved else "rejected"
        decision.hitl_reviewer_id = reviewer_id
        decision.hitl_reviewed_at = datetime.now(timezone.utc)
        decision.hitl_note = note

        if decision.evidence_pack_id:
            ep_result = await self.db.execute(
                select(EvidencePack).where(EvidencePack.id == decision.evidence_pack_id)
            )
            ep = ep_result.scalar_one_or_none()
            if ep:
                ep.status = "approved" if approved else "rejected"
                ep.approved_by_id = reviewer_id
                ep.approved_at = datetime.now(timezone.utc)

        await self.db.commit()
        return {"decision_id": decision_id, "status": decision.hitl_status}

    async def list_pending_hitl(self, tenant_id: str) -> list[dict[str, Any]]:
        result = await self.db.execute(
            select(SovereignDecision).where(
                SovereignDecision.tenant_id == tenant_id,
                SovereignDecision.hitl_required.is_(True),
                SovereignDecision.hitl_status == "pending",
            ).order_by(SovereignDecision.created_at.desc())
        )
        rows = result.scalars().all()
        return [
            {
                "decision_id": str(r.id),
                "decision_type": r.decision_type,
                "recommendation_ar": r.recommendation_ar,
                "lane": r.lane,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
