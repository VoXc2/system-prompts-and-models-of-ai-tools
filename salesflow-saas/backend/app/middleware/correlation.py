"""Correlation ID middleware for request tracing."""
import uuid
import logging
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Adds X-Request-ID to every request/response for distributed tracing."""

    async def dispatch(self, request: Request, call_next):
        # Use existing header or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        correlation_id_var.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class CorrelationFilter(logging.Filter):
    """Logging filter that adds correlation_id to log records."""

    def filter(self, record):
        record.correlation_id = correlation_id_var.get("")
        return True
