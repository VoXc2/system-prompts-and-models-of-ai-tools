"""
Arabic-capable extractive text helpers.

If the optional ``mukhtasar`` package is installed (private wheel / future PyPI),
its summarization entrypoints are used when available. Otherwise a fast
extractive fallback runs in-process (typical latency << 500ms for moderate input).
"""

from __future__ import annotations

import importlib
import logging
import re
from typing import Any, Callable

logger = logging.getLogger("dealix.text_intelligence.processor")

_MAX_CHARS_DEFAULT = 12_000

_mukhtasar_mod: Any = None
for _candidate in ("mukhtasar",):
    try:
        _mukhtasar_mod = importlib.import_module(_candidate)
        logger.info("text_processor: loaded optional module %s", _candidate)
        break
    except ImportError:
        continue


_AR_SENT_SPLIT = re.compile(r"(?<=[\.\!\?\n؟])\s+|(?<=\n)")


def _split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = _AR_SENT_SPLIT.split(text)
    return [p.strip() for p in parts if p and len(p.strip()) > 2]


# Minimal Arabic + Latin stopwords for frequency scoring (extractive baseline)
_STOP = frozenset(
    """
    و في من على الى عن أن ما مع إلى لا أو هل كيف هذا هذه ذلك التي الذي
    هناك حيث أيضا قد كان كانت يكون تم كما بين عند عندما بعد قبل
    the a an is are was were be been being of to in for on at by and or not
    """.split()
)


def _tokenize(s: str) -> list[str]:
    return re.findall(r"[\u0600-\u06FFA-Za-z0-9]+", s.lower())


def _sentence_scores(text: str) -> list[tuple[str, float]]:
    sentences = _split_sentences(text)
    if not sentences:
        return []
    word_freq: dict[str, float] = {}
    for s in sentences:
        for w in _tokenize(s):
            if w in _STOP or len(w) < 2:
                continue
            word_freq[w] = word_freq.get(w, 0.0) + 1.0

    ranked: list[tuple[str, float]] = []
    for s in sentences:
        score = 0.0
        for w in _tokenize(s):
            if w in _STOP:
                continue
            score += word_freq.get(w, 0.0)
        # Prefer mid-length sentences
        ntok = max(1, len(_tokenize(s)))
        norm = score / (ntok**0.5)
        ranked.append((s, norm))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def _try_mukhtasar_summarize(text: str, max_sentences: int) -> str | None:
    if _mukhtasar_mod is None:
        return None
    for name in ("summarize_text", "summarize", "mukhtasar", "compress"):
        fn: Callable[..., Any] | None = getattr(_mukhtasar_mod, name, None)
        if not callable(fn):
            continue
        try:
            out = fn(text, max_sentences=max_sentences)
        except TypeError:
            try:
                out = fn(text)
            except Exception:
                continue
        except Exception:
            logger.exception("mukhtasar callable %s failed", name)
            continue
        if out:
            return str(out).strip()
    return None


def summarize_text(text: str, max_sentences: int = 3, max_chars: int = 1200) -> str:
    """Return a short summary; prefers Mukhtasar when installed."""
    text = (text or "")[:_MAX_CHARS_DEFAULT].strip()
    if not text:
        return ""

    ext = _try_mukhtasar_summarize(text, max_sentences)
    if ext:
        return ext[:max_chars]

    ranked = _sentence_scores(text)
    if not ranked:
        return text[:max_chars]

    picked: list[str] = []
    for sent, _ in ranked:
        if sent in picked:
            continue
        picked.append(sent)
        if len(picked) >= max_sentences:
            break
    out = " ".join(picked).strip()
    if len(out) > max_chars:
        out = out[: max_chars - 1] + "…"
    return out


def rank_sentences(text: str) -> list[tuple[str, float]]:
    """Ordered (sentence, score) highest first."""
    text = (text or "")[:_MAX_CHARS_DEFAULT].strip()
    if not text:
        return []
    return _sentence_scores(text)


def extract_key_sentences(text: str, n: int = 5) -> list[str]:
    """Top-N informative sentences (extractive)."""
    ranked = rank_sentences(text)
    out: list[str] = []
    for sent, _ in ranked:
        if sent not in out:
            out.append(sent)
        if len(out) >= n:
            break
    return out
