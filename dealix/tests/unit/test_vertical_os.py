"""Smoke tests for the Vertical OS layer."""

from __future__ import annotations

import auto_client_acquisition.vertical_os.clinics  # noqa: F401  (registers)
import auto_client_acquisition.vertical_os.logistics  # noqa: F401
import auto_client_acquisition.vertical_os.real_estate  # noqa: F401
from auto_client_acquisition.vertical_os.base import (
    ALL_VERTICALS,
    KPI,
    MessageTemplate,
    VerticalOS,
    get_vertical,
    list_vertical_summaries,
)


def test_three_verticals_registered():
    assert "clinics" in ALL_VERTICALS
    assert "real_estate" in ALL_VERTICALS
    assert "logistics" in ALL_VERTICALS


def test_get_vertical_unknown_returns_none():
    assert get_vertical("xxx") is None


def test_each_vertical_has_required_fields():
    for v in ALL_VERTICALS.values():
        assert v.vertical_id
        assert v.sector_ar
        assert v.pain_points_ar
        assert v.dashboard_kpis
        assert v.message_templates
        assert v.proposal_template_ar
        assert v.benchmark_reply_rate > 0
        assert v.avg_deal_value_sar > 0


def test_channel_mix_sums_close_to_one():
    for v in ALL_VERTICALS.values():
        if v.recommended_channel_mix:
            total = sum(v.recommended_channel_mix.values())
            assert 0.99 <= total <= 1.01


def test_clinics_kpis_include_no_show():
    v = get_vertical("clinics")
    metric_ids = {k.metric_id for k in v.dashboard_kpis}
    assert "no_show_rate" in metric_ids


def test_real_estate_message_targets_decision_maker():
    v = get_vertical("real_estate")
    bodies = [t.body_ar for t in v.message_templates]
    assert any("first_name" in t.variables for t in v.message_templates)


def test_logistics_priority_signals_include_tender():
    v = get_vertical("logistics")
    assert "tender_published" in v.priority_signals


def test_list_summaries_returns_compact_dicts():
    summaries = list_vertical_summaries()
    assert len(summaries) == 3
    for s in summaries:
        assert "vertical_id" in s
        assert "avg_deal_value_sar" in s
        assert "primary_channel" in s
        assert "n_kpis" in s


def test_kpi_higher_is_better_consistent():
    """Cost / time KPIs should mark higher_is_better=False."""
    for v in ALL_VERTICALS.values():
        for kpi in v.dashboard_kpis:
            mid = kpi.metric_id
            if "cost" in mid or "time" in mid or "no_show" in mid:
                assert kpi.higher_is_better is False, f"{mid} should be lower-is-better"


def test_message_template_body_uses_arabic():
    """Sanity: at least one Arabic char in each template."""
    for v in ALL_VERTICALS.values():
        for t in v.message_templates:
            # Arabic Unicode block 0x0600..0x06FF
            assert any("؀" <= ch <= "ۿ" for ch in t.body_ar), f"{t.template_id} not Arabic"
