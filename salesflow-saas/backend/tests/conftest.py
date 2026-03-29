"""Test fixtures for Dealix backend."""
import asyncio
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.config import get_settings
from app.api.v1.deps import get_db

settings = get_settings()


# Use a separate test database or in-memory approach
TEST_DATABASE_URL = settings.DATABASE_URL


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Async HTTP client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_tenant_id():
    """Generate a unique tenant ID for test isolation."""
    return str(uuid.uuid4())


@pytest.fixture
def auth_headers():
    """Generate JWT auth headers for testing."""
    import jwt
    from app.config import get_settings
    s = get_settings()
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token = jwt.encode(
        {
            "sub": user_id,
            "tenant_id": tenant_id,
            "role": "admin",
            "exp": datetime(2099, 1, 1, tzinfo=timezone.utc),
        },
        s.SECRET_KEY,
        algorithm=s.ALGORITHM,
    )
    return {
        "Authorization": f"Bearer {token}",
        "_tenant_id": tenant_id,
        "_user_id": user_id,
    }
