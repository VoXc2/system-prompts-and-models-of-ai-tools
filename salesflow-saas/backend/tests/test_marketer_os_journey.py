"""
رحلة «نظام المسوّق» — تسجيل شريك، تكرار البريد، تفعيل، صفقات، خطة غير صالحة، وترقية employed عند 10 صفقات.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _affiliate_body(suffix: str) -> dict:
    return {
        "full_name": f"مسوّق تجربة {suffix}",
        "full_name_ar": f"مسوّق تجربة {suffix}",
        "email": f"aff_os_{suffix}@dealix.marketer.test",
        "phone": "0509988776",
        "whatsapp": "0509988776",
        "city": "الرياض",
        "national_id": "1234567890",
    }


@pytest.mark.asyncio
async def test_marketer_os_register_activate_deal_and_duplicate_email():
    suffix = uuid.uuid4().hex[:12]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        body = _affiliate_body(suffix)
        reg = await ac.post("/api/v1/affiliates/register", json=body)
        assert reg.status_code == 201, reg.text
        a = reg.json()
        assert a["email"] == body["email"]
        assert a["status"] == "pending"
        assert a["referral_code"].startswith("DLX-")
        aid = a["id"]

        dup = await ac.post("/api/v1/affiliates/register", json=body)
        assert dup.status_code == 400
        assert "Email" in dup.json().get("detail", "") or "email" in dup.json().get("detail", "").lower()

        act = await ac.post(f"/api/v1/affiliates/{aid}/activate")
        assert act.status_code == 200
        assert act.json()["status"] == "active"

        deal = await ac.post(
            f"/api/v1/affiliates/{aid}/deals",
            json={"client_company": "شركة النمو التجريبية", "plan_type": "professional"},
        )
        assert deal.status_code == 201
        dj = deal.json()
        assert "commission" in dj
        assert dj["commission"] > 0

        bad_plan = await ac.post(
            f"/api/v1/affiliates/{aid}/deals",
            json={"client_company": "عميل آخر", "plan_type": "platinum"},
        )
        assert bad_plan.status_code == 400

        g = await ac.get(f"/api/v1/affiliates/{aid}")
        assert g.status_code == 200
        assert g.json()["total_deals_closed"] >= 1


@pytest.mark.asyncio
async def test_marketer_os_auto_employ_after_ten_deals():
    suffix = uuid.uuid4().hex[:12]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        body = _affiliate_body(f"emp_{suffix}")
        body["email"] = f"aff_emp_{suffix}@dealix.marketer.test"
        reg = await ac.post("/api/v1/affiliates/register", json=body)
        assert reg.status_code == 201
        aid = reg.json()["id"]

        await ac.post(f"/api/v1/affiliates/{aid}/activate")
        for i in range(10):
            r = await ac.post(
                f"/api/v1/affiliates/{aid}/deals",
                json={"client_company": f"عميل {i}", "plan_type": "basic"},
            )
            assert r.status_code == 201, r.text

        g = await ac.get(f"/api/v1/affiliates/{aid}")
        assert g.status_code == 200
        assert g.json()["status"] == "employed"
        assert g.json()["total_deals_closed"] == 10
