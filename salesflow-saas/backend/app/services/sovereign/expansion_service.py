"""Sovereign Expansion — Market expansion tracking and launch console."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class ExpansionService:
    """Manages expansion markets and the launch console."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_market(
        self, tenant_id: str, data: dict,
    ) -> "ExpansionMarket":
        from app.models.sovereign_expansion import ExpansionMarket

        market = ExpansionMarket(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            market_name=data["market_name"],
            market_name_ar=data.get("market_name_ar"),
            country_code=data["country_code"],
            region=data.get("region"),
            status=data.get("status", "scanning"),
            priority_score=data.get("priority_score"),
            compliance_readiness=data.get("compliance_readiness"),
            localization_status=data.get("localization_status"),
            pricing_plan=data.get("pricing_plan"),
            channel_plan=data.get("channel_plan"),
            launch_date=data.get("launch_date"),
            stop_loss_threshold=data.get("stop_loss_threshold"),
            actual_vs_forecast=data.get("actual_vs_forecast"),
            currency=data.get("currency", "SAR"),
            assigned_to_id=uuid.UUID(data["assigned_to_id"]) if data.get("assigned_to_id") else None,
            notes=data.get("notes"),
        )
        self.db.add(market)
        await self.db.flush()
        return market

    async def list_markets(
        self,
        tenant_id: str,
        status: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_expansion import ExpansionMarket

        query = select(ExpansionMarket).where(
            ExpansionMarket.tenant_id == uuid.UUID(tenant_id),
        )
        if status:
            query = query.where(ExpansionMarket.status == status)

        query = query.order_by(ExpansionMarket.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_market(
        self, tenant_id: str, market_id: str,
    ) -> Optional["ExpansionMarket"]:
        from app.models.sovereign_expansion import ExpansionMarket

        result = await self.db.execute(
            select(ExpansionMarket).where(
                ExpansionMarket.id == uuid.UUID(market_id),
                ExpansionMarket.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_market(
        self, tenant_id: str, market_id: str, data: dict,
    ) -> Optional["ExpansionMarket"]:
        from app.models.sovereign_expansion import ExpansionMarket

        result = await self.db.execute(
            select(ExpansionMarket).where(
                ExpansionMarket.id == uuid.UUID(market_id),
                ExpansionMarket.tenant_id == uuid.UUID(tenant_id),
            )
        )
        market = result.scalar_one_or_none()
        if not market:
            return None

        updatable_fields = [
            "market_name", "market_name_ar", "country_code", "region",
            "status", "priority_score", "compliance_readiness",
            "localization_status", "pricing_plan", "channel_plan",
            "launch_date", "stop_loss_threshold", "actual_vs_forecast",
            "currency", "assigned_to_id", "notes",
        ]
        for field in updatable_fields:
            if field in data:
                value = data[field]
                if field == "assigned_to_id" and value is not None:
                    value = uuid.UUID(value)
                setattr(market, field, value)

        market.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return market

    async def get_expansion_console(self, tenant_id: str) -> dict:
        from app.models.sovereign_expansion import ExpansionMarket

        tid = uuid.UUID(tenant_id)

        statuses = ["scanning", "evaluating", "preparing", "launching", "live", "paused"]

        by_status: dict = {}
        for s in statuses:
            count = (await self.db.execute(
                select(func.count()).where(
                    ExpansionMarket.tenant_id == tid,
                    ExpansionMarket.status == s,
                )
            )).scalar() or 0
            by_status[s] = count

        total = sum(by_status.values())

        by_region_result = await self.db.execute(
            select(
                ExpansionMarket.region,
                func.count().label("count"),
            ).where(
                ExpansionMarket.tenant_id == tid,
            ).group_by(ExpansionMarket.region)
        )
        by_region = {
            (row.region or "unassigned"): row.count
            for row in by_region_result.all()
        }

        avg_priority = (await self.db.execute(
            select(func.avg(ExpansionMarket.priority_score)).where(
                ExpansionMarket.tenant_id == tid,
            )
        )).scalar()

        return {
            "total_markets": total,
            "by_status": by_status,
            "by_region": by_region,
            "average_priority_score": float(avg_priority) if avg_priority else 0.0,
        }
