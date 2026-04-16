"""Sovereign Connector Facade: connector registry and health board."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_connector import ConnectorDefinition
from app.schemas.sovereign import (
    ConnectorDefinitionCreate,
    ConnectorDefinitionResponse,
    ConnectorHealthUpdate,
)

router = APIRouter(prefix="/sovereign/connectors", tags=["Sovereign Connector Facade"])


@router.post("/", response_model=ConnectorDefinitionResponse, status_code=201)
async def register_connector(
    data: ConnectorDefinitionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    connector = ConnectorDefinition(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(connector)
    await db.flush()
    await db.refresh(connector)
    return ConnectorDefinitionResponse.model_validate(connector)


@router.get("/", response_model=List[ConnectorDefinitionResponse])
async def list_connectors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(ConnectorDefinition)
        .where(ConnectorDefinition.tenant_id == current_user.tenant_id)
        .order_by(ConnectorDefinition.created_at.desc())
    )
    result = await db.execute(q)
    return [ConnectorDefinitionResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/health-board")
async def connector_health_board(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connector health board: all connectors with activity summary."""
    q = await db.execute(
        select(ConnectorDefinition)
        .where(ConnectorDefinition.tenant_id == current_user.tenant_id)
    )
    connectors = q.scalars().all()

    active = sum(1 for c in connectors if c.is_active)
    inactive = len(connectors) - active

    items = []
    for c in connectors:
        items.append({
            "connector_key": c.connector_key,
            "display_name": c.display_name,
            "display_name_ar": c.display_name_ar,
            "provider": c.provider,
            "version": c.version,
            "is_active": c.is_active,
            "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
            "action_class": c.action_class,
        })

    return {
        "total": len(connectors),
        "active": active,
        "inactive": inactive,
        "connectors": items,
    }


@router.get("/{key}", response_model=ConnectorDefinitionResponse)
async def get_connector(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConnectorDefinition).where(
            ConnectorDefinition.connector_key == key,
            ConnectorDefinition.tenant_id == current_user.tenant_id,
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return ConnectorDefinitionResponse.model_validate(connector)


@router.patch("/{key}/health", response_model=ConnectorDefinitionResponse)
async def update_connector_health(
    key: str,
    data: ConnectorHealthUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConnectorDefinition).where(
            ConnectorDefinition.connector_key == key,
            ConnectorDefinition.tenant_id == current_user.tenant_id,
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(connector, field, value)
    if data.last_verified_at is None and data.is_active is not None:
        connector.last_verified_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(connector)
    return ConnectorDefinitionResponse.model_validate(connector)
