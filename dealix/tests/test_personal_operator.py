"""Personal Operator unit + API smoke tests."""

from __future__ import annotations

import pytest

from auto_client_acquisition.personal_operator import ApprovalDecision, default_sami_profile, suggest_opportunities
from auto_client_acquisition.personal_operator.operator import apply_decision, build_daily_brief, draft_intro_message


def test_daily_brief_arabic_greeting():
    brief = build_daily_brief(default_sami_profile())
    assert brief.greeting.startswith("صباح الخير")
    data = brief.to_dict()
    assert "generated_at" in data
    assert data["top_decisions"]


def test_opportunities_have_actions():
    first = suggest_opportunities()[0]
    card = first.to_card()
    assert "actions" in card
    assert set(card["actions"].keys()) >= {"accept", "skip", "draft", "schedule", "needs_research"}
    assert len(card["action_buttons"]) <= 3


def test_decision_accept_returns_draft_next():
    opp = suggest_opportunities()[0]
    result = apply_decision(opp, ApprovalDecision.ACCEPT)
    assert result["next_action"] == "draft_message"
    assert result.get("approval_required") is True


def test_decision_skip_returns_skipped():
    opp = suggest_opportunities()[0]
    result = apply_decision(opp, ApprovalDecision.SKIP)
    assert result["status"] == "skipped"


def test_draft_message_approval_required():
    opp = suggest_opportunities()[0]
    msg = draft_intro_message(opp)
    assert msg["approval_required"] is True
    assert "body_ar" in msg


@pytest.mark.asyncio
async def test_launch_readiness_has_score(async_client):
    r = await async_client.get("/api/v1/personal-operator/launch-readiness")
    assert r.status_code == 200
    body = r.json()
    assert "score" in body
    assert "checks" in body


@pytest.mark.asyncio
async def test_launch_report_endpoint(async_client):
    r = await async_client.get("/api/v1/personal-operator/launch-report")
    assert r.status_code == 200
    data = r.json()
    assert data["overall_score"] >= 0
    assert len(data["areas"]) == 15


@pytest.mark.asyncio
async def test_project_ask_semantic_notice(async_client):
    r = await async_client.post(
        "/api/v1/personal-operator/project/ask",
        json={"question": "وش ناقص المشروع؟"},
    )
    assert r.status_code == 200
    j = r.json()
    assert "semantic_status_ar" in j
    assert "غير متصل" in j["semantic_status_ar"] or "not connected" in j["semantic_status_ar"].lower()


@pytest.mark.asyncio
async def test_invalid_decision_400(async_client):
    opp_id = suggest_opportunities()[0].id
    r = await async_client.post(
        f"/api/v1/personal-operator/opportunities/{opp_id}/decision",
        json={"decision": "not_a_real_decision"},
    )
    assert r.status_code == 400
