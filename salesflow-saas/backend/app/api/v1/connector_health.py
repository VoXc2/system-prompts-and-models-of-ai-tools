"""Connector Health API — Versioned registry, health board, governance metadata."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import ConnectorRegistry
from app.services.connector_facade import ConnectorFacade

router = APIRouter(prefix="/connector-health", tags=["Connector Health — صحة الموصلات"])


class ConnectorCreate(BaseModel):
    connector_key: str
    display_name_ar: str
    display_name_en: str | None = None
    vendor: str | None = None
    api_version: str = "v1"
    retry_policy: dict | None = None
    timeout_ms: int = 30000
    idempotency_key_strategy: str = "request_id"
    approval_policy: str = "A"
    audit_mapping: dict | None = None
    telemetry_mapping: dict | None = None
    rollback_notes: str | None = None
    compensation_strategy: str | None = None
    contract_schema: dict | None = None


@router.post("/connectors", status_code=status.HTTP_201_CREATED)
async def register_connector(
    tenant_id: str,
    payload: ConnectorCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """تسجيل موصل جديد — Register a new connector in the governed registry."""
    conn = ConnectorRegistry(
        tenant_id=tenant_id,
        connector_key=payload.connector_key,
        display_name_ar=payload.display_name_ar,
        display_name_en=payload.display_name_en,
        vendor=payload.vendor,
        api_version=payload.api_version,
        retry_policy=payload.retry_policy or {"max_retries": 3, "backoff_multiplier_ms": 1000, "max_backoff_ms": 30000},
        timeout_ms=payload.timeout_ms,
        idempotency_key_strategy=payload.idempotency_key_strategy,
        approval_policy=payload.approval_policy,
        audit_mapping=payload.audit_mapping or {},
        telemetry_mapping=payload.telemetry_mapping or {},
        rollback_notes=payload.rollback_notes,
        compensation_strategy=payload.compensation_strategy,
        contract_schema=payload.contract_schema or {},
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return {"id": str(conn.id), "connector_key": conn.connector_key, "health_status": conn.health_status}


@router.get("/connectors")
async def list_connectors(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """لوحة صحة الموصلات — Connector health board."""
    facade = ConnectorFacade(db, tenant_id)
    return await facade.get_health_board()


@router.get("/connectors/{connector_key}")
async def get_connector(
    connector_key: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(ConnectorRegistry).where(
            ConnectorRegistry.connector_key == connector_key,
            ConnectorRegistry.tenant_id == tenant_id,
        ).limit(1)
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {
        "id": str(conn.id),
        "connector_key": conn.connector_key,
        "display_name_ar": conn.display_name_ar,
        "display_name_en": conn.display_name_en,
        "vendor": conn.vendor,
        "api_version": conn.api_version,
        "retry_policy": conn.retry_policy,
        "timeout_ms": conn.timeout_ms,
        "idempotency_key_strategy": conn.idempotency_key_strategy,
        "approval_policy": conn.approval_policy,
        "audit_mapping": conn.audit_mapping,
        "telemetry_mapping": conn.telemetry_mapping,
        "rollback_notes": conn.rollback_notes,
        "compensation_strategy": conn.compensation_strategy,
        "contract_schema": conn.contract_schema,
        "health_status": conn.health_status,
        "last_success_at": conn.last_success_at.isoformat() if conn.last_success_at else None,
        "last_error": conn.last_error,
        "is_active": conn.is_active,
        "deprecated_at": conn.deprecated_at.isoformat() if conn.deprecated_at else None,
    }


@router.post("/connectors/{connector_key}/test-call")
async def test_connector_call(
    connector_key: str,
    tenant_id: str,
    action: str,
    payload: dict = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """اختبار الموصل — Test a connector call through the governed facade."""
    facade = ConnectorFacade(db, tenant_id)
    return await facade.call(connector_key, action, payload or {})
