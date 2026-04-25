"""Tests for the full automation outreach system — drafts, pipeline, followups."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def app():
    app = FastAPI()
    from app.api.v1.automation import router as auto_router
    app.include_router(auto_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_email_generate(client):
    resp = client.post("/automation/email/generate", json={
        "company": "Foodics",
        "sector": "saas",
        "city": "الرياض",
        "contact_name": "أحمد",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "subject_ar" in data
    assert "body_ar" in data
    assert "followup_day_2" in data
    assert "followup_day_5" in data
    assert "call_script_ar" in data
    assert "linkedin_manual_message" in data
    assert data["opt_out_included"] is True
    assert data["word_count"] > 0
    assert "Foodics" in data["subject_ar"]


def test_email_generate_with_signals(client):
    resp = client.post("/automation/email/generate", json={
        "company": "TestCo",
        "sector": "real_estate",
        "signals": ["hubspot"],
    })
    data = resp.json()
    assert "HubSpot" in data["body_ar"]


def test_compliance_check_allowed(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "ahmed@company.sa",
        "company": "TestCo",
        "source": "linkedin",
    })
    data = resp.json()
    assert data["allowed"] is True
    assert data["reason"] == "compliant"


def test_compliance_check_opt_out(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "ahmed@company.sa",
        "opt_out": True,
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "opt_out"


def test_compliance_check_bounced(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "bad@company.sa",
        "bounced_before": True,
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "bounced_before"


def test_compliance_check_high_risk(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "ceo@big.sa",
        "risk_score": 80,
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "high_risk"


def test_compliance_check_personal_email(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "ahmed@gmail.com",
        "source": "linkedin",
    })
    data = resp.json()
    assert data["allowed"] is True
    assert "personal_email" in data["reason"]


def test_compliance_check_no_source(client):
    resp = client.post("/automation/compliance/check", json={
        "email": "ahmed@company.sa",
        "source": "",
    })
    data = resp.json()
    assert data["allowed"] is False
    assert data["reason"] == "no_source"


def test_reply_classify_interested(client):
    resp = client.post("/automation/reply/classify", json={
        "reply_text": "مهتم جداً، أبي أجرب",
        "company": "TestCo",
    })
    data = resp.json()
    assert data["category"] == "interested"
    assert data["auto_reply_allowed"] is True
    assert "calendly" in data["suggested_response"].lower() or "demo" in data["suggested_response"].lower() or "20 دقيقة" in data["suggested_response"]


def test_reply_classify_price(client):
    resp = client.post("/automation/reply/classify", json={
        "reply_text": "كم السعر؟",
    })
    data = resp.json()
    assert data["category"] == "ask_price"
    assert "499" in data["suggested_response"]


def test_reply_classify_unsubscribe(client):
    resp = client.post("/automation/reply/classify", json={
        "reply_text": "إيقاف لا تتواصل معي",
    })
    data = resp.json()
    assert data["category"] == "unsubscribe"
    assert data["auto_reply_allowed"] is False


def test_reply_classify_crm(client):
    resp = client.post("/automation/reply/classify", json={
        "reply_text": "عندنا CRM وما نحتاج نظام ثاني",
    })
    data = resp.json()
    assert data["category"] == "already_has_crm"
    assert "طبقة" in data["suggested_response"] or "CRM" in data["suggested_response"]


def test_daily_targeting_generate(client):
    resp = client.post("/automation/daily-targeting/generate", json={
        "sectors": ["real_estate", "construction"],
        "cities": ["الرياض"],
        "daily_target_count": 5,
    })
    data = resp.json()
    assert data["total_generated"] > 0
    assert len(data["targets"]) <= 5
    assert data["targets"][0]["sector"] in ("real_estate", "construction")
    assert data["approval_required"] is True


def test_sector_pain_map_coverage(client):
    """Verify all 9 sectors produce valid emails."""
    sectors = ["real_estate", "construction", "hospitality", "food_beverage",
               "logistics", "agency", "saas", "healthcare", "education"]
    for sector in sectors:
        resp = client.post("/automation/email/generate", json={
            "company": f"Test_{sector}",
            "sector": sector,
        })
        assert resp.status_code == 200, f"Failed for sector: {sector}"
        data = resp.json()
        assert len(data["body_ar"]) > 50, f"Empty body for {sector}"
        assert "إيقاف" in data["body_ar"], f"Missing opt-out for {sector}"
