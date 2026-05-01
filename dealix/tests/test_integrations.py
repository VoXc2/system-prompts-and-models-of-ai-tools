"""Draft-only Gmail/Calendar integration helpers."""

from __future__ import annotations

from auto_client_acquisition.personal_operator.integrations import (
    CalendarDraftRequest,
    GmailDraftRequest,
    build_calendar_draft_payload,
    build_gmail_draft_payload,
    validate_external_action_approval,
)


def test_gmail_draft_payload():
    r = build_gmail_draft_payload(GmailDraftRequest(to_hint="x@y.com", subject="s", body_ar="مرحبا"))
    assert r.approval_required is True
    assert r.payload["draft"]["body_ar"]


def test_calendar_draft_payload():
    r = build_calendar_draft_payload(
        CalendarDraftRequest(title="t", duration_minutes=25, agenda_ar=["نقطة 1"]),
    )
    assert r.ok and r.approval_required


def test_validate_external_blocks_without_approval():
    r = validate_external_action_approval(approved=False, mode="draft_only")
    assert r.ok is False
