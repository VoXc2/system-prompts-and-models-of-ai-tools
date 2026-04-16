"""Tests for outreach tracker CLI."""
import os
import tempfile
import pytest
from pathlib import Path

# Patch DATA_FILE before importing tracker
_tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
_tmp.close()
os.environ["DEALIX_TRACKER_CSV"] = _tmp.name

import tracker  # noqa: E402


@pytest.fixture(autouse=True)
def clean_csv():
    """Reset the CSV file before each test."""
    Path(tracker.DATA_FILE).write_text("")
    yield
    try:
        os.unlink(_tmp.name)
    except FileNotFoundError:
        pass


class TestAdd:
    def test_add_new_prospect(self):
        assert tracker.main(["add", "+966500000001", "Test Co"]) == 0
        rows = tracker.load()
        assert len(rows) == 1
        assert rows[0].phone == "+966500000001"
        assert rows[0].company == "Test Co"
        assert rows[0].status == "pending"

    def test_add_duplicate_fails(self):
        tracker.main(["add", "+966500000001", "Test Co"])
        assert tracker.main(["add", "+966500000001", "Dup Co"]) == 1

    def test_add_with_tags(self):
        tracker.main(["add", "+966500000002", "Co", "--tags", "real_estate;riyadh"])
        rows = tracker.load()
        assert "real_estate" in rows[0].tags


class TestStatus:
    def test_update_status(self):
        tracker.main(["add", "+966500000001", "Co"])
        assert tracker.main(["status", "+966500000001", "--to", "contacted"]) == 0
        rows = tracker.load()
        assert rows[0].status == "contacted"
        assert int(rows[0].touches) == 1
        assert rows[0].first_contact_at != ""

    def test_replied_increments_reply_count(self):
        tracker.main(["add", "+966500000001", "Co"])
        tracker.main(["status", "+966500000001", "--to", "contacted"])
        tracker.main(["status", "+966500000001", "--to", "replied"])
        rows = tracker.load()
        assert int(rows[0].reply_count) == 1

    def test_invalid_status_fails(self):
        tracker.main(["add", "+966500000001", "Co"])
        assert tracker.main(["status", "+966500000001", "--to", "invalid_status"]) == 2

    def test_not_found_fails(self):
        assert tracker.main(["status", "+966NOTEXIST", "--to", "contacted"]) == 1


class TestNote:
    def test_add_note(self):
        tracker.main(["add", "+966500000001", "Co"])
        assert tracker.main(["note", "+966500000001", "Wants callback"]) == 0
        rows = tracker.load()
        assert "Wants callback" in rows[0].notes


class TestList:
    def test_list_all(self):
        tracker.main(["add", "+966500000001", "Co1"])
        tracker.main(["add", "+966500000002", "Co2"])
        assert tracker.main(["list"]) == 0

    def test_filter_by_status(self):
        tracker.main(["add", "+966500000001", "Co1"])
        tracker.main(["add", "+966500000002", "Co2"])
        tracker.main(["status", "+966500000001", "--to", "contacted"])
        assert tracker.main(["list", "--status", "contacted"]) == 0


class TestStats:
    def test_empty_stats(self):
        assert tracker.main(["stats"]) == 0

    def test_stats_with_data(self):
        tracker.main(["add", "+966500000001", "Co1"])
        tracker.main(["status", "+966500000001", "--to", "contacted"])
        tracker.main(["add", "+966500000002", "Co2"])
        assert tracker.main(["stats"]) == 0


class TestDue:
    def test_pending_are_due(self):
        tracker.main(["add", "+966500000001", "Co"])
        # Pending prospects with no contact are always due
        assert tracker.main(["due"]) == 0


class TestImport:
    def test_import_csv(self):
        import_file = Path(_tmp.name + ".import.csv")
        import_file.write_text("phone,company,contact_name\n+966500000099,Import Co,Ali\n")
        assert tracker.main(["import", str(import_file)]) == 0
        rows = tracker.load()
        assert any(r.phone == "+966500000099" for r in rows)
        import_file.unlink(missing_ok=True)

    def test_import_skips_existing(self):
        tracker.main(["add", "+966500000099", "Existing Co"])
        import_file = Path(_tmp.name + ".import2.csv")
        import_file.write_text("phone,company\n+966500000099,Dup\n+966500000088,New\n")
        tracker.main(["import", str(import_file)])
        rows = tracker.load()
        assert len(rows) == 2
        import_file.unlink(missing_ok=True)


class TestFollowupCadence:
    def test_contacted_gets_2day_followup(self):
        tracker.main(["add", "+966500000001", "Co"])
        tracker.main(["status", "+966500000001", "--to", "contacted"])
        rows = tracker.load()
        assert rows[0].next_followup_at != ""

    def test_dnc_has_no_followup(self):
        tracker.main(["add", "+966500000001", "Co"])
        tracker.main(["status", "+966500000001", "--to", "dnc"])
        rows = tracker.load()
        assert rows[0].next_followup_at == ""
