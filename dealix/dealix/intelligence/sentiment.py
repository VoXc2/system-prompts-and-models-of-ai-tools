"""
Arabic sentiment analysis — lexicon-based with optional arabert fallback.
تحليل المشاعر بالعربية.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from dealix.intelligence.arabic_nlp import normalize_arabic, segment_arabic

# Compact Saudi-dialect sentiment lexicon (already normalized: hamza→alef, taa→haa).
# Weights in [-1, 1].
_POS_RAW = {
    "ممتاز": 1.0,
    "ممتازة": 1.0,
    "رائع": 1.0,
    "رائعة": 1.0,
    "حلو": 0.8,
    "حلوة": 0.8,
    "جيد": 0.7,
    "جيدة": 0.7,
    "مناسب": 0.6,
    "شكرا": 0.9,
    "فخور": 0.9,
    "عجبني": 0.9,
    "احسنتم": 0.9,
    "ابدع": 0.9,
    "اعجبني": 0.9,
    "زين": 0.7,
    "كفو": 0.9,
    "يعطيك": 0.6,
    "طيب": 0.5,
}
_NEG_RAW = {
    "سيء": -1.0,
    "سيئة": -1.0,
    "فاشل": -1.0,
    "فاشلة": -1.0,
    "ضعيف": -0.9,
    "زعلان": -0.9,
    "مخيب": -0.9,
    "مزعج": -0.8,
    "تافه": -1.0,
    "رديء": -1.0,
    "ما عجبني": -0.9,
    "ما يسوى": -1.0,
    "غلط": -0.6,
    "مشكله": -0.7,
    "مشكلة": -0.7,
    "بطيء": -0.6,
    "غالي": -0.5,
    "معقد": -0.5,
}


def _build_normalized(d: dict[str, float]) -> dict[str, float]:
    return {normalize_arabic(k): v for k, v in d.items()}


_POS = _build_normalized(_POS_RAW)
_NEG = _build_normalized(_NEG_RAW)
_NEGATORS = {"ما", "مو", "ليس", "لا", "مب"}


@dataclass
class SentimentResult:
    label: Literal["positive", "neutral", "negative"]
    score: float  # in [-1, 1]
    confidence: float


class ArabicSentiment:
    def analyze(self, text: str) -> SentimentResult:
        if not text or not text.strip():
            return SentimentResult("neutral", 0.0, 0.0)

        tokens = segment_arabic(normalize_arabic(text))
        score = 0.0
        hits = 0
        for i, tok in enumerate(tokens):
            lex_score = _POS.get(tok, _NEG.get(tok, 0.0))
            if lex_score:
                # Check preceding negator
                if i > 0 and tokens[i - 1] in _NEGATORS:
                    lex_score = -lex_score
                score += lex_score
                hits += 1

        if hits == 0:
            return SentimentResult("neutral", 0.0, 0.15)

        avg = score / hits
        label: Literal["positive", "neutral", "negative"]
        if avg > 0.15:
            label = "positive"
        elif avg < -0.15:
            label = "negative"
        else:
            label = "neutral"
        confidence = min(1.0, abs(avg) * (1 + 0.1 * hits))
        return SentimentResult(label, round(avg, 3), round(confidence, 3))
