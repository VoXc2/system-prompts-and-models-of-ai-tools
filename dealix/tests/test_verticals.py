"""Vertical playbooks."""

from __future__ import annotations

from auto_client_acquisition.business.verticals import get_vertical_playbooks, recommend_vertical, vertical_roi_metric


def test_verticals_include_key_sectors():
    v = get_vertical_playbooks()["verticals"]
    for key in ("clinics", "real_estate", "logistics", "agencies"):
        assert key in v
        assert "pain_ar" in v[key]
        assert "buyer" in v[key]


def test_recommend_vertical():
    r = recommend_vertical(industry="عيادة", city="Riyadh", goal="x")
    assert r["recommended_vertical"] == "clinics"


def test_vertical_roi_metric():
    assert vertical_roi_metric("clinics")
