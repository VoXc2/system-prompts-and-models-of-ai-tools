"""WhatsApp interactive payload helpers."""

from __future__ import annotations

import pytest

from auto_client_acquisition.personal_operator.whatsapp_cards import (
    build_daily_brief_message,
    build_opportunity_buttons,
    parse_button_reply,
)


def test_opportunity_card_max_three_buttons():
    opp = {"id": "opp_test_1", "title": "Test"}
    payload = build_opportunity_buttons(opp)
    buttons = payload["interactive"]["action"]["buttons"]
    assert len(buttons) <= 3


def test_button_ids_stable_and_include_opportunity_id():
    opp = {"id": "opp_customer_beta"}
    payload = build_opportunity_buttons(opp)
    ids = [b["reply"]["id"] for b in payload["interactive"]["action"]["buttons"]]
    assert any("opp_customer_beta" in i for i in ids)
    assert all(i.startswith("opp:") for i in ids)


def test_arabic_labels_present():
    payload = build_opportunity_buttons({"id": "x"})
    titles = [b["reply"]["title"] for b in payload["interactive"]["action"]["buttons"]]
    assert any("قبول" in t for t in titles)


def test_parse_button_reply_maps_action():
    parsed = parse_button_reply({"button": {"payload": "opp:opp_internal_project:accept"}})
    assert parsed["ok"] is True
    assert parsed["action"] == "accept"
    assert parsed["opportunity_id"] == "opp_internal_project"


def test_daily_brief_payload():
    brief = {"greeting": "صباح الخير"}
    msg = build_daily_brief_message(brief)
    assert msg["interactive"]["body"]["text"]
