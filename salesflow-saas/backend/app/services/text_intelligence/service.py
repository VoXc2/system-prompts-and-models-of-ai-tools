"""Production text intelligence facade — structured JSON for CRM, scoring, and automation."""

from __future__ import annotations

import hashlib
import logging
import re
import time
from typing import Any, Optional

from app.services.text_intelligence import heuristics as H
from app.services.text_intelligence.text_processor import extract_key_sentences, summarize_text

logger = logging.getLogger("dealix.text_intelligence")

_PHONE_RE = re.compile(r"(\+?\d[\d\s\-]{7,}\d)")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def mask_sensitive(text: str) -> str:
    """Mask obvious PII for logs and optional storage — not a full DLP suite."""
    if not text:
        return ""
    t = _PHONE_RE.sub("[phone]", text)
    t = _EMAIL_RE.sub("[email]", t)
    return t


def _hash_fp(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:32]


def analyze_arabic_text(
    text: str,
    *,
    context: str = "lead",
    input_kind: str = "unspecified",
) -> dict[str, Any]:
    """
    Input: Arabic (and mixed) business text.
    Output keys match the product contract; never includes raw message in output dict.
    """
    t0 = time.perf_counter()
    raw_len = len(text or "")
    text = (text or "").strip()
    if not text:
        return _empty_result(reason="empty_input")

    text = text[:16_384]

    try:
        masked_for_log = mask_sensitive(text[:500])
        intent = H.classify_intent(text)
        urgency = H.urgency_level(text)
        pains = H.extract_pain_points(text)
        products = H.product_interest_keywords(text)
        sentiment = H.sentiment_label(text)
        stage = H.buying_stage(text)
        conf = H.confidence_from_signals(text, intent)
        summary = summarize_text(text, max_sentences=3, max_chars=900)
        key_sents = extract_key_sentences(text, n=4)
        actions = H.suggest_sales_actions(intent, urgency, stage)

        lead_score_estimate = min(100, int(round(conf * 100)))

        out: dict[str, Any] = {
            "summary": summary,
            "intent": intent,
            "urgency_level": urgency,
            "pain_points": pains,
            "product_interest": products,
            "sentiment": sentiment,
            "buying_stage": stage,
            "confidence_score": conf,
            "lead_score_estimate": lead_score_estimate,
            "key_sentences": key_sents,
            "opportunity_signals": _opportunity_signals(text, intent, urgency, stage),
            "suggested_reply": actions["suggested_reply"],
            "follow_up_suggestion": actions["follow_up_suggestion"],
            "offer_suggestion": actions["offer_suggestion"],
            "next_action": actions["next_action"],
            "_meta": {
                "context": context,
                "input_kind": input_kind,
                "input_sha256_fp": _hash_fp(text),
                "input_chars": raw_len,
                "processor": "mukhtasar_or_extractive",
            },
        }

        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            "text_intelligence.analyze_ok",
            extra={
                "input_chars": raw_len,
                "processing_ms": round(elapsed_ms, 2),
                "confidence": conf,
                "intent": intent,
                "context": context,
                "masked_preview": masked_for_log,
            },
        )
        if elapsed_ms > 500:
            logger.warning(
                "text_intelligence.slow_path",
                extra={"processing_ms": round(elapsed_ms, 2), "input_chars": raw_len},
            )
        return out

    except Exception:
        logger.exception("text_intelligence.analyze_failed", extra={"input_chars": raw_len})
        return _empty_result(reason="processor_error", partial=True)


def _opportunity_signals(text: str, intent: str, urgency: str, stage: str) -> list[str]:
    sig: list[str] = []
    if urgency == "high":
        sig.append("urgency_high")
    if intent == H.INTENT_PURCHASE:
        sig.append("purchase_language")
    if stage == "decision":
        sig.append("late_stage_language")
    if len(H.product_interest_keywords(text, limit=12)) >= 2:
        sig.append("product_focus")
    return sig


def _empty_result(reason: str, partial: bool = False) -> dict[str, Any]:
    return {
        "summary": "",
        "intent": H.INTENT_UNKNOWN,
        "urgency_level": "low",
        "pain_points": [],
        "product_interest": [],
        "sentiment": "neutral",
        "buying_stage": "unknown",
        "confidence_score": 0.1,
        "lead_score_estimate": 10,
        "key_sentences": [],
        "opportunity_signals": [],
        "suggested_reply": "",
        "follow_up_suggestion": "",
        "offer_suggestion": "",
        "next_action": "",
        "_meta": {"error": reason, "partial": partial},
    }


def analyze_market_corpus(texts: list[str], scope: str = "generic") -> dict[str, Any]:
    """Aggregate marketing/competitor/support texts — returns themes only."""
    cleaned = [t[:8_000] for t in texts if t][:200]
    agg = H.market_aggregate_signals(cleaned)
    fp = _hash_fp("\n".join(cleaned))[:40]
    return {
        "scope": scope,
        "source_fingerprint": fp,
        "market_insights": agg,
        "doc_count": len(cleaned),
    }


def strip_raw_for_persistence(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove fields that could duplicate message content at rest."""
    out = dict(payload)
    out.pop("key_sentences", None)
    meta = out.get("_meta")
    if isinstance(meta, dict):
        meta = {k: v for k, v in meta.items() if k != "raw_snippet"}
        out["_meta"] = meta
    return out
