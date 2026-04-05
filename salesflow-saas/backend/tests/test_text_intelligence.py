"""Unit tests for Arabic text intelligence (no external Mukhtasar required)."""

from app.services.text_intelligence.service import analyze_arabic_text, analyze_market_corpus
from app.services.text_intelligence.text_processor import extract_key_sentences, summarize_text


def test_summarize_non_empty():
    t = "نحتاج نظام CRM. السعر مهم جداً. نريد التفعيل هذا الأسبوع."
    s = summarize_text(t, max_sentences=2)
    assert len(s) > 5


def test_extract_key_sentences():
    t = "الجملة الأولى. الجملة الثانية بكلمات أكثر تكراراً تكراراً. الثالثة قصيرة."
    ks = extract_key_sentences(t, n=2)
    assert len(ks) >= 1


def test_analyze_arabic_pricing_intent():
    text = "ما هو سعر الاشتراك الشهري؟ نحتاج عرض سعر لمائة مستخدم."
    out = analyze_arabic_text(text, context="test", input_kind="unit")
    assert out["intent"] in ("pricing", "inquiry", "purchase_intent")
    assert "confidence_score" in out
    assert 0 <= out["confidence_score"] <= 1
    assert out.get("suggested_reply")


def test_analyze_empty():
    out = analyze_arabic_text("", context="test", input_kind="unit")
    assert out["intent"] == "unknown"
    assert out["confidence_score"] <= 0.3


def test_market_aggregate():
    texts = ["السعر غالي", "نريد تحسين الأداء", "عرض جديد هذا الشهر"]
    agg = analyze_market_corpus(texts, scope="reviews")
    assert "market_insights" in agg
    assert agg["doc_count"] == 3
