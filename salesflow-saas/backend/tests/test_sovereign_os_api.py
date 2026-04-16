import pytest


@pytest.mark.asyncio
async def test_sovereign_control_center_demo_snapshot(client):
    response = await client.get("/api/v1/sovereign-os/control-center")
    assert response.status_code == 200

    payload = response.json()
    assert payload["runtime"]["demo_mode"] is True
    assert len(payload["planes"]) == 5
    assert payload["readiness_score_percent"] >= 0


@pytest.mark.asyncio
async def test_evaluate_auto_action(client):
    response = await client.post(
        "/api/v1/sovereign-os/governed-actions/evaluate",
        json={"action_key": "lead_capture"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["resolved_execution_mode"] == "auto"
    assert payload["can_execute_now"] is True
    assert payload["requires_approval"] is False


@pytest.mark.asyncio
async def test_evaluate_approval_required_action_blocks_without_ticket(client):
    response = await client.post(
        "/api/v1/sovereign-os/governed-actions/evaluate",
        json={"action_key": "send_mna_offer"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["resolved_execution_mode"] == "auto_with_approval"
    assert payload["requires_approval"] is True
    assert payload["can_execute_now"] is False
    assert "approval_ticket_missing" in payload["blockers"]


@pytest.mark.asyncio
async def test_evaluate_approval_required_action_allows_with_ticket(client):
    response = await client.post(
        "/api/v1/sovereign-os/governed-actions/evaluate",
        json={"action_key": "send_mna_offer", "approval_ticket_id": "APR-77"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["resolved_execution_mode"] == "auto_with_approval"
    assert payload["can_execute_now"] is True
    assert payload["blockers"] == []


@pytest.mark.asyncio
async def test_readiness_definition_shape(client):
    response = await client.get("/api/v1/sovereign-os/readiness-definition")
    assert response.status_code == 200

    payload = response.json()
    assert payload["criteria_count"] >= 8
    assert payload["surface_count"] >= 18
