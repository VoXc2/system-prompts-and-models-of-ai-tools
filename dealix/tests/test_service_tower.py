"""Tests for Service Tower — catalog, wizard, pricing, CEO cards."""

from __future__ import annotations

from auto_client_acquisition.service_tower.contract_templates import list_contract_templates
from auto_client_acquisition.service_tower.pricing_engine import quote_service
from auto_client_acquisition.service_tower.service_catalog import get_service_by_id, list_tower_services
from auto_client_acquisition.service_tower.service_wizard import recommend_service, start_service
from auto_client_acquisition.service_tower.upgrade_paths import build_all_upgrade_paths
from auto_client_acquisition.service_tower.vertical_service_map import build_vertical_service_map
from auto_client_acquisition.service_tower.whatsapp_ceo_control import build_ceo_daily_service_brief


def test_tower_catalog_has_all_services_with_pricing_or_free() -> None:
    data = list_tower_services()
    services = data.get("services") or []
    assert len(services) >= 10
    for s in services:
        pr = s.get("pricing_range_sar") or {}
        assert "min" in pr and "max" in pr
        assert s.get("approval_policy")
        assert s.get("proof_metrics")


def test_wizard_recommends_list_intelligence_for_uploaded_list() -> None:
    r = recommend_service("b2b_saas", goal="clean my csv list", has_contact_list=True)
    assert r["recommended_service_id"] == "list_intelligence"


def test_wizard_recommends_agency_program_for_agency() -> None:
    r = recommend_service("marketing agency", goal="get clients", has_contact_list=False)
    assert r["recommended_service_id"] == "agency_partner_program"


def test_quote_returns_range() -> None:
    q = quote_service("growth_os", company_size="smb", urgency="normal", channels_count=2)
    assert q.get("ok") is True
    r = q.get("quoted_range_sar") or {}
    assert int(r["min"]) >= 2999


def test_start_never_live_send() -> None:
    out = start_service(
        "first_10_opportunities",
        {"sector": "training", "city": "Riyadh", "offer": "pilot", "goal": "meetings"},
    )
    assert out.get("live_send") is False
    assert out.get("approval_required") is True


def test_ceo_cards_max_three_buttons() -> None:
    brief = build_ceo_daily_service_brief()
    for c in brief.get("cards") or []:
        assert len(c.get("buttons") or []) <= 3


def test_growth_os_has_required_integrations() -> None:
    svc = get_service_by_id("growth_os")
    assert svc
    assert "gmail" in (svc.get("required_integrations") or [])


def test_vertical_map_three_doors() -> None:
    m = build_vertical_service_map()
    assert len(m.get("doors") or []) == 3


def test_upgrade_paths_lists_services() -> None:
    p = build_all_upgrade_paths()
    assert len(p.get("paths") or []) >= 10


def test_contract_templates_require_legal_review() -> None:
    t = list_contract_templates()
    for x in t.get("templates") or []:
        assert x.get("legal_review_required") is True
        assert x.get("not_legal_advice") is True
