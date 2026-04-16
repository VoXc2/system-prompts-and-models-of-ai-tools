"""Sovereign OS snapshot endpoint — structured enterprise command center."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.api.deps import get_current_user
from app.database import async_session
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User


@pytest_asyncio.fixture
async def sovereign_user():
    suffix = uuid.uuid4().hex[:10]
    async with async_session() as db:
        tenant = Tenant(
            name=f"Sovereign Co {suffix}",
            slug=f"sov-{suffix}",
            email=f"sov-{suffix}@example.com",
        )
        db.add(tenant)
        await db.flush()
        stub_hash = "$2b$12$dummyNotForLoginxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        user = User(
            tenant_id=tenant.id,
            email=f"sov-user-{suffix}@example.com",
            password_hash=stub_hash,
            full_name="Sovereign User",
            role="owner",
        )
        db.add(user)
        await db.commit()
        uid = str(user.id)
    return uid


def _override_user(user_id: str):
    async def _dep():
        async with async_session() as db:
            return (await db.execute(select(User).where(User.id == user_id))).scalar_one()

    return _dep


@pytest.mark.asyncio
async def test_sovereign_os_snapshot_schema(sovereign_user):
    transport = ASGITransport(app=app)
    app.dependency_overrides[get_current_user] = _override_user(sovereign_user)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get("/api/v1/sovereign-os/snapshot", headers={"X-Correlation-ID": "test-cid-1"})
            assert r.status_code == 200
            body = r.json()
            assert body.get("correlation_id") == "test-cid-1"
            assert "sales_os" in body
            assert body["sales_os"]["total_leads"] >= 0
            assert "partnership" in body and "ma_corp_dev" in body
            assert "planes" in body and isinstance(body["planes"], list)
            assert "model_routing_fabric" in body
            assert len(body["model_routing_fabric"]) >= 1
    finally:
        app.dependency_overrides.pop(get_current_user, None)
