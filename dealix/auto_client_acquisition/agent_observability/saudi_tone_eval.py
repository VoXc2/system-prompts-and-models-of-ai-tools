"""Saudi-tone eval — does this message sound natural in a Saudi B2B context?"""

from __future__ import annotations

import re

# Positive markers — natural Saudi conversational tone.
POSITIVE_MARKERS_AR: tuple[str, ...] = (
    "هلا", "أهلاً", "مساء الخير", "صباح الخير",
    "لاحظت", "شفت", "متابع",
    "يناسبك", "تحب", "إذا فيه وقت",
    "تجربة", "Pilot", "بايلوت",
)

# Negative markers — too corporate, too formal, or LLM-generic.
NEGATIVE_MARKERS_AR: tuple[str, ...] = (
    "السيد المحترم", "تحية طيبة وبعد", "ندعوكم لاكتشاف",
    "ابتداءً من تاريخه", "فوراً وعلى وجه السرعة",
    "leverage", "synergy", "best-in-class",
    "نفخر بأن نقدم لكم",
)


def _arabic_ratio(text: str) -> float:
    if not text:
        return 0.0
    arabic = sum(1 for ch in text if "؀" <= ch <= "ۿ")
    total = sum(1 for ch in text if not ch.isspace())
    if total == 0:
        return 0.0
    return arabic / total


def saudi_tone_eval(text: str) -> dict[str, object]:
    """
    Score a message for "natural Saudi tone".

    Returns:
        {
          "score": 0..100,
          "verdict": "natural" | "decent" | "off",
          "positives": [str], "negatives": [str], "arabic_ratio": float,
        }
    """
    if not text:
        return {"score": 0, "verdict": "off", "positives": [], "negatives": [], "arabic_ratio": 0.0}

    positives = [m for m in POSITIVE_MARKERS_AR if m in text]
    negatives = [m for m in NEGATIVE_MARKERS_AR if m in text]
    ratio = _arabic_ratio(text)

    score = 30  # base
    score += min(50, len(positives) * 12)
    score -= min(60, len(negatives) * 20)
    if ratio >= 0.6:
        score += 20
    elif ratio >= 0.3:
        score += 10
    score = max(0, min(100, score))

    # Length penalty for huge messages.
    word_count = len(re.split(r"\s+", text.strip()))
    if word_count > 80:
        score = max(0, score - 10)

    if score >= 75:
        verdict = "natural"
    elif score >= 50:
        verdict = "decent"
    else:
        verdict = "off"

    return {
        "score": score,
        "verdict": verdict,
        "positives": positives,
        "negatives": negatives,
        "arabic_ratio": round(ratio, 3),
    }
