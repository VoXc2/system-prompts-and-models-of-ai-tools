"""Unit tests for dealix.intelligence.arabic_nlp."""

from __future__ import annotations

from dealix.intelligence.arabic_nlp import ArabicNLP, normalize_arabic, segment_arabic


def test_normalize_removes_diacritics():
    n = normalize_arabic("مَرْحَبَاً")
    # tashkeel and tatweel removed, alef retained
    assert n == "مرحبا"


def test_normalize_hamza():
    assert normalize_arabic("إحسان أمر آسف") == "احسان امر اسف"


def test_normalize_taa_marbuta():
    assert normalize_arabic("مؤسسة") == "مؤسسه"


def test_segment_returns_tokens():
    tokens = segment_arabic("مرحبا بك في دياليكس")
    assert len(tokens) >= 3


def test_arabic_nlp_is_arabic():
    nlp = ArabicNLP()
    assert nlp.is_arabic("مرحبا بك")
    assert not nlp.is_arabic("hello world")
