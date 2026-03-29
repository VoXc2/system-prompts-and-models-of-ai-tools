import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.api.v1.router import api_router

logger = logging.getLogger(__name__)
settings = get_settings()

# Rate limiter — uses client IP, defaults to 100 req/min per endpoint
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="AI Revenue Operating System for Saudi SMEs — Multi-tenant Sales Automation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS — configurable via ALLOWED_ORIGINS env var
allowed_origins = [settings.FRONTEND_URL]
if hasattr(settings, "ALLOWED_ORIGINS") and settings.ALLOWED_ORIGINS:
    allowed_origins.extend([o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()])
if settings.DEBUG:
    allowed_origins.append("http://localhost:3000")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler — never leak stack traces in production
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "حدث خطأ في الخادم. حاول مرة أخرى لاحقاً.",
            "error": "internal_server_error",
        },
    )


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    if request.url.path not in ("/api/v1/health", "/api/docs", "/api/redoc", "/api/openapi.json"):
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check — verifies DB and Redis connectivity
# ---------------------------------------------------------------------------

@app.get("/api/v1/health")
async def health_check():
    health = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "database": "unknown",
        "redis": "unknown",
    }

    # Check database
    try:
        from app.database import async_session
        from sqlalchemy import text
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        health["database"] = f"error: {str(e)[:100]}"
        health["status"] = "degraded"

    # Check Redis
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        health["redis"] = "connected"
    except Exception as e:
        health["redis"] = f"error: {str(e)[:100]}"
        health["status"] = "degraded"

    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)
