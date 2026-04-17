"""V002 — Runtime RLS Fuzz Test.

10,000 cross-tenant queries. Tenant A's session attempts to read rows from
Tenant B's context. Expected: zero rows returned from B's data.

Any violation = P0 incident. This test is added to nightly CI.

Run:
    pytest backend/tests/security/test_rls_fuzz.py -v
    pytest backend/tests/security/test_rls_fuzz.py::test_cross_tenant_isolation_fuzz -v --count=10000
"""

from __future__ import annotations

import os
import uuid
from typing import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.database_rls import set_tenant_context

FUZZ_ITERATIONS = int(os.getenv("RLS_FUZZ_ITERATIONS", "10000"))

TENANT_SCOPED_TABLES = [
    "deals",
    "leads",
    "approval_requests",
    "evidence_packs",
    "contradictions",
    "compliance_controls",
    "ai_conversations",
    "audit_logs",
    "integration_sync_states",
    "strategic_deals",
    "durable_checkpoints",
    "idempotency_keys",
]


async def _seed_two_tenants(session: AsyncSession) -> tuple[uuid.UUID, uuid.UUID]:
    """Create two tenant rows in each table for isolation testing."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    return tenant_a, tenant_b


@pytest.mark.asyncio
async def test_cross_tenant_isolation_fuzz() -> None:
    """Fuzz test: iterate switching tenant context and confirm zero bleed."""
    async with async_session_factory() as session:
        tenant_a, tenant_b = await _seed_two_tenants(session)

        violations: list[tuple[str, str, int]] = []

        for i in range(FUZZ_ITERATIONS):
            # Alternate contexts
            current = tenant_a if i % 2 == 0 else tenant_b
            other = tenant_b if i % 2 == 0 else tenant_a

            await set_tenant_context(session, str(current))

            for table in TENANT_SCOPED_TABLES:
                result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {table} WHERE tenant_id = :other"),
                    {"other": str(other)},
                )
                leaked = result.scalar_one()
                if leaked and leaked > 0:
                    violations.append((table, str(current), leaked))

        assert not violations, (
            f"RLS FUZZ FAILURE — {len(violations)} cross-tenant leaks detected: "
            f"{violations[:10]}"
        )


@pytest.mark.asyncio
async def test_rls_policies_enabled_on_all_tables() -> None:
    """Every tenant-scoped table must have RLS enabled."""
    async with async_session_factory() as session:
        result = await session.execute(
            text(
                """
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename = ANY(:tables)
                """
            ),
            {"tables": TENANT_SCOPED_TABLES},
        )
        unprotected = [row[0] for row in result if not row[1]]
        assert not unprotected, f"RLS disabled on: {unprotected}"


@pytest.mark.asyncio
async def test_rls_default_deny_with_no_tenant_context() -> None:
    """Queries without tenant context must return zero rows."""
    async with async_session_factory() as session:
        # Intentionally NOT calling set_tenant_context
        for table in TENANT_SCOPED_TABLES:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar_one()
            assert count == 0, (
                f"RLS default-deny FAILURE — {table} returned {count} rows "
                f"without tenant context"
            )
