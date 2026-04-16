"""Sovereign Connector — Connector registry and health board."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class ConnectorService:
    """Manages connector definitions and their health status."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_connector(
        self, tenant_id: str, data: dict,
    ) -> "ConnectorDefinition":
        from app.models.sovereign_connector import ConnectorDefinition

        connector = ConnectorDefinition(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            connector_key=data["connector_key"],
            display_name=data["display_name"],
            display_name_ar=data.get("display_name_ar"),
            version=data["version"],
            provider=data["provider"],
            contract_schema=data["contract_schema"],
            retry_policy=data["retry_policy"],
            timeout_seconds=data.get("timeout_seconds", 30),
            idempotency_key_template=data.get("idempotency_key_template"),
            action_class=data.get("action_class", "auto"),
            audit_events=data.get("audit_events"),
            telemetry_config=data.get("telemetry_config"),
            compensation_notes=data.get("compensation_notes"),
            is_active=data.get("is_active", True),
            last_verified_at=data.get("last_verified_at"),
        )
        self.db.add(connector)
        await self.db.flush()
        return connector

    async def list_connectors(self, tenant_id: str) -> list:
        from app.models.sovereign_connector import ConnectorDefinition

        query = (
            select(ConnectorDefinition)
            .where(ConnectorDefinition.tenant_id == uuid.UUID(tenant_id))
            .order_by(ConnectorDefinition.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_connector(
        self, tenant_id: str, connector_key: str,
    ) -> Optional["ConnectorDefinition"]:
        from app.models.sovereign_connector import ConnectorDefinition

        result = await self.db.execute(
            select(ConnectorDefinition).where(
                ConnectorDefinition.connector_key == connector_key,
                ConnectorDefinition.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_connector_status(
        self,
        tenant_id: str,
        connector_key: str,
        status: bool,
        error: Optional[str] = None,
    ) -> Optional["ConnectorDefinition"]:
        from app.models.sovereign_connector import ConnectorDefinition

        result = await self.db.execute(
            select(ConnectorDefinition).where(
                ConnectorDefinition.connector_key == connector_key,
                ConnectorDefinition.tenant_id == uuid.UUID(tenant_id),
            )
        )
        connector = result.scalar_one_or_none()
        if not connector:
            return None

        connector.is_active = status
        connector.last_verified_at = datetime.now(timezone.utc)
        connector.updated_at = datetime.now(timezone.utc)
        if error:
            connector.compensation_notes = error

        await self.db.flush()
        return connector

    async def get_connector_health_board(self, tenant_id: str) -> dict:
        from app.models.sovereign_connector import ConnectorDefinition

        tid = uuid.UUID(tenant_id)

        total = (await self.db.execute(
            select(func.count()).where(ConnectorDefinition.tenant_id == tid)
        )).scalar() or 0

        active = (await self.db.execute(
            select(func.count()).where(
                ConnectorDefinition.tenant_id == tid,
                ConnectorDefinition.is_active == True,  # noqa: E712
            )
        )).scalar() or 0

        inactive = total - active

        by_provider_result = await self.db.execute(
            select(
                ConnectorDefinition.provider,
                func.count().label("count"),
            ).where(ConnectorDefinition.tenant_id == tid).group_by(ConnectorDefinition.provider)
        )
        by_provider = {row.provider: row.count for row in by_provider_result.all()}

        by_action_class_result = await self.db.execute(
            select(
                ConnectorDefinition.action_class,
                func.count().label("count"),
            ).where(ConnectorDefinition.tenant_id == tid).group_by(ConnectorDefinition.action_class)
        )
        by_action_class = {row.action_class: row.count for row in by_action_class_result.all()}

        return {
            "total_connectors": total,
            "active": active,
            "inactive": inactive,
            "by_provider": by_provider,
            "by_action_class": by_action_class,
        }
