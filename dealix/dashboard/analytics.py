"""
Analytics / KPI aggregation.
تجميع مؤشرات الأداء.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AgentRunRecord, DealRecord, LeadRecord


@dataclass
class KPISummary:
    leads_total: int
    leads_by_status: dict[str, int]
    leads_by_source: dict[str, int]
    leads_by_sector: dict[str, int]
    deals_total: int
    pipeline_sar: float
    agent_runs_total: int
    agent_runs_errors: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "leads_total": self.leads_total,
            "leads_by_status": self.leads_by_status,
            "leads_by_source": self.leads_by_source,
            "leads_by_sector": self.leads_by_sector,
            "deals_total": self.deals_total,
            "pipeline_sar": self.pipeline_sar,
            "agent_runs_total": self.agent_runs_total,
            "agent_runs_errors": self.agent_runs_errors,
        }


class Analytics:
    """DB-backed KPI aggregation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def summary(self) -> KPISummary:
        total_leads = (await self.session.scalar(select(func.count(LeadRecord.id)))) or 0

        by_status = {
            row.status: row.count
            for row in (
                await self.session.execute(
                    select(LeadRecord.status, func.count(LeadRecord.id).label("count")).group_by(
                        LeadRecord.status
                    )
                )
            ).all()
        }
        by_source = {
            row.source: row.count
            for row in (
                await self.session.execute(
                    select(LeadRecord.source, func.count(LeadRecord.id).label("count")).group_by(
                        LeadRecord.source
                    )
                )
            ).all()
        }
        by_sector = {
            (row.sector or "unknown"): row.count
            for row in (
                await self.session.execute(
                    select(LeadRecord.sector, func.count(LeadRecord.id).label("count")).group_by(
                        LeadRecord.sector
                    )
                )
            ).all()
        }

        deals_total = (await self.session.scalar(select(func.count(DealRecord.id)))) or 0
        pipeline_sar = (await self.session.scalar(select(func.sum(DealRecord.amount)))) or 0.0

        runs_total = (await self.session.scalar(select(func.count(AgentRunRecord.id)))) or 0
        runs_errors = (
            await self.session.scalar(
                select(func.count(AgentRunRecord.id)).where(AgentRunRecord.status == "error")
            )
        ) or 0

        return KPISummary(
            leads_total=int(total_leads),
            leads_by_status=by_status,
            leads_by_source=by_source,
            leads_by_sector=by_sector,
            deals_total=int(deals_total),
            pipeline_sar=float(pipeline_sar),
            agent_runs_total=int(runs_total),
            agent_runs_errors=int(runs_errors),
        )
