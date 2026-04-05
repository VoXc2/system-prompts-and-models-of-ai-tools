"""Hourly tick: local scan only. External AI ecosystem scan is manual/CI — see docs."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def upgrade_director_hourly_tick() -> dict:
    from app.config import get_settings

    settings = get_settings()
    if not settings.DEALIX_UPGRADE_DIRECTOR_HOURLY:
        return {"status": "disabled", "reason": "DEALIX_UPGRADE_DIRECTOR_HOURLY=false"}

    async def run() -> dict:
        from uuid import UUID

        from app.database import async_session
        from app.services.upgrade_director.snapshot import collect_local_dependency_snapshot
        from app.services.upgrade_director.service import record_automated_hourly_scan

        snap = collect_local_dependency_snapshot()
        pt: str | None = (settings.DEALIX_PLATFORM_TENANT_ID or "").strip() or None
        platform_uuid = UUID(pt) if pt else None
        async with async_session() as db:
            cycle = await record_automated_hourly_scan(
                db, local_scan=snap, platform_tenant_id=platform_uuid
            )
            await db.commit()
            return {"status": "ok", "cycle_id": str(cycle.id), "snapshot_keys": list(snap.keys())}

    return asyncio.run(run())
