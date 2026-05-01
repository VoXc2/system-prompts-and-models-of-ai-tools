"""
Dealix Copilot — the conversational layer over the Revenue OS.

User asks "وش أسوي اليوم؟" → intent router → answer engine pulls from
Revenue Memory + Revenue Graph + Market Radar → renders Arabic answer
with optional action buttons (each gated by the same orchestrator
policies as autonomous workflows).

Public API:
    from auto_client_acquisition.copilot import (
        Intent, ask, propose_actions,
    )
"""

from auto_client_acquisition.copilot.intent_router import (
    Intent,
    classify_intent,
    list_intents,
)
from auto_client_acquisition.copilot.answer_engine import (
    CopilotAnswer,
    answer,
    explain_metric,
)
from auto_client_acquisition.copilot.safe_actions import (
    SAFE_ACTIONS,
    SafeAction,
    propose_actions,
)

__all__ = [
    "Intent",
    "classify_intent",
    "list_intents",
    "CopilotAnswer",
    "answer",
    "explain_metric",
    "SAFE_ACTIONS",
    "SafeAction",
    "propose_actions",
]


# Convenience high-level entry point
def ask(*, question_ar: str, customer_id: str, context: dict | None = None):
    """One-call entry — classifies intent, builds answer, proposes actions."""
    intent = classify_intent(question_ar)
    ans = answer(intent=intent, question_ar=question_ar, customer_id=customer_id, context=context or {})
    actions = propose_actions(intent=intent, customer_id=customer_id, context=context or {})
    return {
        "intent": intent.intent_id,
        "answer_ar": ans.answer_ar,
        "citations": ans.citations,
        "confidence": ans.confidence,
        "follow_up_questions": ans.follow_up_questions,
        "proposed_actions": [a.to_dict() for a in actions],
    }
