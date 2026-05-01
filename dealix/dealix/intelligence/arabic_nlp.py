"""
Arabic NLP helpers — normalization, diacritics, tokenization.
أدوات معالجة اللغة العربية — التطبيع، التشكيل، التقطيع.

Optional deps: pyarabic, camel-tools. Gracefully degrades without them.
"""

from __future__ import annotations

import re
import unicodedata

try:
    from pyarabic import araby  # type: ignore

    _HAS_PYARABIC = True
except ImportError:  # pragma: no cover
    _HAS_PYARABIC = False

# Regex for common Arabic operations
_RE_TATWEEL = re.compile("\u0640")
_RE_DIACRITICS = re.compile("[\u0610-\u061a\u064b-\u065f\u06d6-\u06ed]")
_RE_NON_ARABIC = re.compile(r"[^\u0600-\u06FF\s]")


def normalize_arabic(
    text: str,
    *,
    strip_tashkeel: bool = True,
    strip_tatweel: bool = True,
    normalize_hamza: bool = True,
    normalize_taa: bool = True,
) -> str:
    """Normalize Arabic text for consistent matching."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)

    if strip_tatweel:
        text = _RE_TATWEEL.sub("", text)
    if strip_tashkeel:
        text = _RE_DIACRITICS.sub("", text)

    if normalize_hamza:
        text = text.translate(str.maketrans({"إ": "ا", "أ": "ا", "آ": "ا", "ٱ": "ا"}))
    if normalize_taa:
        text = text.replace("ة", "ه")
    # Normalize alef maksura to yaa
    text = text.replace("ى", "ي")
    return text.strip()


def segment_arabic(text: str) -> list[str]:
    """Tokenize Arabic text into words, preserving punctuation-free segments."""
    if _HAS_PYARABIC:
        return araby.tokenize(text)
    # Fallback: whitespace split after stripping punctuation
    return [w for w in re.split(r"\s+", text) if w]


def arabic_ratio(text: str) -> float:
    if not text:
        return 0.0
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    return arabic_chars / max(len(text), 1)


class ArabicNLP:
    """High-level Arabic NLP interface."""

    def normalize(self, text: str) -> str:
        return normalize_arabic(text)

    def tokens(self, text: str) -> list[str]:
        return segment_arabic(normalize_arabic(text))

    def is_arabic(self, text: str, threshold: float = 0.3) -> bool:
        return arabic_ratio(text) >= threshold

    def stem(self, word: str) -> str:  # pragma: no cover
        if _HAS_PYARABIC:
            return araby.strip_diacritics(word)
        return word
