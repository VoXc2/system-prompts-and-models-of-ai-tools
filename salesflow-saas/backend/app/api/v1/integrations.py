"""Integrations management API — connect/disconnect external services."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.api.v1.deps import get_current_user, get_db, require_role
from app.models.integration import IntegrationAccount

router = APIRouter()


class IntegrationConnect(BaseModel):
    provider: str  # whatsapp, google_calendar, payment, email_smtp
    account_id: str
    account_name: Optional[str] = None
    credentials: Optional[dict] = None
    settings: Optional[dict] = None


@router.get("")
async def list_integrations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(IntegrationAccount).where(IntegrationAccount.tenant_id == tenant_id)
    )
    items = result.scalars().all()
    return {"items": [_serialize(i) for i in items]}


@router.post("", status_code=201)
async def connect_integration(
    data: IntegrationConnect,
    current_user: dict = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
):
    integration = IntegrationAccount(
        tenant_id=current_user["tenant_id"],
        provider=data.provider,
        account_id=data.account_id,
        account_name=data.account_name,
        is_active=True,
    )
    if data.credentials and hasattr(integration, "credentials"):
        integration.credentials = data.credentials
    if data.settings and hasattr(integration, "settings"):
        integration.settings = data.settings
    db.add(integration)
    await db.flush()
    return _serialize(integration)


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: UUID,
    current_user: dict = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IntegrationAccount).where(
            IntegrationAccount.id == integration_id,
            IntegrationAccount.tenant_id == current_user["tenant_id"],
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="الربط غير موجود")
    integration.is_active = False
    await db.flush()
    return {"status": "disconnected"}


@router.get("/{integration_id}/status")
async def integration_status(
    integration_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IntegrationAccount).where(
            IntegrationAccount.id == integration_id,
            IntegrationAccount.tenant_id == current_user["tenant_id"],
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="الربط غير موجود")
    return {
        "id": str(integration.id),
        "provider": integration.provider,
        "is_active": integration.is_active,
        "connected_at": integration.created_at.isoformat() if integration.created_at else None,
    }


def _serialize(i):
    return {
        "id": str(i.id),
        "provider": i.provider,
        "account_id": i.account_id,
        "account_name": getattr(i, "account_name", None),
        "is_active": i.is_active,
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }
