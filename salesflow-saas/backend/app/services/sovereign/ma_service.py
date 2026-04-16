"""Sovereign M&A — Acquisition target tracking and pipeline."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class MAService:
    """Manages M&A targets and the acquisition pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_target(
        self, tenant_id: str, data: dict,
    ) -> "MATarget":
        from app.models.sovereign_ma import MATarget

        target = MATarget(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            company_name=data["company_name"],
            company_name_ar=data.get("company_name_ar"),
            sector=data.get("sector"),
            status=data.get("status", "sourced"),
            valuation_low=data.get("valuation_low"),
            valuation_high=data.get("valuation_high"),
            currency=data.get("currency", "SAR"),
            synergy_model=data.get("synergy_model"),
            dd_room_access=data.get("dd_room_access"),
            investment_memo_url=data.get("investment_memo_url"),
            board_pack_url=data.get("board_pack_url"),
            offer_strategy=data.get("offer_strategy"),
            signing_readiness=data.get("signing_readiness", False),
            close_readiness=data.get("close_readiness", False),
            assigned_to_id=uuid.UUID(data["assigned_to_id"]) if data.get("assigned_to_id") else None,
            notes=data.get("notes"),
        )
        self.db.add(target)
        await self.db.flush()
        return target

    async def list_targets(
        self,
        tenant_id: str,
        status: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_ma import MATarget

        query = select(MATarget).where(
            MATarget.tenant_id == uuid.UUID(tenant_id),
        )
        if status:
            query = query.where(MATarget.status == status)

        query = query.order_by(MATarget.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_target(
        self, tenant_id: str, target_id: str,
    ) -> Optional["MATarget"]:
        from app.models.sovereign_ma import MATarget

        result = await self.db.execute(
            select(MATarget).where(
                MATarget.id == uuid.UUID(target_id),
                MATarget.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_target(
        self, tenant_id: str, target_id: str, data: dict,
    ) -> Optional["MATarget"]:
        from app.models.sovereign_ma import MATarget

        result = await self.db.execute(
            select(MATarget).where(
                MATarget.id == uuid.UUID(target_id),
                MATarget.tenant_id == uuid.UUID(tenant_id),
            )
        )
        target = result.scalar_one_or_none()
        if not target:
            return None

        updatable_fields = [
            "company_name", "company_name_ar", "sector", "status",
            "valuation_low", "valuation_high", "currency",
            "synergy_model", "dd_room_access",
            "investment_memo_url", "board_pack_url",
            "offer_strategy", "signing_readiness", "close_readiness",
            "assigned_to_id", "notes",
        ]
        for field in updatable_fields:
            if field in data:
                value = data[field]
                if field == "assigned_to_id" and value is not None:
                    value = uuid.UUID(value)
                setattr(target, field, value)

        target.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return target

    async def get_ma_pipeline(self, tenant_id: str) -> dict:
        from app.models.sovereign_ma import MATarget

        tid = uuid.UUID(tenant_id)

        stage_order = ["sourced", "screening", "due_diligence", "negotiation", "signing", "closed"]

        pipeline: dict = {}
        for stage in stage_order:
            count = (await self.db.execute(
                select(func.count()).where(
                    MATarget.tenant_id == tid,
                    MATarget.status == stage,
                )
            )).scalar() or 0

            val_low = (await self.db.execute(
                select(func.coalesce(func.sum(MATarget.valuation_low), 0)).where(
                    MATarget.tenant_id == tid,
                    MATarget.status == stage,
                )
            )).scalar() or 0

            val_high = (await self.db.execute(
                select(func.coalesce(func.sum(MATarget.valuation_high), 0)).where(
                    MATarget.tenant_id == tid,
                    MATarget.status == stage,
                )
            )).scalar() or 0

            pipeline[stage] = {
                "count": count,
                "valuation_low": float(val_low),
                "valuation_high": float(val_high),
            }

        total = sum(s["count"] for s in pipeline.values())

        signing_ready = (await self.db.execute(
            select(func.count()).where(
                MATarget.tenant_id == tid,
                MATarget.signing_readiness == True,  # noqa: E712
            )
        )).scalar() or 0

        close_ready = (await self.db.execute(
            select(func.count()).where(
                MATarget.tenant_id == tid,
                MATarget.close_readiness == True,  # noqa: E712
            )
        )).scalar() or 0

        return {
            "pipeline": pipeline,
            "total_targets": total,
            "signing_ready": signing_ready,
            "close_ready": close_ready,
        }
