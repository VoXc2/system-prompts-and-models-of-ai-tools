from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _register_and_get_token() -> str:
    suffix = uuid.uuid4().hex[:12]
    email = f"gov_{suffix}@dealix.test"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        reg = await ac.post(
            "/api/v1/auth/register",
            json={
                "company_name": f"Gov Test {suffix}",
                "full_name": "Gov Owner",
                "email": email,
                "password": "Gov_Test_9876",
            },
        )
        assert reg.status_code == 200, reg.text
        return reg.json()["access_token"]


@pytest.mark.asyncio
async def test_approval_create_enriches_governance_contract():
    token = await _register_and_get_token()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resource_id = str(uuid.uuid4())
        create = await ac.post(
            "/api/v1/operations/approvals",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "whatsapp",
                "resource_type": "term_sheet",
                "resource_id": resource_id,
                "payload": {"counterparty": "Partner X"},
                "evidence_refs": [{"type": "memo", "ref": "memo://term-sheet/001", "title": "Term Sheet Brief"}],
            },
        )
        assert create.status_code == 200, create.text
        body = create.json()
        assert body["governance"]["approval_class"] in ("executive", "board")
        assert body["governance"]["reversibility_class"] in ("R1", "R2", "R3")
        assert body["policy"]["requires_approval"] is True
        assert body["trace"]["trace_id"].startswith("trace_")

        listed = await ac.get(
            "/api/v1/operations/approvals",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert listed.status_code == 200
        items = listed.json()["items"]
        assert len(items) >= 1
        row = items[0]
        assert row["governance"]["plane"] in ("decision", "execution", "trust", "data", "operating")
        assert row["requires_human_approval"] is True
        assert len(row["evidence_refs"]) >= 1


@pytest.mark.asyncio
async def test_approval_create_blocks_forbidden_policy_action():
    token = await _register_and_get_token()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        blocked = await ac.post(
            "/api/v1/operations/approvals",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "channel": "email",
                "resource_type": "security_control",
                "resource_id": str(uuid.uuid4()),
                "action": "exfiltrate_secrets",
                "payload": {"note": "should never pass"},
            },
        )
        assert blocked.status_code == 422
        detail = blocked.json()["detail"]
        assert detail["policy"]["allowed"] is False
        assert detail["policy"]["class"] == "C"


@pytest.mark.asyncio
async def test_executive_control_center_returns_live_surface_matrix():
    token = await _register_and_get_token()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(
            "/api/v1/operations/executive-control-center",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["demo_mode"] is False
        assert "decision_plane" in body
        assert "trust_plane" in body
        assert "policy_violations_board" in body
        assert "live_surfaces" in body
        assert len(body["live_surfaces"]) >= 10
        assert body["live_surfaces_total"] == len(body["live_surfaces"])
