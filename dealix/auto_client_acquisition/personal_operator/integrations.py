"""Draft-only abstractions for Gmail and Calendar — no OAuth or send here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ExternalMode = Literal["draft_only", "approved_send"]


@dataclass(frozen=True)
class GmailDraftRequest:
    to_hint: str
    subject: str
    body_ar: str
    mode: ExternalMode = "draft_only"


@dataclass(frozen=True)
class CalendarDraftRequest:
    title: str
    duration_minutes: int
    agenda_ar: list[str]
    mode: ExternalMode = "draft_only"


@dataclass(frozen=True)
class IntegrationResult:
    ok: bool
    approval_required: bool
    payload: dict[str, Any]
    note: str


def build_gmail_draft_payload(req: GmailDraftRequest) -> IntegrationResult:
    return IntegrationResult(
        ok=True,
        approval_required=True,
        payload={
            "provider": "gmail",
            "draft": {
                "to": req.to_hint,
                "subject": req.subject,
                "body_ar": req.body_ar,
            },
            "mode": req.mode,
        },
        note="Gmail send requires OAuth adapter + explicit human approval in production.",
    )


def build_calendar_draft_payload(req: CalendarDraftRequest) -> IntegrationResult:
    return IntegrationResult(
        ok=True,
        approval_required=True,
        payload={
            "provider": "google_calendar",
            "draft_event": {
                "title": req.title,
                "duration_minutes": req.duration_minutes,
                "agenda_ar": req.agenda_ar,
            },
            "mode": req.mode,
        },
        note="Calendar event creation is blocked until approval layer and OAuth are configured.",
    )


def validate_external_action_approval(*, approved: bool, mode: ExternalMode) -> IntegrationResult:
    if not approved:
        return IntegrationResult(
            ok=False,
            approval_required=True,
            payload={},
            note="blocked_pending_approval",
        )
    if mode != "approved_send":
        return IntegrationResult(
            ok=False,
            approval_required=True,
            payload={},
            note="adapter_not_configured_use_approved_send_with_real_integration",
        )
    return IntegrationResult(
        ok=True,
        approval_required=False,
        payload={"status": "would_delegate_to_adapter"},
        note="Implement real Google API calls only behind this gate.",
    )
