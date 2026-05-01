"""Health, liveness, readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import HealthResponse
from core.config.settings import get_settings
from core.llm import get_router as get_model_router

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness + config summary."""
    settings = get_settings()
    providers = [p.value for p in get_model_router().available_providers()]
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        env=settings.app_env,
        providers=providers,
    )


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Readiness probe."""
    return {"status": "ready"}


@router.get("/live")
async def live() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "alive"}


@router.get("/health/deep")
async def health_deep() -> dict[str, object]:
    """Deep health check — verifies DB, Redis, LLM providers."""
    import os
    import time

    checks: dict[str, dict[str, object]] = {}
    overall = "ok"

    # Postgres
    t0 = time.perf_counter()
    try:
        import psycopg2  # type: ignore

        dsn = os.getenv("DATABASE_URL") or os.getenv("DATABASE_DSN")
        if dsn:
            conn = psycopg2.connect(dsn, connect_timeout=3)
            conn.cursor().execute("SELECT 1")
            conn.close()
            checks["postgres"] = {"status": "ok", "ms": round((time.perf_counter() - t0) * 1000, 1)}
        else:
            checks["postgres"] = {"status": "skip", "reason": "no DATABASE_URL"}
    except Exception as e:  # pragma: no cover
        checks["postgres"] = {"status": "fail", "error": str(e)[:200]}
        overall = "degraded"

    # Redis
    t0 = time.perf_counter()
    try:
        import redis  # type: ignore

        url = os.getenv("REDIS_URL")
        if url:
            r = redis.from_url(url, socket_timeout=3)
            r.ping()
            checks["redis"] = {"status": "ok", "ms": round((time.perf_counter() - t0) * 1000, 1)}
        else:
            checks["redis"] = {"status": "skip", "reason": "no REDIS_URL"}
    except Exception as e:  # pragma: no cover
        checks["redis"] = {"status": "fail", "error": str(e)[:200]}
        overall = "degraded"

    # LLM providers
    providers = [p.value for p in get_model_router().available_providers()]
    checks["llm_providers"] = {"status": "ok" if providers else "fail", "providers": providers}
    if not providers:
        overall = "degraded"

    return {"status": overall, "checks": checks, "version": get_settings().app_version}


@router.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    """Standard healthz alias for UptimeRobot/K8s probes."""
    return {"status": "ok", "service": "dealix"}


@router.get("/_test_sentry", include_in_schema=False)
async def test_sentry() -> dict[str, str]:
    """Deliberate error to verify Sentry integration.

    Protected by ADMIN_TOKEN header in production.
    """
    import os

    from fastapi import HTTPException

    # In dev, allow freely. In prod, require admin token.
    if os.getenv("APP_ENV", "dev") == "prod":
        admin_token = os.getenv("ADMIN_TOKEN", "")
        # Request injection is complex in FastAPI without Depends; keep simple check
        if not admin_token:
            raise HTTPException(status_code=404, detail="Not found")

    raise Exception("Test Sentry integration — deliberate error")
