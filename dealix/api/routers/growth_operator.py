"""
Growth Operator router — Arabic Growth Operator endpoints.

Approval-first: every outbound is draft. Nothing is sent / charged /
scheduled live from this router; that happens in dedicated send / billing
/ calendar services after explicit user approval.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Query

from auto_client_acquisition.growth_operator import (
    build_calendar_draft,
    build_meeting_agenda,
    build_moyasar_payment_link_draft,
    build_post_meeting_followup,
    build_weekly_proof_pack,
    contactability_summary,
    dedupe_contacts,
    draft_arabic_message,
    draft_followup,
    draft_objection_response,
    draft_partner_outreach,
    list_missions,
    partner_scorecard,
    profile_from_dict,
    recommend_top_10,
    run_mission,
    score_contactability,
    suggest_partner_types,
    summarize_import,
)

router = APIRouter(prefix="/api/v1/growth-operator", tags=["growth-operator"])
log = logging.getLogger(__name__)


# ── 1. Contacts: import preview ─────────────────────────────────
@router.post("/contacts/import-preview")
async def contacts_import_preview(
    contacts: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    channel: str = Body(default="whatsapp", embed=True),
) -> dict[str, Any]:
    """Preview import: dedupe + source classify + contactability summary."""
    deduped = dedupe_contacts(contacts)
    return {
        "import_summary": summarize_import(contacts),
        "contactability": contactability_summary(deduped, channel=channel),
        "policy_note_ar": (
            "العميل يرفع أرقام مملوكة/مصرح بها. لا cold WhatsApp بدون lawful basis."
        ),
        "approval_required": True,
        "approval_status": "pending_approval",
    }


# ── 2. Targeting: top-10 ────────────────────────────────────────
@router.post("/targets/top-10")
async def targets_top_10(
    contacts: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    sector_hint: str = Body(default="", embed=True),
    channel: str = Body(default="whatsapp", embed=True),
) -> dict[str, Any]:
    """Rank uploaded contacts → top-10 safe + Why-Now."""
    return recommend_top_10(contacts, sector_hint=sector_hint, channel=channel)


# ── 3. Messages: draft / followup / objection ──────────────────
@router.post("/messages/draft")
async def messages_draft(
    contact: dict[str, Any] = Body(..., embed=True),
    profile: dict[str, Any] | None = Body(default=None, embed=True),
    goal_ar: str = Body(default="تشغيل نمو B2B بلا إرسال عشوائي", embed=True),
) -> dict[str, Any]:
    """Saudi-tone Arabic outreach draft (always pending_approval)."""
    return draft_arabic_message(contact, profile=profile, goal_ar=goal_ar)


@router.post("/messages/followup")
async def messages_followup(
    contact: dict[str, Any] = Body(..., embed=True),
    days_since_last: int = Body(default=3, embed=True),
    last_outcome: str = Body(default="no_reply", embed=True),
) -> dict[str, Any]:
    return draft_followup(
        contact, days_since_last=days_since_last, last_outcome=last_outcome,
    )


@router.post("/messages/objection-response")
async def messages_objection_response(
    objection_id: str = Body(..., embed=True),
    contact: dict[str, Any] | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    return draft_objection_response(objection_id, contact=contact)


# ── 4. Partners: suggest / outreach / scorecard ────────────────
@router.post("/partners/suggest")
async def partners_suggest(
    sector: str = Body(default="", embed=True),
    customer_size: str = Body(default="smb", embed=True),
) -> dict[str, Any]:
    return suggest_partner_types(sector=sector, customer_size=customer_size)


@router.post("/partners/outreach")
async def partners_outreach(
    partner_type_key: str = Body(..., embed=True),
    partner_name: str = Body(default="", embed=True),
    customer_name: str = Body(default="Dealix", embed=True),
) -> dict[str, Any]:
    return draft_partner_outreach(
        partner_type_key=partner_type_key,
        partner_name=partner_name,
        customer_name=customer_name,
    )


@router.post("/partners/scorecard")
async def partners_scorecard(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return partner_scorecard(
        partner_id=payload.get("partner_id", "unknown"),
        intros_made=int(payload.get("intros_made", 0)),
        deals_influenced=int(payload.get("deals_influenced", 0)),
        revenue_share_paid_sar=float(payload.get("revenue_share_paid_sar", 0)),
        relationship_age_months=int(payload.get("relationship_age_months", 0)),
    )


# ── 5. Meetings: agenda / calendar draft / followup ────────────
@router.post("/meetings/draft")
async def meetings_draft(
    contact_name: str = Body(..., embed=True),
    company: str = Body(..., embed=True),
    contact_email: str | None = Body(default=None, embed=True),
    purpose_ar: str = Body(default="اكتشاف وتأهيل أولي", embed=True),
    duration_minutes: int = Body(default=20, embed=True),
    proposed_start_iso: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    """Build agenda + calendar draft (NOT created live)."""
    agenda = build_meeting_agenda(
        contact_name=contact_name,
        company=company,
        purpose_ar=purpose_ar,
        duration_minutes=duration_minutes,
    )
    cal_draft = build_calendar_draft(
        contact_email=contact_email,
        contact_name=contact_name,
        company=company,
        proposed_start_iso=proposed_start_iso,
        duration_minutes=duration_minutes,
    )
    return {"agenda": agenda, "calendar_draft": cal_draft}


@router.post("/meetings/post-followup")
async def meetings_post_followup(
    contact_name: str = Body(..., embed=True),
    company: str = Body(..., embed=True),
    summary_ar: str = Body(..., embed=True),
    next_step_ar: str = Body(default="أرسل recap + pilot offer", embed=True),
) -> dict[str, Any]:
    return build_post_meeting_followup(
        contact_name=contact_name,
        company=company,
        summary_ar=summary_ar,
        next_step_ar=next_step_ar,
    )


# ── 6. Payment offer (Moyasar payment-link draft) ─────────────
@router.post("/payment-offer/draft")
async def payment_offer_draft(
    plan_key: str = Body(..., embed=True),
    customer_id: str = Body(..., embed=True),
    contact_email: str | None = Body(default=None, embed=True),
    custom_amount_sar: float | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    return build_moyasar_payment_link_draft(
        plan_key=plan_key,
        customer_id=customer_id,
        contact_email=contact_email,
        custom_amount_sar=custom_amount_sar,
    )


# ── 7. Missions ────────────────────────────────────────────────
@router.get("/missions")
async def missions_list() -> dict[str, Any]:
    return list_missions()


@router.post("/missions/{mission_id}/run")
async def missions_run(
    mission_id: str,
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    return run_mission(mission_id, payload=payload)


# ── 8. Proof Pack demo ─────────────────────────────────────────
@router.get("/proof-pack/demo")
async def proof_pack_demo(
    customer_id: str = Query(default="demo"),
    customer_name: str = Query(default="Demo Saudi B2B Co."),
) -> dict[str, Any]:
    return build_weekly_proof_pack(
        customer_id=customer_id,
        customer_name=customer_name,
        week_label="W18-2026",
        plan_cost_weekly_sar=750,
        opportunities_discovered=42,
        messages_drafted=38,
        messages_approved=33,
        messages_sent=33,
        replies_received=11,
        positive_replies=4,
        meetings_booked=3,
        meetings_held=2,
        proposals_sent=1,
        deals_won=0,
        pipeline_added_sar=185_000,
        revenue_won_sar=0,
        risky_drafts_blocked=5,
        revenue_leaks_recovered=2,
        avg_response_minutes=42,
        best_message_subject="ملاحظة على توسعكم في الرياض",
        best_message_reply_rate=0.18,
    )


# ── 9. Single-contact contactability ─────────────────────────
@router.post("/contactability/score")
async def contactability_score_single(
    contact: dict[str, Any] = Body(..., embed=True),
    channel: str = Body(default="whatsapp", embed=True),
) -> dict[str, Any]:
    return score_contactability(contact, channel=channel)


# ── 10. Profile ────────────────────────────────────────────────
@router.post("/profile")
async def profile_set(
    profile: dict[str, Any] = Body(..., embed=True),
) -> dict[str, Any]:
    p = profile_from_dict(profile)
    return {
        "profile": p.to_dict(),
        "is_specialized": p.is_specialized(),
        "missing_fields_ar": (
            [] if p.is_specialized() else
            ["sector", "city", "offer_one_liner", "ideal_customer"]
        ),
    }
