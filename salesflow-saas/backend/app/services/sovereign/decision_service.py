"""Sovereign Decision Plane — AI recommendations, contradiction tracking, dashboard."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class DecisionService:
    """Manages AI recommendations and contradiction records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Recommendations ────────────────────────────

    async def create_recommendation(
        self, tenant_id: str, data: dict,
    ) -> "AIRecommendation":
        from app.models.sovereign_decision import AIRecommendation

        rec = AIRecommendation(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            recommendation_type=data["recommendation_type"],
            title=data["title"],
            title_ar=data.get("title_ar"),
            summary=data["summary"],
            summary_ar=data.get("summary_ar"),
            evidence_sources=data.get("evidence_sources", []),
            assumptions=data.get("assumptions", []),
            confidence_score=data["confidence_score"],
            freshness_at=data.get("freshness_at"),
            model_version=data["model_version"],
            model_lane=data["model_lane"],
            policy_notes=data.get("policy_notes"),
            alternatives=data.get("alternatives"),
            status=data.get("status", "draft"),
            target_entity_type=data["target_entity_type"],
            target_entity_id=uuid.UUID(data["target_entity_id"]) if data.get("target_entity_id") else None,
            provenance_chain=data.get("provenance_chain"),
        )
        self.db.add(rec)
        await self.db.flush()
        return rec

    async def list_recommendations(
        self,
        tenant_id: str,
        filters: Optional[dict] = None,
    ) -> list:
        from app.models.sovereign_decision import AIRecommendation

        query = select(AIRecommendation).where(
            AIRecommendation.tenant_id == uuid.UUID(tenant_id),
        )

        if filters:
            if filters.get("recommendation_type"):
                query = query.where(
                    AIRecommendation.recommendation_type == filters["recommendation_type"],
                )
            if filters.get("status"):
                query = query.where(AIRecommendation.status == filters["status"])
            if filters.get("target_entity_type"):
                query = query.where(
                    AIRecommendation.target_entity_type == filters["target_entity_type"],
                )

        query = query.order_by(AIRecommendation.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recommendation(
        self, tenant_id: str, recommendation_id: str,
    ) -> Optional["AIRecommendation"]:
        from app.models.sovereign_decision import AIRecommendation

        result = await self.db.execute(
            select(AIRecommendation).where(
                AIRecommendation.id == uuid.UUID(recommendation_id),
                AIRecommendation.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_recommendation_status(
        self,
        tenant_id: str,
        recommendation_id: str,
        status: str,
        approved_by_id: Optional[str] = None,
    ) -> Optional["AIRecommendation"]:
        from app.models.sovereign_decision import AIRecommendation

        result = await self.db.execute(
            select(AIRecommendation).where(
                AIRecommendation.id == uuid.UUID(recommendation_id),
                AIRecommendation.tenant_id == uuid.UUID(tenant_id),
            )
        )
        rec = result.scalar_one_or_none()
        if not rec:
            return None

        rec.status = status
        rec.updated_at = datetime.now(timezone.utc)
        if approved_by_id:
            rec.approved_by_id = uuid.UUID(approved_by_id)
            rec.approved_at = datetime.now(timezone.utc)
        await self.db.flush()
        return rec

    # ── Contradictions ─────────────────────────────

    async def create_contradiction(
        self, tenant_id: str, data: dict,
    ) -> "ContradictionRecord":
        from app.models.sovereign_decision import ContradictionRecord

        record = ContradictionRecord(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            recommendation_id=uuid.UUID(data["recommendation_id"]) if data.get("recommendation_id") else None,
            intended_action=data["intended_action"],
            claimed_action=data["claimed_action"],
            actual_tool_call=data.get("actual_tool_call"),
            side_effects=data.get("side_effects"),
            contradiction_status=data.get("contradiction_status", "none"),
            resolution_notes=data.get("resolution_notes"),
        )
        self.db.add(record)
        await self.db.flush()
        return record

    async def list_contradictions(
        self,
        tenant_id: str,
        status_filter: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_decision import ContradictionRecord

        query = select(ContradictionRecord).where(
            ContradictionRecord.tenant_id == uuid.UUID(tenant_id),
        )
        if status_filter:
            query = query.where(ContradictionRecord.contradiction_status == status_filter)

        query = query.order_by(ContradictionRecord.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ── Dashboard ──────────────────────────────────

    async def get_decision_dashboard(self, tenant_id: str) -> dict:
        from app.models.sovereign_decision import AIRecommendation, ContradictionRecord

        tid = uuid.UUID(tenant_id)

        total_recs = (await self.db.execute(
            select(func.count()).where(AIRecommendation.tenant_id == tid)
        )).scalar() or 0

        pending_recs = (await self.db.execute(
            select(func.count()).where(
                AIRecommendation.tenant_id == tid,
                AIRecommendation.status == "draft",
            )
        )).scalar() or 0

        approved_recs = (await self.db.execute(
            select(func.count()).where(
                AIRecommendation.tenant_id == tid,
                AIRecommendation.status == "approved",
            )
        )).scalar() or 0

        rejected_recs = (await self.db.execute(
            select(func.count()).where(
                AIRecommendation.tenant_id == tid,
                AIRecommendation.status == "rejected",
            )
        )).scalar() or 0

        avg_confidence = (await self.db.execute(
            select(func.avg(AIRecommendation.confidence_score)).where(
                AIRecommendation.tenant_id == tid,
            )
        )).scalar()

        total_contradictions = (await self.db.execute(
            select(func.count()).where(ContradictionRecord.tenant_id == tid)
        )).scalar() or 0

        unresolved_contradictions = (await self.db.execute(
            select(func.count()).where(
                ContradictionRecord.tenant_id == tid,
                ContradictionRecord.contradiction_status != "resolved",
            )
        )).scalar() or 0

        lane_result = await self.db.execute(
            select(
                AIRecommendation.model_lane,
                func.count().label("count"),
            ).where(
                AIRecommendation.tenant_id == tid,
            ).group_by(AIRecommendation.model_lane)
        )
        model_routing = {row.model_lane: row.count for row in lane_result.all()}

        return {
            "total_recommendations": total_recs,
            "pending_recommendations": pending_recs,
            "approved_recommendations": approved_recs,
            "rejected_recommendations": rejected_recs,
            "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
            "total_contradictions": total_contradictions,
            "unresolved_contradictions": unresolved_contradictions,
            "model_routing": model_routing,
        }
