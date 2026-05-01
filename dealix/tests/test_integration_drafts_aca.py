"""Draft-only integration payloads under auto_client_acquisition.integrations."""

from __future__ import annotations

from auto_client_acquisition.integrations.calendar_operator import build_calendar_draft_payload
from auto_client_acquisition.integrations.gmail_operator import build_gmail_draft_payload
from auto_client_acquisition.integrations.moyasar_draft import build_moyasar_payment_draft


def test_gmail_draft_has_raw_and_approval() -> None:
    out = build_gmail_draft_payload({"to": "x@y.com", "subject_ar": "موضوع", "body_ar": "مرحبا"})
    assert out["approval_required"] is True
    assert "raw" in out["message"]


def test_calendar_draft_shape() -> None:
    out = build_calendar_draft_payload({})
    assert out["approval_required"] is True
    assert "start" in out["event"]


def test_moyasar_invalid_amount() -> None:
    out = build_moyasar_payment_draft({"amount_halalas": "x"})
    assert out["valid"] is False
    assert out.get("payment_link_draft") is None


def test_moyasar_payment_link_draft_present() -> None:
    out = build_moyasar_payment_draft({"amount_halalas": 50000, "invoice_reference": "INV-1"})
    assert out["valid"] is True
    assert "api.moyasar.com" in (out.get("payment_link_draft") or "")
    assert out.get("invoice_reference") == "INV-1"
