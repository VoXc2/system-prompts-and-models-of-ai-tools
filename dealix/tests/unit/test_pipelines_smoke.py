"""Smoke tests for normalization, dedupe, and scoring pipelines."""

from __future__ import annotations

from auto_client_acquisition.pipelines.dedupe import build_index, find_match
from auto_client_acquisition.pipelines.normalize import (
    fuzzy_company_key,
    is_acceptable,
    normalize_company_name,
    normalize_domain,
    normalize_email,
    normalize_row,
    normalize_saudi_phone,
)
from auto_client_acquisition.pipelines.scoring import (
    compute_data_quality,
    compute_lead_score,
)


# ── Phone ──────────────────────────────────────────────────────
def test_phone_local_to_e164():
    assert normalize_saudi_phone("0501234567") == "+966501234567"


def test_phone_already_e164():
    assert normalize_saudi_phone("+966501234567") == "+966501234567"


def test_phone_double_zero_intl():
    assert normalize_saudi_phone("00966501234567") == "+966501234567"


def test_phone_short_local():
    assert normalize_saudi_phone("501234567") == "+966501234567"


def test_phone_empty():
    assert normalize_saudi_phone("") is None
    assert normalize_saudi_phone(None) is None


# ── Domain ─────────────────────────────────────────────────────
def test_domain_strips_protocol_and_www():
    assert normalize_domain("https://www.foodics.com/contact") == "foodics.com"


def test_domain_case_insensitive():
    assert normalize_domain("FOODICS.com") == "foodics.com"


def test_domain_invalid():
    assert normalize_domain("") is None
    assert normalize_domain(None) is None
    assert normalize_domain("just-a-string") is None


# ── Email ──────────────────────────────────────────────────────
def test_email_lowercase():
    assert normalize_email("Sami@DEALIX.me") == "sami@dealix.me"


def test_email_invalid():
    assert normalize_email("not-an-email") is None
    assert normalize_email("") is None


# ── Row normalization ──────────────────────────────────────────
def test_normalize_row_arabic_keys():
    nr = normalize_row({
        "اسم الشركة": "شركة الراجحي العقارية",
        "الموقع": "https://alrajhi-realestate.com",
        "الهاتف": "+966501234567",
        "المدينة": "الرياض",
        "القطاع": "real_estate",
    })
    assert nr["domain"] == "alrajhi-realestate.com"
    assert nr["phone"] == "+966501234567"
    assert nr["city"] == "الرياض"


def test_acceptable_requires_company_and_identifier():
    nr = normalize_row({"company_name": "X"})
    ok, why = is_acceptable(nr)
    assert ok is False
    assert "no_contact_or_identifier" in (why or "")


def test_acceptable_with_phone():
    nr = normalize_row({"company_name": "Test", "phone": "0501234567"})
    ok, _why = is_acceptable(nr)
    assert ok is True


# ── Dedupe ─────────────────────────────────────────────────────
def test_dedupe_by_domain():
    idx = build_index([
        {"id": "acc_1", "company_name": "Foodics", "normalized_name": "foodics",
         "domain": "foodics.com", "city": "Riyadh"},
    ])
    new = {
        "company_name": "فودكس", "normalized_name": "فودكس",
        "domain": "foodics.com", "phone": None, "email": None,
        "google_place_id": None, "city": "Riyadh",
    }
    hit, kind = find_match(new, idx)
    assert hit == "acc_1"
    assert kind == "domain"


def test_dedupe_no_match_for_different_domain():
    idx = build_index([
        {"id": "acc_1", "company_name": "Foodics", "normalized_name": "foodics",
         "domain": "foodics.com", "city": "Riyadh"},
    ])
    new = {
        "company_name": "Other", "normalized_name": "other",
        "domain": "otherco.sa", "phone": None, "email": None,
        "google_place_id": None, "city": "Riyadh",
    }
    hit, kind = find_match(new, idx)
    assert hit is None
    assert kind is None


def test_dedupe_by_place_id():
    idx = build_index([
        {"id": "acc_x", "company_name": "Clinic", "normalized_name": "clinic",
         "google_place_id": "PID_123", "city": "Riyadh"},
    ])
    hit, kind = find_match(
        {"company_name": "Clinic", "normalized_name": "clinic",
         "google_place_id": "PID_123", "city": "Riyadh"},
        idx,
    )
    assert (hit, kind) == ("acc_x", "place_id")


# ── Scoring ────────────────────────────────────────────────────
def test_lead_score_high_value_sector():
    score = compute_lead_score({
        "sector": "saas", "country": "SA", "city": "Riyadh",
        "phone": "+966501234567", "website": "https://foodics.com",
        "email": "info@foodics.com",
    })
    assert score.priority in ("P0", "P1", "P2")
    assert score.fit > 0
    assert score.recommended_channel is not None


def test_lead_score_opt_out_blocks_channel():
    score = compute_lead_score({
        "sector": "saas", "country": "SA",
        "phone": "+966501234567", "opt_out": True,
    })
    assert score.recommended_channel is None


def test_dq_score_negative_on_opt_out():
    dq, reasons = compute_data_quality({
        "domain": "x.com", "city": "Riyadh", "sector": "SaaS",
        "phone": "+966501234567", "opt_out": True,
        "allowed_use": "business_contact_research_only",
    })
    assert dq == 0  # opt_out subtracts 100, clamped to 0
    assert "-opt_out" in reasons


def test_dq_score_rewards_multi_source():
    dq, reasons = compute_data_quality({
        "domain": "x.com", "website": "https://x.com",
        "city": "Riyadh", "sector": "SaaS",
        "source_url": "https://example.com",
        "phone": "+966501234567",
        "source_count": 3, "best_source": "google_maps",
        "allowed_use": "business_contact_research_only",
    })
    assert "+multi_source" in reasons
    assert dq > 50
