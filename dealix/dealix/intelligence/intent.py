"""
Intent classification — lightweight regex-based classifier.
تصنيف النية — يعتمد على قواعد خفيفة مع إمكانية ترقية إلى Groq Llama.
"""

from __future__ import annotations

from dataclasses import dataclass

from dealix.intelligence.arabic_nlp import normalize_arabic


@dataclass
class IntentResult:
    intent: str
    confidence: float
    matched_keywords: list[str]


# Saudi-dialect + MSA intent cues
_INTENT_CUES: dict[str, list[str]] = {
    "request_quote": ["اسعار", "سعر", "كم", "كلفه", "عرض سعر", "quote", "price", "pricing"],
    "book_demo": ["تجربه", "ديمو", "demo", "موعد", "اجتماع", "booking", "حجز"],
    "ask_integration": ["تكامل", "integration", "hubspot", "calendly", "api", "webhook"],
    "support": ["مشكله", "مشكلة", "خطا", "خطأ", "error", "bug", "لا يعمل", "معطل"],
    "partnership": ["شراكه", "شراكة", "partnership", "وكيل", "ريسلر", "تعاون"],
    "greeting": ["هلا", "مرحبا", "السلام", "اهلا", "hi", "hello"],
    "goodbye": ["باي", "الى اللقاء", "bye", "سلام"],
    "compliment": ["شكرا", "احسنتم", "كفو", "فخور", "رائع"],
    "complaint": ["زعلان", "سيء", "فاشل", "مخيب", "لا انصح"],
}


class IntentClassifier:
    def __init__(self) -> None:
        self.cues = {k: [normalize_arabic(c) for c in v] for k, v in _INTENT_CUES.items()}

    def classify(self, text: str) -> IntentResult:
        if not text or not text.strip():
            return IntentResult("unknown", 0.0, [])

        norm = normalize_arabic(text.lower())
        scores: dict[str, tuple[int, list[str]]] = {}
        for intent, cues in self.cues.items():
            hits: list[str] = []
            for cue in cues:
                if cue in norm:
                    hits.append(cue)
            if hits:
                scores[intent] = (len(hits), hits)

        if not scores:
            return IntentResult("unknown", 0.1, [])

        best = max(scores.items(), key=lambda kv: kv[1][0])
        count, matches = best[1]
        # Confidence: 0.6 + 0.1 per extra match, capped at 0.95
        conf = min(0.95, 0.6 + 0.1 * (count - 1))
        return IntentResult(intent=best[0], confidence=round(conf, 2), matched_keywords=matches)
