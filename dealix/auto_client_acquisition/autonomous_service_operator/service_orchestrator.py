"""Map intents to recommended service_ids and bundles."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import intent_classifier as ic
from auto_client_acquisition.service_excellence.service_scoring import calculate_service_excellence_score
from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def recommend_for_intent(intent: str) -> dict[str, Any]:
    """Return primary service_id, optional bundle, and excellence gate."""
    mapping: dict[str, tuple[str, str | None]] = {
        ic.INTENT_WANT_MORE_CUSTOMERS: ("first_10_opportunities", "growth_starter"),
        ic.INTENT_HAS_CONTACT_LIST: ("list_intelligence", "data_to_revenue"),
        ic.INTENT_WANT_PARTNERSHIPS: ("partner_sprint", "partnership_growth"),
        ic.INTENT_ASK_PARTNERSHIP: ("partner_sprint", "partnership_growth"),
        ic.INTENT_WANT_DAILY_GROWTH: ("self_growth_operator", "executive_growth_os"),
        ic.INTENT_WANT_MEETINGS: ("meeting_booking_sprint", None),
        ic.INTENT_WANT_EMAIL_RESCUE: ("email_revenue_rescue", None),
        ic.INTENT_WANT_WHATSAPP_SETUP: ("whatsapp_compliance_setup", None),
        ic.INTENT_ASK_PRICING: ("growth_os", None),
        ic.INTENT_ASK_SERVICES: ("free_growth_diagnostic", None),
        ic.INTENT_ASK_DEMO: ("free_growth_diagnostic", None),
        ic.INTENT_ASK_PROOF: ("first_10_opportunities", None),
        ic.INTENT_ASK_REVENUE_TODAY: ("growth_os", None),
    }
    sid, bundle = mapping.get(intent, ("free_growth_diagnostic", None))
    svc = get_service_by_id(sid) or {}
    score = calculate_service_excellence_score(sid)
    return {
        "intent": intent,
        "recommended_service_id": sid,
        "service_name_ar": svc.get("name_ar"),
        "suggested_bundle_id": bundle,
        "excellence": {"total_score": score["total_score"], "status": score["status"]},
        "demo": True,
    }


def cold_whatsapp_response() -> dict[str, Any]:
    return {
        "blocked": True,
        "message_ar": "لا ندعم واتساب بارد أو غير موافق عليه. نرشّح: قالب opt-in، أو إيميل draft، أو سباق اجتماعات بعد موافقة.",
        "alternatives": ["whatsapp_opt_in_template", "gmail_draft", "meeting_booking_sprint"],
        "demo": True,
    }
