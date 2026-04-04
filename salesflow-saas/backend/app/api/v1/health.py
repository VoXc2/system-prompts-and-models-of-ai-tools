from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
from pydantic import BaseModel as Schema

from app.database import get_db
from app.config import get_settings

router = APIRouter()
_settings = get_settings()


class HealthResponse(Schema):
    status: str
    timestamp: str
    version: str = "2.0.0"
    app: str = "Dealix"
    environment: str = "production"


class ReadyResponse(Schema):
    status: str
    database: str
    redis: str | None = None
    timestamp: str


async def _redis_ping_status() -> str:
    """Best-effort broker/cache check (Celery uses REDIS_URL)."""
    url = _settings.REDIS_URL
    if not url:
        return "skipped"
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(url, socket_connect_timeout=1.5)
        await client.ping()
        await client.aclose()
        return "connected"
    except Exception:
        return "unavailable"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="2.0.0",
        app=_settings.APP_NAME,
        environment=_settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    redis_status = await _redis_ping_status()
    overall = "ready" if db_status == "connected" else "not_ready"
    return ReadyResponse(
        status=overall,
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
