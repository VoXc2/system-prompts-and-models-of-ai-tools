"""Tests for follow-up prioritization engine."""
import csv
import tempfile
import os
import pytest
from pathlib import Path
from datetime import datetime, timedelta

import prioritize as p


def _make_csv(rows: list[dict]) -> Path:
    """Write a temporary CSV with prospect rows."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    fields = [
        "phone", "company", "contact_name", "channel", "status",
        "first_contact_at", "last_contact_at", "next_followup_at",
        "reply_count", "touches", "notes", "tags",
    ]
    writer = csv.DictWriter(tmp, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        full = {f: "" for f in fields}
        full.update(row)
        writer.writerow(full)
    tmp.close()
    return Path(tmp.name)


@pytest.fixture
def csv_path():
    paths = []
    yield paths
    for path in paths:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


class TestScoring:
    def test_pending_gets_nonzero_score(self):
        prospect = p.Prospect(
            phone="+966500000001", company="Test Co", contact_name="Ali",
            channel="whatsapp", status="pending",
            first_contact_at="", last_contact_at="", next_followup_at="",
            reply_count=0, touches=0, notes="", tags="",
        )
        score, reason = p.score_prospect(prospect)
        assert score > 0
        assert "funnel" in reason

    def test_qualified_scores_higher_than_pending(self):
        base = dict(
            phone="+966500000001", company="Co", contact_name="",
            channel="whatsapp", first_contact_at="",
            last_contact_at="", next_followup_at="",
            reply_count=0, touches=0, notes="", tags="",
        )
        pending = p.Prospect(**base, status="pending")
        qualified = p.Prospect(**base, status="qualified")
        s_pending, _ = p.score_prospect(pending)
        s_qualified, _ = p.score_prospect(qualified)
        assert s_qualified > s_pending

    def test_terminal_statuses_score_zero(self):
        for status in ("closed_won", "closed_lost", "dnc"):
            prospect = p.Prospect(
                phone="+966500000001", company="Co", contact_name="",
                channel="whatsapp", status=status,
                first_contact_at="", last_contact_at="", next_followup_at="",
                reply_count=0, touches=0, notes="", tags="",
            )
            score, _ = p.score_prospect(prospect)
            assert score == 0, f"{status} should score 0"

    def test_tags_boost_score(self):
        no_tag = p.Prospect(
            phone="+966500000001", company="Co", contact_name="",
            channel="whatsapp", status="pending",
            first_contact_at="", last_contact_at="", next_followup_at="",
            reply_count=0, touches=0, notes="", tags="",
        )
        with_tag = p.Prospect(
            phone="+966500000002", company="Co", contact_name="",
            channel="whatsapp", status="pending",
            first_contact_at="", last_contact_at="", next_followup_at="",
            reply_count=0, touches=0, notes="", tags="enterprise",
        )
        s1, _ = p.score_prospect(no_tag)
        s2, _ = p.score_prospect(with_tag)
        assert s2 > s1

    def test_engagement_ratio(self):
        high = p.Prospect(
            phone="+966500000001", company="Co", contact_name="",
            channel="whatsapp", status="replied",
            first_contact_at="2026-04-10 10:00", last_contact_at="2026-04-14 10:00",
            next_followup_at="", reply_count=3, touches=4, notes="", tags="",
        )
        low = p.Prospect(
            phone="+966500000002", company="Co", contact_name="",
            channel="whatsapp", status="replied",
            first_contact_at="2026-04-10 10:00", last_contact_at="2026-04-14 10:00",
            next_followup_at="", reply_count=1, touches=10, notes="", tags="",
        )
        s_high, _ = p.score_prospect(high)
        s_low, _ = p.score_prospect(low)
        assert s_high > s_low


class TestPrioritize:
    def test_sorts_by_score_descending(self):
        prospects = [
            p.Prospect(
                phone="+966500000001", company="Low", contact_name="",
                channel="whatsapp", status="pending",
                first_contact_at="", last_contact_at="", next_followup_at="",
                reply_count=0, touches=0, notes="", tags="",
            ),
            p.Prospect(
                phone="+966500000002", company="High", contact_name="",
                channel="whatsapp", status="qualified",
                first_contact_at="2026-04-13 10:00",
                last_contact_at="2026-04-14 10:00", next_followup_at="",
                reply_count=2, touches=3, notes="", tags="enterprise",
            ),
        ]
        actions = p.prioritize(prospects)
        assert len(actions) == 2
        assert actions[0].prospect.company == "High"


class TestActionPicking:
    def test_pending_gets_wa01(self):
        action = p.pick_action(
            p.Prospect(
                phone="+966500000001", company="Co", contact_name="",
                channel="whatsapp", status="pending",
                first_contact_at="", last_contact_at="", next_followup_at="",
                reply_count=0, touches=0, notes="", tags="",
            ),
            None,
        )
        assert "WA-01" in action

    def test_qualified_gets_call(self):
        action = p.pick_action(
            p.Prospect(
                phone="+966500000001", company="Co", contact_name="",
                channel="whatsapp", status="qualified",
                first_contact_at="", last_contact_at="", next_followup_at="",
                reply_count=0, touches=0, notes="", tags="",
            ),
            2,
        )
        assert "مكالمة" in action or "call" in action.lower()


class TestCLI:
    def test_table_output(self, csv_path):
        path = _make_csv([
            {"phone": "+966500000001", "company": "Co1", "status": "pending"},
            {"phone": "+966500000002", "company": "Co2", "status": "qualified",
             "last_contact_at": "2026-04-14 10:00", "reply_count": "2", "touches": "3"},
        ])
        csv_path.append(path)
        assert p.main(["--csv", str(path), "--top", "5"]) == 0

    def test_json_output(self, csv_path):
        path = _make_csv([
            {"phone": "+966500000001", "company": "Co1", "status": "replied",
             "last_contact_at": "2026-04-14 10:00", "reply_count": "1", "touches": "2"},
        ])
        csv_path.append(path)
        assert p.main(["--csv", str(path), "--json"]) == 0

    def test_export_csv(self, csv_path, tmp_path):
        path = _make_csv([
            {"phone": "+966500000001", "company": "Co1", "status": "pending"},
        ])
        csv_path.append(path)
        out = tmp_path / "out.csv"
        assert p.main(["--csv", str(path), "--export", str(out)]) == 0
        assert out.exists()
        content = out.read_text()
        assert "+966500000001" in content
