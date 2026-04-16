import uuid

import pytest


@pytest.mark.asyncio
async def test_sovereign_public_snapshot(client):
    r = await client.get("/api/v1/sovereign/snapshot")
    assert r.status_code == 200
    data = r.json()
    assert data.get("demo_mode") is True
    assert data.get("surfaces")
    assert data.get("contracts")


@pytest.mark.asyncio
async def test_sovereign_approval_commitment_and_ledger_flow(client):
    suffix = uuid.uuid4().hex[:12]
    email = f"sovereign_{suffix}@dealix.test"
    password = "Sovereign_Pass_123"

    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "company_name": f"Sovereign Co {suffix}",
            "company_name_ar": "شركة سيادية",
            "full_name": "Owner Sovereign",
            "email": email,
            "password": password,
            "phone": "0500001111",
            "industry": "saas",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    approval_payload = {
        "domain": "sales",
        "decision_type": "non_standard_discount",
        "approval_class": "A2",
        "reversibility_class": "R2",
        "sensitivity_class": "S2",
        "policy_refs": ["policy.sales.discount", "policy.pdpl.consent"],
        "evidence_pack_id": f"evp-{suffix}",
        "requested_by": "Owner Sovereign",
        "notes": "Needs management review",
    }
    create_approval = await client.post(
        "/api/v1/sovereign/approvals",
        headers=headers,
        json=approval_payload,
    )
    assert create_approval.status_code == 200
    approval_id = create_approval.json()["approval_request_id"]

    approvals = await client.get("/api/v1/sovereign/approvals", headers=headers)
    assert approvals.status_code == 200
    assert approvals.json()["count"] >= 1

    resolve = await client.put(
        f"/api/v1/sovereign/approvals/{approval_id}",
        headers=headers,
        json={"approve": True, "note": "Approved by owner"},
    )
    assert resolve.status_code == 200
    assert resolve.json()["status"] == "approved"

    commitment_payload = {
        "domain": "expansion",
        "workflow_type": "canary_launch",
        "state": "queued",
        "owner": "ops-owner",
        "sla_hours": 8,
        "requires_durable_runtime": True,
        "approval_request_id": approval_id,
        "policy_refs": ["policy.release.gate"],
        "evidence_pack_id": f"evp-{suffix}",
    }
    create_commitment = await client.post(
        "/api/v1/sovereign/workflow-commitments",
        headers=headers,
        json=commitment_payload,
    )
    assert create_commitment.status_code == 200
    commitment_id = create_commitment.json()["workflow_commitment_id"]

    commitments = await client.get("/api/v1/sovereign/workflow-commitments", headers=headers)
    assert commitments.status_code == 200
    assert commitments.json()["count"] >= 1
    assert any(
        item["workflow_commitment_id"] == commitment_id
        for item in commitments.json()["items"]
    )

    ledger_payload = {
        "tool_name": "send_email",
        "tool_operation": "proposal_send",
        "execution_status": "success",
        "policy_decision": "needs_approval",
        "policy_refs": ["policy.sales.discount"],
        "approval_request_id": approval_id,
        "input_hash": "a" * 32,
        "output_hash": "b" * 32,
        "evidence_pack_id": f"evp-{suffix}",
    }
    create_receipt = await client.post(
        "/api/v1/sovereign/tool-verification-ledger",
        headers=headers,
        json=ledger_payload,
    )
    assert create_receipt.status_code == 200
    receipt_id = create_receipt.json()["receipt_id"]
    assert receipt_id

    ledger = await client.get("/api/v1/sovereign/tool-verification-ledger", headers=headers)
    assert ledger.status_code == 200
    assert ledger.json()["count"] >= 1
    assert any(item["receipt_id"] == receipt_id for item in ledger.json()["items"])
