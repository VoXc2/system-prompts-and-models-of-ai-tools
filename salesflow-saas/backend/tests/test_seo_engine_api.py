"""SEO engine API — auth + tenant scope."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_seo_engine_runs_for_owner():
    suffix = uuid.uuid4().hex[:12]
    email = f"seo_{suffix}@dealix.test"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        reg = await ac.post(
            "/api/v1/auth/register",
            json={
                "company_name": f"SEO Co {suffix}",
                "company_name_ar": "شركة سيو",
                "full_name": "Owner",
                "email": email,
                "password": "Seo_Test_Pass_9",
                "phone": "0500000000",
                "industry": "saas",
            },
        )
        assert reg.status_code == 200, reg.text
        token = reg.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}

        r = await ac.post(
            "/api/v1/seo-engine/runs",
            headers=h,
            json={"run_kind": "technical_audit", "options": {}},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("status") in ("completed", "failed")
        assert "run_id" in body

        lst = await ac.get("/api/v1/seo-engine/runs", headers=h)
        assert lst.status_code == 200
        assert len(lst.json().get("runs", [])) >= 1
