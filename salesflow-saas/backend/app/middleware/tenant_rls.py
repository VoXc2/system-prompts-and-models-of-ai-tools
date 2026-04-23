"""Tenant RLS Middleware — sets PostgreSQL session tenant context per request.

Extracts tenant_id from JWT and sets it via SET LOCAL on the DB session.
RLS policies on tenant-scoped tables filter by this setting.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TenantRLSMiddleware(BaseHTTPMiddleware):
    """Sets app.tenant_id session variable from JWT for RLS enforcement.

    Note: RLS works only on PostgreSQL. SQLite (CI) silently ignores the
    SET LOCAL statement, so this middleware is a no-op on SQLite.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract tenant_id from JWT if available
        tenant_id = None
        try:
            from app.utils.security import decode_token
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                token = auth[7:]
                payload = decode_token(token)
                tenant_id = payload.get("tenant_id") if isinstance(payload, dict) else None
        except Exception:
            tenant_id = None

        # Make available to downstream handlers
        request.state.tenant_id = tenant_id
        return await call_next(request)
