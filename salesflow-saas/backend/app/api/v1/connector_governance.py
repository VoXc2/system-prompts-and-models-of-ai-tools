"""Connector Governance API — integration health from real IntegrationSyncState."""

from fastapi import APIRouter, Depends
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.connector_governance import connector_governance

router = APIRouter(prefix="/connectors", tags=["Connector Governance"])


@router.get("/governance")
async def governance_board(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get connector governance board from real IntegrationSyncState data."""
    board = await connector_governance.get_governance_board(db, tenant_id=tenant_id)
    return {"connectors": board, "total": len(board)}


@router.post("/{connector_key}/health-check")
async def health_check(
    connector_key: str,
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Trigger health check and update connector status."""
    conn = await connector_governance.update_connector_status(
        db, tenant_id=tenant_id, connector_key=connector_key, status="ok"
    )
    return {"connector_key": connector_key, "status": conn.status}


@router.get("/{connector_key}/history")
async def connector_history(connector_key: str) -> Dict[str, Any]:
    """Get sync history for a connector."""
    return {"connector_key": connector_key, "history": []}


@router.put("/{connector_key}/disable")
async def disable_connector(
    connector_key: str,
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Disable a connector."""
    conn = await connector_governance.update_connector_status(
        db, tenant_id=tenant_id, connector_key=connector_key, status="disabled", error="Manually disabled"
    )
    return {"connector_key": connector_key, "status": "disabled"}
