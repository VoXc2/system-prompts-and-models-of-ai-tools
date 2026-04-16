"""Sovereign Partnership — Strategic partner management and scorecards."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class PartnershipService:
    """Manages strategic partners and partnership scorecards."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_partner(
        self, tenant_id: str, data: dict,
    ) -> "Partner":
        from app.models.sovereign_partnership import Partner

        partner = Partner(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            name=data["name"],
            name_ar=data.get("name_ar"),
            partner_type=data["partner_type"],
            status=data.get("status", "prospect"),
            strategic_fit_score=data.get("strategic_fit_score"),
            channel_economics=data.get("channel_economics"),
            contribution_margin=data.get("contribution_margin"),
            currency=data.get("currency", "SAR"),
            alliance_structure=data.get("alliance_structure"),
            term_sheet_url=data.get("term_sheet_url"),
            activated_at=data.get("activated_at"),
            contact_name=data.get("contact_name"),
            contact_email=data.get("contact_email"),
            contact_phone=data.get("contact_phone"),
            notes=data.get("notes"),
            notes_ar=data.get("notes_ar"),
            scorecard_data=data.get("scorecard_data"),
        )
        self.db.add(partner)
        await self.db.flush()
        return partner

    async def list_partners(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        partner_type: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_partnership import Partner

        query = select(Partner).where(
            Partner.tenant_id == uuid.UUID(tenant_id),
        )
        if status:
            query = query.where(Partner.status == status)
        if partner_type:
            query = query.where(Partner.partner_type == partner_type)

        query = query.order_by(Partner.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_partner(
        self, tenant_id: str, partner_id: str,
    ) -> Optional["Partner"]:
        from app.models.sovereign_partnership import Partner

        result = await self.db.execute(
            select(Partner).where(
                Partner.id == uuid.UUID(partner_id),
                Partner.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_partner(
        self, tenant_id: str, partner_id: str, data: dict,
    ) -> Optional["Partner"]:
        from app.models.sovereign_partnership import Partner

        result = await self.db.execute(
            select(Partner).where(
                Partner.id == uuid.UUID(partner_id),
                Partner.tenant_id == uuid.UUID(tenant_id),
            )
        )
        partner = result.scalar_one_or_none()
        if not partner:
            return None

        updatable_fields = [
            "name", "name_ar", "partner_type", "status",
            "strategic_fit_score", "channel_economics", "contribution_margin",
            "currency", "alliance_structure", "term_sheet_url", "activated_at",
            "contact_name", "contact_email", "contact_phone",
            "notes", "notes_ar", "scorecard_data",
        ]
        for field in updatable_fields:
            if field in data:
                setattr(partner, field, data[field])

        partner.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return partner

    async def get_partnership_scorecards(self, tenant_id: str) -> dict:
        from app.models.sovereign_partnership import Partner

        tid = uuid.UUID(tenant_id)

        total = (await self.db.execute(
            select(func.count()).where(Partner.tenant_id == tid)
        )).scalar() or 0

        by_status_result = await self.db.execute(
            select(
                Partner.status,
                func.count().label("count"),
            ).where(Partner.tenant_id == tid).group_by(Partner.status)
        )
        by_status = {row.status: row.count for row in by_status_result.all()}

        by_type_result = await self.db.execute(
            select(
                Partner.partner_type,
                func.count().label("count"),
            ).where(Partner.tenant_id == tid).group_by(Partner.partner_type)
        )
        by_type = {row.partner_type: row.count for row in by_type_result.all()}

        avg_fit = (await self.db.execute(
            select(func.avg(Partner.strategic_fit_score)).where(Partner.tenant_id == tid)
        )).scalar()

        total_margin = (await self.db.execute(
            select(func.coalesce(func.sum(Partner.contribution_margin), 0)).where(
                Partner.tenant_id == tid,
            )
        )).scalar()

        return {
            "total_partners": total,
            "by_status": by_status,
            "by_type": by_type,
            "average_strategic_fit": float(avg_fit) if avg_fit else 0.0,
            "total_contribution_margin": float(total_margin),
        }
