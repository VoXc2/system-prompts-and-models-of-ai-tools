import asyncio
import os
import sys
from pathlib import Path

# JWT-based API tests require this gate to be off (production may set .env).
os.environ["DEALIX_INTERNAL_API_TOKEN"] = ""

# Ensure backend package imports work whether pytest is run from repo root or backend/.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _init_database():
    from app.database import init_db

    asyncio.run(init_db())


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
