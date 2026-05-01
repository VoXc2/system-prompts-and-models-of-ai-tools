"""Unit tests for the Intake agent."""

from __future__ import annotations

import pytest

from auto_client_acquisition.agents.intake import IntakeAgent, LeadSource, LeadStatus


@pytest.mark.asyncio
async def test_intake_arabic_detection():
    agent = IntakeAgent()
    lead = await agent.run(
        payload={
            "company": "شركة الرياض",
            "name": "محمد",
            "message": "نحتاج نظام AI لإدارة العملاء",
        },
        source=LeadSource.WEBSITE,
    )
    assert lead.locale == "ar"
    assert lead.status == LeadStatus.NEW
    assert lead.id.startswith("intake_") or lead.id.startswith("lead_")


@pytest.mark.asyncio
async def test_intake_phone_normalization():
    agent = IntakeAgent()
    lead = await agent.run(
        payload={
            "company": "Test Co",
            "name": "Jane",
            "phone": "0501234567",
        },
        source=LeadSource.WEBSITE,
    )
    assert lead.contact_phone == "+966501234567"


@pytest.mark.asyncio
async def test_intake_email_normalization():
    agent = IntakeAgent()
    lead = await agent.run(
        payload={
            "company": "Test Co",
            "name": "Jane",
            "email": "  JANE@Example.COM  ",
        },
        source=LeadSource.WEBSITE,
    )
    assert lead.contact_email == "jane@example.com"


@pytest.mark.asyncio
async def test_intake_dedup_hash_populated():
    agent = IntakeAgent()
    payload = {"company": "Same Co", "name": "A", "email": "a@b.com"}
    lead1 = await agent.run(payload=payload, source=LeadSource.WEBSITE)
    lead2 = await agent.run(payload=payload, source=LeadSource.WEBSITE)
    assert lead1.dedup_hash == lead2.dedup_hash
    assert lead2.metadata["is_duplicate"] is True
