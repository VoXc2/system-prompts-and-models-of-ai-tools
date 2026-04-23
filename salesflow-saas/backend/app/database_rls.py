"""Tenant context helpers for PostgreSQL Row-Level Security (RLS).

When RLS policies are enabled, each session must set:
    SET LOCAL app.tenant_id = '<tenant-uuid>'

This must happen before any tenant-scoped query in the session.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, tenant_id: str | UUID | None) -> None:
    """Set RLS tenant context for the current session.

    Call at the start of every request handler that touches tenant-scoped data.
    Uses SET LOCAL so it only affects the current transaction.
    """
    if tenant_id is None:
        # default-deny: no tenant context = no rows returned
        await session.execute(text("SET LOCAL app.tenant_id = ''"))
        return

    tid = str(tenant_id)
    # Sanitize: only valid UUID format allowed
    try:
        UUID(tid)
    except (ValueError, TypeError):
        await session.execute(text("SET LOCAL app.tenant_id = ''"))
        return

    await session.execute(text(f"SET LOCAL app.tenant_id = '{tid}'"))


async def clear_tenant_context(session: AsyncSession) -> None:
    """Clear tenant context (forces default-deny on subsequent queries)."""
    await session.execute(text("SET LOCAL app.tenant_id = ''"))


async def get_current_tenant(session: AsyncSession) -> Optional[str]:
    """Get current tenant_id from session context."""
    result = await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
    val = result.scalar()
    return val if val else None
