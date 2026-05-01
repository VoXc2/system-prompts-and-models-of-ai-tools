"""Smoke tests for Compliance OS v2."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from auto_client_acquisition.compliance_os.consent_ledger import (
    ALL_BASES,
    LawfulBasis,
    latest_state,
    record_consent,
    record_opt_out,
)
from auto_client_acquisition.compliance_os.contactability import check_contactability
from auto_client_acquisition.compliance_os.data_subject_requests import (
    DSR_TYPES,
    DSRStatus,
    SLA_DAYS,
    dsr_dashboard,
    is_overdue,
    open_dsr,
    process_dsr,
)
from auto_client_acquisition.compliance_os.risk_engine import score_campaign_risk
from auto_client_acquisition.compliance_os.ropa import (
    DEFAULT_ACTIVITIES,
    build_ropa,
)
from auto_client_acquisition.compliance_os.vendor_registry import (
    DEFAULT_VENDORS,
    Vendor,
    VendorStatus,
    register_vendor,
    vendors_summary,
)


# ── Consent Ledger ───────────────────────────────────────────────
def test_lawful_basis_constants_known():
    for b in (
        LawfulBasis.CONSENT, LawfulBasis.LEGITIMATE_INTEREST,
        LawfulBasis.CONTRACT, LawfulBasis.LEGAL_OBLIGATION,
    ):
        assert b in ALL_BASES


def test_record_consent_validates_basis():
    with pytest.raises(ValueError):
        record_consent(customer_id="c", contact_id="x", lawful_basis="bogus", purpose="x")


def test_latest_state_no_records():
    s = latest_state([])
    assert s["has_consent"] is False
    assert s["is_opted_out"] is False


def test_latest_state_after_consent():
    rec = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.LEGITIMATE_INTEREST,
        purpose="b2b_outreach",
    )
    s = latest_state([rec])
    assert s["has_consent"] is True
    assert s["lawful_basis"] == LawfulBasis.LEGITIMATE_INTEREST


def test_opt_out_overrides_prior_consent():
    rec1 = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.CONSENT, purpose="x",
        occurred_at=datetime(2026, 1, 1),
    )
    rec2 = record_opt_out(customer_id="c", contact_id="x", occurred_at=datetime(2026, 2, 1))
    s = latest_state([rec1, rec2])
    assert s["is_opted_out"] is True
    assert s["has_consent"] is False


def test_expired_consent_not_active():
    rec = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.CONSENT, purpose="x",
        expires_at=datetime(2020, 1, 1),  # past
    )
    s = latest_state([rec])
    assert s["has_consent"] is False


# ── Contactability ───────────────────────────────────────────────
def test_contactability_safe_with_consent():
    rec = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.LEGITIMATE_INTEREST, purpose="x",
    )
    s = check_contactability(
        contact_id="x", consent_records=[rec],
        messages_sent_this_week=0, current_riyadh_hour=12,
    )
    assert s.can_contact is True
    assert s.reason_code == "safe"


def test_contactability_blocks_opted_out():
    rec = record_opt_out(customer_id="c", contact_id="x")
    s = check_contactability(contact_id="x", consent_records=[rec])
    assert s.can_contact is False
    assert s.reason_code == "opted_out"


def test_contactability_blocks_no_consent():
    s = check_contactability(contact_id="x", consent_records=[])
    assert s.can_contact is False
    assert s.reason_code == "no_consent"


def test_contactability_blocks_freq_cap():
    rec = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.LEGITIMATE_INTEREST, purpose="x",
    )
    s = check_contactability(
        contact_id="x", consent_records=[rec],
        messages_sent_this_week=2, weekly_cap=2,
    )
    assert s.can_contact is False
    assert s.reason_code == "freq_cap"


def test_contactability_blocks_quiet_hours():
    rec = record_consent(
        customer_id="c", contact_id="x",
        lawful_basis=LawfulBasis.LEGITIMATE_INTEREST, purpose="x",
    )
    s = check_contactability(
        contact_id="x", consent_records=[rec], current_riyadh_hour=23,
    )
    assert s.can_contact is False
    assert s.reason_code == "quiet_hours"


# ── DSR ──────────────────────────────────────────────────────────
def test_dsr_types_known():
    assert "access" in DSR_TYPES
    assert "delete" in DSR_TYPES


def test_open_dsr_validates_type():
    with pytest.raises(ValueError):
        open_dsr(customer_id="c", data_subject_id="x", request_type="invalid")


def test_open_dsr_assigns_sla():
    r = open_dsr(customer_id="c", data_subject_id="x", request_type="delete")
    assert r.status == DSRStatus.OPEN
    expected_due = r.received_at + timedelta(days=SLA_DAYS["delete"])
    assert abs((r.sla_due_at - expected_due).total_seconds()) < 1


def test_process_dsr_completion():
    r = open_dsr(customer_id="c", data_subject_id="x", request_type="access")
    process_dsr(r, action_taken="completed", handled_by="dpo@x.sa", artifact_url="https://...")
    assert r.status == DSRStatus.COMPLETED
    assert r.completed_at is not None
    assert r.artifacts.get("export_url") == "https://..."


def test_process_dsr_rejection_requires_reason():
    r = open_dsr(customer_id="c", data_subject_id="x", request_type="object")
    with pytest.raises(ValueError):
        process_dsr(r, action_taken="rejected", handled_by="x")
    process_dsr(r, action_taken="rejected", handled_by="x", rejection_reason="duplicate")
    assert r.status == DSRStatus.REJECTED


def test_dsr_overdue_detection():
    r = open_dsr(
        customer_id="c", data_subject_id="x", request_type="access",
        received_at=datetime(2025, 1, 1),
    )
    assert is_overdue(r, now=datetime(2026, 1, 1)) is True


def test_dsr_dashboard():
    rs = [
        open_dsr(customer_id="c", data_subject_id="a", request_type="access"),
        open_dsr(customer_id="c", data_subject_id="b", request_type="delete"),
    ]
    process_dsr(rs[0], action_taken="completed", handled_by="x", artifact_url="...")
    d = dsr_dashboard(rs)
    assert d["n_total"] == 2
    assert d["by_status"][DSRStatus.COMPLETED] == 1


# ── Risk Engine ──────────────────────────────────────────────────
def test_clean_campaign_is_safe():
    r = score_campaign_risk(
        target_count=100,
        contacts_with_consent=100,
        contacts_opted_out=0,
        contacts_no_lawful_basis=0,
        template_body="مرحباً، نقدم حلول مبيعات B2B سعودية.",
        template_subject="نموذج",
        channel="email",
        has_unsubscribe_link=True,
    )
    assert r.risk_band == "safe"
    assert r.contacts_safe == 100


def test_risky_phrase_increases_score():
    r = score_campaign_risk(
        target_count=100, contacts_with_consent=100,
        contacts_opted_out=0, contacts_no_lawful_basis=0,
        template_body="عرض ضمان 100% نتائج مضمونة!",
    )
    assert r.risk_score > 30


def test_no_unsubscribe_blocks_email():
    r = score_campaign_risk(
        target_count=100, contacts_with_consent=100,
        contacts_opted_out=0, contacts_no_lawful_basis=0,
        template_body="x", channel="email", has_unsubscribe_link=False,
    )
    assert any("Unsubscribe" in b or "List" in b for b in r.blockers)


def test_pii_in_body_blocks():
    r = score_campaign_risk(
        target_count=100, contacts_with_consent=100,
        contacts_opted_out=0, contacts_no_lawful_basis=0,
        template_body="ارسل لنا رقم الهوية",
    )
    assert any("PII" in b or "حساسة" in b for b in r.blockers)


def test_low_safe_coverage_flags_issue():
    r = score_campaign_risk(
        target_count=100, contacts_with_consent=20,
        contacts_opted_out=20, contacts_no_lawful_basis=60,
        template_body="ok",
    )
    assert any("منخفضة" in i or "50%" in i for i in r.issues)


# ── RoPA ─────────────────────────────────────────────────────────
def test_default_ropa_has_required_activities():
    activities = {a.activity_id for a in DEFAULT_ACTIVITIES}
    for required in ("discovery", "enrichment", "outreach"):
        assert required in activities


def test_build_ropa_returns_json():
    r = build_ropa(customer_id="c", customer_name="Test Co.", dpo_name="x", dpo_email="x@x.sa")
    j = r.to_json()
    assert j["customer_id"] == "c"
    assert j["n_activities"] >= 6
    assert all("lawful_basis" in a for a in j["activities"])


def test_ropa_csv_rows():
    r = build_ropa(customer_id="c", customer_name="Test")
    rows = r.to_csv_rows()
    assert len(rows) == len(DEFAULT_ACTIVITIES)
    assert "name_ar" in rows[0]


# ── Vendor Registry ──────────────────────────────────────────────
def test_default_vendors_registered():
    ids = {v.vendor_id for v in DEFAULT_VENDORS}
    assert "anthropic" in ids
    assert "moyasar" in ids


def test_register_vendor_assigns_id_and_timestamp():
    v = Vendor(
        vendor_id="",
        name="Custom",
        purpose_ar="x",
        data_accessed=["x"],
        region="SA",
    )
    out = register_vendor(v)
    assert out.vendor_id.startswith("vnd_")
    assert out.onboarded_at is not None


def test_vendors_summary():
    s = vendors_summary()
    assert s["total"] == len(DEFAULT_VENDORS)
    assert s["with_dpa"] >= 0
    assert s["dpa_coverage_pct"] >= 0
