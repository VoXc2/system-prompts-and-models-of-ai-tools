"""Sovereign Growth OS — enterprise command center snapshot (structured JSON)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.sovereign_os import SovereignOsSnapshot
from app.services.sovereign_os_snapshot import build_sovereign_os_snapshot, new_correlation_id

router = APIRouter(prefix="/sovereign-os", tags=["Sovereign OS"])


@router.get("/snapshot", response_model=SovereignOsSnapshot)
async def sovereign_os_snapshot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
):
    """
    Typed snapshot for Executive Room surfaces: revenue, partnerships, M&A,
    expansion, PMI, approvals, risk, compliance matrix, and model routing fabric.
    """
    cid = x_correlation_id or new_correlation_id()
    return await build_sovereign_os_snapshot(db, tenant_id=current_user.tenant_id, correlation_id=cid)
