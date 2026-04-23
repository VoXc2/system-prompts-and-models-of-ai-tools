"""Idempotency Middleware — checks Idempotency-Key header on POST/PUT.

If key exists, returns cached response (no side effects).
Otherwise, stores response after successful execution.
"""

from __future__ import annotations

import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


IDEMPOTENT_METHODS = {"POST", "PUT", "PATCH"}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware: idempotent retry support via Idempotency-Key header.

    Behavior:
    - GET/DELETE: pass through (naturally idempotent)
    - POST/PUT/PATCH without header: pass through (caller opted out)
    - POST/PUT/PATCH with header + key found: return cached response
    - POST/PUT/PATCH with header + key new: execute, cache response
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in IDEMPOTENT_METHODS:
            return await call_next(request)

        key = request.headers.get("idempotency-key")
        if not key:
            return await call_next(request)

        # Lookup cached response
        try:
            from app.database import async_session
            from app.services.idempotency_service import idempotency_service

            tenant_id = getattr(request.state, "tenant_id", None) or ""

            async with async_session() as db:
                cached = await idempotency_service.get_existing(
                    db, key=key, tenant_id=str(tenant_id)
                )
                if cached:
                    return JSONResponse(
                        cached["response"],
                        status_code=int(cached["status_code"]),
                        headers={"X-Idempotency-Cached": "true"},
                    )
        except Exception:
            # If lookup fails, fall through to normal execution
            pass

        # Execute request
        response = await call_next(request)

        # Cache response if successful
        try:
            if 200 <= response.status_code < 300:
                from app.database import async_session
                from app.services.idempotency_service import idempotency_service

                tenant_id = getattr(request.state, "tenant_id", None) or ""

                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                response_data = json.loads(body) if body else {}
                async with async_session() as db:
                    try:
                        await idempotency_service.store(
                            db, key=key, tenant_id=str(tenant_id),
                            endpoint=str(request.url.path),
                            request_body=None,
                            response=response_data,
                            status_code=response.status_code,
                        )
                    except Exception:
                        pass

                return JSONResponse(
                    response_data, status_code=response.status_code,
                    headers={"X-Idempotency-Stored": "true"},
                )
        except Exception:
            pass

        return response
