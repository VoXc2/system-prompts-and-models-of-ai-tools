"""Unit tests for the Connector Catalog."""

from __future__ import annotations

from auto_client_acquisition.connector_catalog import (
    ALL_CONNECTORS,
    all_risks,
    catalog_summary,
    connector_risks,
    connector_status,
    get_connector,
    list_connectors,
)


def test_catalog_has_at_least_12_connectors():
    out = list_connectors()
    assert out["total"] >= 12


def test_catalog_includes_critical_connectors():
    keys = {c.key for c in ALL_CONNECTORS}
    for required in (
        "whatsapp_cloud", "gmail", "google_calendar", "moyasar",
        "linkedin_lead_forms", "google_business_profile",
        "x_api", "instagram_graph", "google_sheets",
        "crm_generic", "website_forms", "google_meet",
    ):
        assert required in keys


def test_every_connector_has_risk_level():
    for c in ALL_CONNECTORS:
        assert c.risk_level in ("low", "medium", "high")


def test_every_connector_has_blocked_or_safe_actions():
    for c in ALL_CONNECTORS:
        assert isinstance(c.allowed_actions, tuple)
        assert isinstance(c.blocked_actions, tuple)


def test_whatsapp_blocks_cold_send():
    wa = get_connector("whatsapp_cloud")
    assert wa is not None
    assert "cold_send_without_consent" in wa.blocked_actions


def test_moyasar_blocks_card_storage():
    m = get_connector("moyasar")
    assert m is not None
    assert "store_card_number" in m.blocked_actions


def test_summary_aggregates():
    s = catalog_summary()
    assert s["total"] == len(ALL_CONNECTORS)
    assert "by_launch_phase" in s
    assert "by_risk_level" in s


def test_status_returns_safe_default_modes():
    out = connector_status()
    for entry in out["statuses"]:
        assert entry["mode"] in ("connected_draft_only", "not_connected",
                                 "connected_live_with_approval")


def test_risks_present_for_high_risk_connectors():
    for key in ("whatsapp_cloud", "moyasar", "google_meet"):
        risks = connector_risks(key)
        assert risks, f"missing risks for {key}"


def test_unknown_connector_has_no_risks():
    assert connector_risks("totally_unknown") == []


def test_all_risks_keyed_by_connector():
    out = all_risks()
    for c in ALL_CONNECTORS:
        assert c.key in out
