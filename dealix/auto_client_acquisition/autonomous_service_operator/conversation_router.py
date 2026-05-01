"""Single entry: user message → intent → recommendation + session updates."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import (
    approval_manager as am,
    intent_classifier as ic,
    operator_memory as om,
    service_bundles as sb,
    service_orchestrator as so,
    session_state as ss,
    workflow_runner as wr,
)


def handle_message(session_id: str, message: str, mode: str = "client") -> dict[str, Any]:
    intent = ic.classify_intent(message)
    om.append_turn(session_id, "user", message, {"intent": intent})

    if intent == ic.INTENT_COLD_WHATSAPP_REQUEST:
        body = so.cold_whatsapp_response()
        om.append_turn(session_id, "assistant", body["message_ar"], {"blocked": True})
        ss.upsert_session(session_id, {"last_intent": intent, "blocked": True})
        return {"session_id": session_id, "intent": intent, **body}

    rec = so.recommend_for_intent(intent)
    ss.upsert_session(
        session_id,
        {
            "last_intent": intent,
            "recommended_service_id": rec["recommended_service_id"],
            "mode": mode,
        },
    )
    wr.advance(session_id, "start_service")

    reply_ar = _build_reply_ar(intent, rec)
    om.append_turn(session_id, "assistant", reply_ar, {"recommendation": rec})
    return {
        "session_id": session_id,
        "intent": intent,
        "recommendation": rec,
        "reply_ar": reply_ar,
        "bundles_hint": sb.list_bundles() if intent == ic.INTENT_ASK_SERVICES else None,
        "demo": True,
    }


def _build_reply_ar(intent: str, rec: dict[str, Any]) -> str:
    sid = rec.get("recommended_service_id")
    name = rec.get("service_name_ar") or sid
    if intent == ic.INTENT_ASK_SERVICES:
        return (
            "أنسب مسار: ابدأ بتشخيص مجاني ثم اختر باقة Growth Starter أو Data to Revenue. "
            "راجع قائمة الباقات من /api/v1/operator/bundles."
        )
    if intent == ic.INTENT_ASK_PROOF:
        return f"Proof Pack مرتبط بخدمة {name} — جاهز كعرض تجريبي بعد أول مسودات موافَق عليها."
    return f"نوصي بخدمة: {name} ({sid}). الخطوة التالية: أكمل المدخلات ثم راجع المسودات قبل أي إرسال."
