"""Smoke tests for the company research agent (rules-only, no LLM call)."""

from __future__ import annotations

from auto_client_acquisition.email.research_agent import (
    DEFAULT_BRIEF, SECTOR_BRIEFS, research_company_rules,
)


def test_research_known_sector_real_estate_developer():
    brief = research_company_rules({
        "company_name": "شركة الراجحي العقارية",
        "sector": "real_estate_developer",
        "city": "Riyadh",
        "domain": "alrajhi-real-estate.com",
        "email": "info@alrajhi-real-estate.com",
        "allowed_use": "business_contact_research_only",
        "best_source": "saudi_business_directory",
    })
    assert brief.company_name == "شركة الراجحي العقارية"
    assert "عقاري" in brief.pain_hypothesis or "lead" in brief.pain_hypothesis
    assert brief.best_offer == "pilot_499"
    assert brief.best_channel == "phone_task"
    assert brief.confidence >= 0.6
    assert brief.risk_note == "ok"


def test_research_known_sector_logistics():
    brief = research_company_rules({
        "company_name": "شركة شحن سريعة", "sector": "logistics",
        "phone": "+966500000000",
        "allowed_use": "business_contact_research_only",
    })
    assert "RFQ" in brief.pain_hypothesis or "شحن" in brief.pain_hypothesis
    assert brief.best_offer == "pilot_999"


def test_research_unknown_sector_falls_back_to_default():
    brief = research_company_rules({
        "company_name": "شركة غير معروفة",
        "sector": "made_up_sector_xyz",
        "phone": "+966500000000",
        "allowed_use": "business_contact_research_only",
    })
    assert brief.confidence < 0.6  # lower confidence on default
    assert brief.best_offer == DEFAULT_BRIEF["best_offer"]


def test_research_high_risk_flags_in_risk_note():
    brief = research_company_rules({
        "company_name": "شركة ما", "sector": "real_estate",
        "risk_level": "high",
        "phone": "+966500000000",
        "allowed_use": "business_contact_research_only",
    })
    assert "high_risk" in brief.risk_note


def test_research_missing_allowed_use_flags():
    brief = research_company_rules({
        "company_name": "شركة ما", "sector": "real_estate",
        "phone": "+966500000000",
        # allowed_use missing
    })
    assert "allowed_use_missing" in brief.risk_note


def test_research_no_business_contact_flags():
    brief = research_company_rules({
        "company_name": "شركة ما", "sector": "real_estate",
        "allowed_use": "business_contact_research_only",
        # no email or phone
    })
    assert "no_business_contact" in brief.risk_note


def test_all_sector_briefs_have_required_keys():
    """Every sector brief must have all 7 keys for the email generator."""
    required = {"brief", "pain", "fit", "gain", "objections",
                "first_sentence", "best_offer", "best_channel"}
    for sector, tpl in SECTOR_BRIEFS.items():
        missing = required - set(tpl.keys())
        assert not missing, f"{sector} missing: {missing}"


def test_research_includes_sources_used():
    brief = research_company_rules({
        "company_name": "شركة ما", "sector": "real_estate",
        "domain": "example.sa", "best_source": "saudi_business_directory",
        "google_place_id": "ChIJxxx",
        "phone": "+966500000000",
        "allowed_use": "business_contact_research_only",
    })
    assert any("directory" in s for s in brief.sources_used)
    assert any("google_places" in s for s in brief.sources_used)
    assert any("website" in s for s in brief.sources_used)


def test_research_marketing_agency_offers_partnership():
    brief = research_company_rules({
        "company_name": "وكالة تسويق", "sector": "marketing_agency",
        "email": "info@agency.sa",
        "allowed_use": "business_contact_research_only",
    })
    assert brief.best_offer == "partnership"
    assert "MRR" in brief.dealix_fit or "resell" in brief.dealix_fit
