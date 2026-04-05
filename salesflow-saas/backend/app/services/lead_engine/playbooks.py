"""Playbook definitions — triggers and motions (code-first; DB can override later)."""

from __future__ import annotations

from typing import Any, Dict, List

# motion: whatsapp_first | sdr_outbound | abm | nurture | partner | field_sales | founder_led

SAUDI_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "smb_whatsapp_first": {
        "name_ar": "واتساب أولاً — SMB",
        "motion": "whatsapp_first",
        "triggers": {"priority_band": ["P0", "P1"], "company_size": ["smb"]},
        "first_touch": "whatsapp_intro_template",
        "second_touch": "value_pdf_ar",
        "escalation": "call_request_if_replied",
        "pause_if": ["no_response_14d"],
        "success_metrics": ["reply_rate", "meeting_booked"],
    },
    "enterprise_abm": {
        "name_ar": "ABM مؤسسي",
        "motion": "abm",
        "triggers": {"priority_band": ["P0", "P1"], "company_size": ["enterprise"]},
        "first_touch": "multi_thread_email",
        "second_touch": "executive_brief_ar",
        "escalation": "exec_meeting",
        "pause_if": ["competitor_won"],
        "success_metrics": ["meeting", "pipeline"],
    },
    "high_intent_replace": {
        "name_ar": "استبدال منافس — نية عالية",
        "motion": "sdr_outbound",
        "triggers": {"intent": "high", "signal": "competitor_tool"},
        "first_touch": "comparison_one_pager",
        "second_touch": "demo_offer",
        "success_metrics": ["demo_booked"],
    },
    "local_city_cluster": {
        "name_ar": "تجميع مدينة",
        "motion": "field_sales",
        "triggers": {"geo_cluster": True},
        "first_touch": "local_case_study",
        "success_metrics": ["visit_or_call"],
    },
    "inbound_accel": {
        "name_ar": "تسريع وارد",
        "motion": "nurture",
        "triggers": {"source": ["website", "referral"]},
        "first_touch": "speed_to_lead_whatsapp",
        "success_metrics": ["time_to_first_touch"],
    },
}


def pick_playbook_key(priority_band: str, motion_hint: str, meta: Dict[str, Any]) -> str:
    if priority_band in ("P3", "reject"):
        return "inbound_accel"
    if meta.get("enterprise"):
        return "enterprise_abm"
    if motion_hint == "whatsapp_first" or meta.get("whatsapp_priority"):
        return "smb_whatsapp_first"
    if meta.get("competitor_replacement"):
        return "high_intent_replace"
    if meta.get("city_cluster"):
        return "local_city_cluster"
    return "smb_whatsapp_first"
