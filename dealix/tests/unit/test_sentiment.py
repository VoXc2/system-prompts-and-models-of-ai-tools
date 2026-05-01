"""Unit tests for Arabic sentiment."""

from __future__ import annotations

from dealix.intelligence.sentiment import ArabicSentiment


def test_positive():
    s = ArabicSentiment()
    r = s.analyze("الخدمة ممتازة وكفو")
    assert r.label == "positive"
    assert r.score > 0


def test_negative():
    s = ArabicSentiment()
    r = s.analyze("التجربة كانت سيئة وفاشلة")
    assert r.label == "negative"
    assert r.score < 0


def test_neutral():
    s = ArabicSentiment()
    r = s.analyze("السلام عليكم")
    assert r.label == "neutral"


def test_negator_flips_sign():
    s = ArabicSentiment()
    r_pos = s.analyze("الخدمة ممتازة")
    r_neg = s.analyze("الخدمة ما ممتازة")
    assert r_pos.score > 0
    assert r_neg.score < r_pos.score
