"""Lead engine — recompute and intel."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_lead_engine_recompute_and_intel():
    suffix = uuid.uuid4().hex[:12]
    email = f"le_{suffix}@dealix.test"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        reg = await ac.post(
            "/api/v1/auth/register",
            json={
                "company_name": f"LE Co {suffix}",
                "company_name_ar": "محرك عروض",
                "full_name": "Owner",
                "email": email,
                "password": "Le_Test_Pass_9",
                "phone": "0500000000",
                "industry": "saas",
            },
        )
        assert reg.status_code == 200, reg.text
        token = reg.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}

        lead = await ac.post(
            "/api/v1/leads",
            headers=h,
            json={
                "name": "Test Clinic",
                "phone": "0501111111",
                "source": "google_maps_hunter",
                "status": "new",
                "metadata": {"city": "Riyadh", "sector": "medical"},
            },
        )
        assert lead.status_code == 201, lead.text
        lid = lead.json()["id"]

        r = await ac.post(f"/api/v1/lead-engine/recompute/{lid}", headers=h)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "score" in body
        assert "priority_band" in body
        assert "motion" in body

        intel = await ac.get(f"/api/v1/lead-engine/intel/{lid}", headers=h)
        assert intel.status_code == 200
        assert intel.json().get("score") == body["score"]
