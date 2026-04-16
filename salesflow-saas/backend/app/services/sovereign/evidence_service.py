"""Sovereign Evidence — Evidence packs for executive decisions."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class EvidenceService:
    """Manages evidence packs assembled for executive decisions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_evidence_pack(
        self,
        tenant_id: str,
        data: dict,
        assembled_by_id: Optional[str] = None,
    ) -> "EvidencePack":
        from app.models.sovereign_evidence import EvidencePack

        pack = EvidencePack(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            title=data["title"],
            title_ar=data.get("title_ar"),
            pack_type=data["pack_type"],
            status=data.get("status", "assembling"),
            entity_type=data.get("entity_type"),
            entity_id=uuid.UUID(data["entity_id"]) if data.get("entity_id") else None,
            sources=data["sources"],
            assumptions=data.get("assumptions"),
            financial_model_version=data.get("financial_model_version"),
            policy_notes=data.get("policy_notes"),
            alternatives=data.get("alternatives"),
            rollback_plan=data.get("rollback_plan"),
            approval_class=data.get("approval_class"),
            reversibility_class=data.get("reversibility_class"),
            sensitivity=data.get("sensitivity", "internal"),
            assembled_by_id=uuid.UUID(assembled_by_id) if assembled_by_id else None,
        )
        self.db.add(pack)
        await self.db.flush()
        return pack

    async def list_evidence_packs(
        self,
        tenant_id: str,
        pack_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_evidence import EvidencePack

        query = select(EvidencePack).where(
            EvidencePack.tenant_id == uuid.UUID(tenant_id),
        )
        if pack_type:
            query = query.where(EvidencePack.pack_type == pack_type)
        if status:
            query = query.where(EvidencePack.status == status)

        query = query.order_by(EvidencePack.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_evidence_pack(
        self, tenant_id: str, pack_id: str,
    ) -> Optional["EvidencePack"]:
        from app.models.sovereign_evidence import EvidencePack

        result = await self.db.execute(
            select(EvidencePack).where(
                EvidencePack.id == uuid.UUID(pack_id),
                EvidencePack.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_evidence_status(
        self,
        tenant_id: str,
        pack_id: str,
        status: str,
        approved_by_id: Optional[str] = None,
    ) -> Optional["EvidencePack"]:
        from app.models.sovereign_evidence import EvidencePack

        result = await self.db.execute(
            select(EvidencePack).where(
                EvidencePack.id == uuid.UUID(pack_id),
                EvidencePack.tenant_id == uuid.UUID(tenant_id),
            )
        )
        pack = result.scalar_one_or_none()
        if not pack:
            return None

        pack.status = status
        pack.updated_at = datetime.now(timezone.utc)
        if approved_by_id:
            pack.approved_by_id = uuid.UUID(approved_by_id)
            pack.approved_at = datetime.now(timezone.utc)

        await self.db.flush()
        return pack

    async def get_evidence_summary(self, tenant_id: str) -> dict:
        from app.models.sovereign_evidence import EvidencePack

        tid = uuid.UUID(tenant_id)

        total = (await self.db.execute(
            select(func.count()).where(EvidencePack.tenant_id == tid)
        )).scalar() or 0

        by_status_result = await self.db.execute(
            select(
                EvidencePack.status,
                func.count().label("count"),
            ).where(EvidencePack.tenant_id == tid).group_by(EvidencePack.status)
        )
        by_status = {row.status: row.count for row in by_status_result.all()}

        by_type_result = await self.db.execute(
            select(
                EvidencePack.pack_type,
                func.count().label("count"),
            ).where(EvidencePack.tenant_id == tid).group_by(EvidencePack.pack_type)
        )
        by_type = {row.pack_type: row.count for row in by_type_result.all()}

        by_sensitivity_result = await self.db.execute(
            select(
                EvidencePack.sensitivity,
                func.count().label("count"),
            ).where(EvidencePack.tenant_id == tid).group_by(EvidencePack.sensitivity)
        )
        by_sensitivity = {row.sensitivity: row.count for row in by_sensitivity_result.all()}

        pending_approval = (await self.db.execute(
            select(func.count()).where(
                EvidencePack.tenant_id == tid,
                EvidencePack.status == "pending_approval",
            )
        )).scalar() or 0

        return {
            "total_packs": total,
            "by_status": by_status,
            "by_type": by_type,
            "by_sensitivity": by_sensitivity,
            "pending_approval": pending_approval,
        }
