"""Unit tests for the Paid Beta Daily Scorecard script."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import paid_beta_daily_scorecard as pbds  # noqa: E402


# ----- core scorecard logic -----

def test_zero_input_yields_off_track():
    card = pbds.build_scorecard(0, 0, 0, 0, 0, 0, as_of="2026-05-01")
    assert card.messages == 0
    assert card.reply_rate == 0.0
    # 0 messages, 0 replies, 0 demos → daily target on messages is breached.
    assert "OFF_TRACK" in card.daily_verdict or "BEHIND" in card.daily_verdict
    assert any("رسالة" in a or "messages" in a.lower() for a in card.next_actions)


def test_full_day_on_track():
    card = pbds.build_scorecard(10, 1, 1, 0, 0, 0, as_of="2026-05-01")
    assert card.daily_verdict == "ON_TRACK"
    # Weekly is still in early days; expect blockers but daily is fine.
    assert "BLOCKERS" in card.weekly_verdict


def test_high_message_zero_reply_triggers_tone_action():
    card = pbds.build_scorecard(20, 0, 0, 0, 0, 0)
    assert any("نبرة" in a or "tone" in a.lower() for a in card.next_actions)


def test_payment_received_advances_proof_pack_action():
    card = pbds.build_scorecard(20, 4, 2, 1, 1, 0)
    assert any("Proof Pack" in a for a in card.next_actions)


def test_weekly_targets_hit_when_full_week():
    card = pbds.build_scorecard(70, 15, 7, 3, 2, 1)
    assert card.weekly_verdict == "WEEKLY_TARGETS_HIT"


def test_conversion_rates_computed():
    card = pbds.build_scorecard(25, 5, 2, 1, 1, 0)
    assert card.reply_rate == 0.2
    assert card.demo_rate == 0.4
    assert card.pilot_rate == 0.5
    assert card.payment_rate == 1.0


# ----- rendering -----

def test_render_text_contains_arabic_labels():
    card = pbds.build_scorecard(25, 4, 2, 1, 0, 0)
    text = pbds.render_text(card)
    assert "Paid Beta Daily Scorecard" in text
    assert "رسائل أُرسلت" in text
    assert "Daily Verdict" in text
    assert "Weekly Verdict" in text
    assert "Next Actions" in text


def test_render_json_is_valid_json():
    card = pbds.build_scorecard(25, 4, 2, 1, 0, 0, as_of="2026-05-01")
    output = pbds.render_json(card)
    parsed = json.loads(output)
    assert parsed["messages"] == 25
    assert parsed["as_of"] == "2026-05-01"
    assert "next_actions" in parsed
    assert isinstance(parsed["next_actions"], list)


# ----- CLI -----

def test_cli_main_text_mode(capsys):
    rc = pbds.main([
        "--messages", "25", "--replies", "4",
        "--demos", "2", "--pilots", "1",
        "--payments", "0", "--proof-packs", "0",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Paid Beta Daily Scorecard" in captured.out
    assert "25" in captured.out


def test_cli_main_json_mode(capsys):
    rc = pbds.main([
        "--messages", "25", "--replies", "4",
        "--demos", "2", "--pilots", "1",
        "--payments", "1", "--proof-packs", "0",
        "--json",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["messages"] == 25
    assert payload["payments"] == 1
    assert payload["weekly_verdict"]


def test_cli_as_of_today(capsys):
    rc = pbds.main(["--messages", "10", "--as-of", "today"])
    assert rc == 0
    captured = capsys.readouterr()
    # 'today' should resolve to a real date string in the output (YYYY-MM-DD).
    assert "20" in captured.out  # any year starts with "20" in our era


def test_cli_as_of_explicit(capsys):
    rc = pbds.main([
        "--messages", "10", "--as-of", "2026-04-30",
        "--json",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["as_of"] == "2026-04-30"
