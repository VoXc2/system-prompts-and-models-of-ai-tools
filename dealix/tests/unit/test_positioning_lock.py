"""Positioning Lock tests — enforce category rules + prohibited claims."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Positive claims that must NEVER appear in customer-facing pages.
# (Negative restatements like "no auto-DM" in safety sections are fine —
# we only block positive claims that promise forbidden behavior.)
PROHIBITED_PHRASES = (
    "نضمن لك عملاء",
    "نضمن مبيعات",
    "نتائج مضمونة 100%",
    "ضمان مضمون",
    "مليون ريال خلال شهر",
    "نسحب كل بيانات LinkedIn",
    "نقوم بـ auto-DM",
    "نتجاوز PDPL",
    "بدون مراجعة بشرية",
    "AI-only — لا تدخل بشري",
    "بديل HubSpot",
    "أرخص من Salesforce",
    "نقتل CRM",
)

# Required claims that should appear in the positioning + market messaging docs.
REQUIRED_CLAIMS_FRAGMENTS_AR = (
    "Approval-first",
    "PDPL",
    "Saudi Tone",
    "Proof Pack",
)


def _read(rel_path: str) -> str:
    p = REPO_ROOT / rel_path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def test_positioning_lock_exists():
    text = _read("docs/POSITIONING_LOCK.md")
    assert text, "POSITIONING_LOCK.md missing"
    assert "Saudi Revenue Execution OS" in text
    assert "ليس CRM" in text
    assert "ليس بوت واتساب" in text


def test_prohibited_claims_doc_exists():
    text = _read("docs/PROHIBITED_CLAIMS.md")
    assert text, "PROHIBITED_CLAIMS.md missing"
    assert "نضمن" in text
    assert "scraping" in text.lower()


def test_approved_market_messaging_doc_exists():
    text = _read("docs/APPROVED_MARKET_MESSAGING.md")
    assert text, "APPROVED_MARKET_MESSAGING.md missing"
    for fragment in REQUIRED_CLAIMS_FRAGMENTS_AR:
        assert fragment in text, f"missing required fragment: {fragment}"


def test_no_prohibited_phrases_in_landing_pages():
    """Customer-facing landing pages must NOT contain prohibited claims."""
    pages = [
        "landing/private-beta.html",
        "landing/services.html",
        "landing/free-diagnostic.html",
        "landing/first-10-opportunities.html",
        "landing/agency-partner.html",
        "landing/list-intelligence.html",
        "landing/growth-os.html",
        "landing/companies.html",
    ]
    failures: list[str] = []
    for page in pages:
        text = _read(page)
        if not text:
            continue  # page doesn't exist
        for bad in PROHIBITED_PHRASES:
            if bad in text:
                failures.append(f"{page} contains prohibited phrase: {bad}")
    assert not failures, "Prohibited phrases found:\n" + "\n".join(failures)


def test_companies_page_has_approved_messaging():
    text = _read("landing/companies.html")
    assert text, "landing/companies.html missing"
    assert "Approval-first" in text or "approval-first" in text.lower()
    # Should reference Proof Pack
    assert "Proof Pack" in text


def test_marketers_or_agency_page_exists():
    """At least one of the agency-facing pages must exist."""
    a = _read("landing/agency-partner.html")
    m = _read("landing/marketers.html")
    assert a or m, "Need at least one of agency-partner.html or marketers.html"


def test_private_beta_page_no_guarantees():
    text = _read("landing/private-beta.html")
    assert text, "private-beta.html missing"
    assert "نضمن" not in text or "لا نضمن" in text
    assert "guarantee" not in text.lower() or "no guarantee" in text.lower()


def test_revenue_today_playbook_emphasizes_approval():
    text = _read("docs/REVENUE_TODAY_PLAYBOOK.md")
    assert text, "REVENUE_TODAY_PLAYBOOK.md missing"
    assert "Approval-first" in text or "approval" in text.lower()
    # Must explicitly state no live charge
    assert "live charge" in text.lower() or "API charge" in text or "manual" in text.lower()


def test_positioning_lock_has_5_bundles():
    text = _read("docs/POSITIONING_LOCK.md")
    for bundle in (
        "Growth Starter",
        "Data to Revenue",
        "Executive Growth OS",
        "Partnership Growth",
        "Full Growth Control Tower",
    ):
        assert bundle in text, f"missing bundle in POSITIONING_LOCK.md: {bundle}"


def test_positioning_lock_lists_5_modes():
    text = _read("docs/POSITIONING_LOCK.md")
    for mode in (
        "CEO Mode",
        "Growth Manager Mode",
        "Agency Partner Mode",
        "Self-Growth Mode",
        "Service Delivery Mode",
    ):
        assert mode in text, f"missing mode in POSITIONING_LOCK.md: {mode}"
