"""
Rate limiting via slowapi.
تحديد المعدل عبر slowapi.

Default policy (per route):
  POST /api/v1/leads          → 10/min
  POST /api/v1/sales/*        → 30/min
  POST /api/v1/webhooks/wa    → 100/min
  Other API routes            → 60/min
  Global (per IP, all paths)  → 1000/min
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address

    _HAS_SLOWAPI = True
except ImportError:  # pragma: no cover
    _HAS_SLOWAPI = False
    Limiter = None  # type: ignore
    RateLimitExceeded = Exception  # type: ignore


def _key_func(request: Request) -> str:
    """Prefer API key (authenticated callers) over IP."""
    key = request.headers.get("X-API-Key")
    if key:
        return f"api:{key[:16]}"
    if _HAS_SLOWAPI:
        return get_remote_address(request)
    return request.client.host if request.client else "anon"


DEFAULT_GLOBAL_LIMIT = os.getenv("RL_GLOBAL", "1000/minute")

limiter: Any = None
if _HAS_SLOWAPI:
    limiter = Limiter(
        key_func=_key_func,
        default_limits=[DEFAULT_GLOBAL_LIMIT],
        storage_uri=os.getenv("RL_STORAGE_URI", "memory://"),
        strategy="fixed-window",
    )


# Per-route limits (applied via decorators in routers)
LIMITS = {
    "leads_create": os.getenv("RL_LEADS", "10/minute"),
    "sales_any": os.getenv("RL_SALES", "30/minute"),
    "whatsapp_webhook": os.getenv("RL_WA_WEBHOOK", "100/minute"),
    "generic_api": os.getenv("RL_GENERIC", "60/minute"),
}


def setup_rate_limit(app: FastAPI) -> None:
    """Wire slowapi into the FastAPI app. No-op if slowapi is missing."""
    if not _HAS_SLOWAPI or limiter is None:
        return

    app.state.limiter = limiter

    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": "RateLimitExceeded",
                "detail": f"Too many requests: {exc.detail}",
                "ar": "تجاوزت الحد المسموح، يرجى المحاولة لاحقاً.",
            },
        )

    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
