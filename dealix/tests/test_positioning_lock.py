"""Sanity checks for positioning docs (no prohibited phrases in approved doc)."""

from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
DOCS = _REPO / "docs"


def test_positioning_lock_exists_and_has_category() -> None:
    p = DOCS / "POSITIONING_LOCK.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "Saudi Revenue Execution OS" in text or "نظام تشغيل" in text
    assert "ليس CRM" in text or "ليس" in text


def test_prohibited_claims_lists_guarantee() -> None:
    p = DOCS / "PROHIBITED_CLAIMS.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "نضمن" in text or "مضمون" in text


def test_approved_messaging_has_headlines() -> None:
    p = DOCS / "APPROVED_MARKET_MESSAGING.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "Dealix" in text
    assert "scraping" not in text.lower()


def test_self_growth_and_service_delivery_modes() -> None:
    from auto_client_acquisition.autonomous_service_operator.self_growth_mode import mode_profile as sg
    from auto_client_acquisition.autonomous_service_operator.service_delivery_mode import mode_profile as sd

    assert sg()["mode"] == "self_growth"
    assert sd()["mode"] == "service_delivery"
