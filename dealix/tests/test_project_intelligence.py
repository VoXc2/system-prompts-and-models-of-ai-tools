"""Project intelligence deterministic helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from auto_client_acquisition.v3 import project_intelligence as pi


def test_classify_path():
    assert pi.classify_path("api/main.py") == "api"
    assert pi.classify_path("docs/README.md") == "documentation"


def test_chunk_text_creates_chunks(tmp_path: Path):
    p = tmp_path / "sample.py"
    p.write_text("line\n" * 400, encoding="utf-8")
    docs = pi.scan_project(tmp_path)
    doc = next(d for d in docs if d.path.endswith("sample.py"))
    chunks = pi.chunk_text(doc, max_chars=200, overlap=20)
    assert len(chunks) >= 2


def test_naive_search_returns_results(tmp_path: Path):
    f = tmp_path / "foo.py"
    f.write_text("personal operator daily brief", encoding="utf-8")
    docs = pi.scan_project(tmp_path)
    hits = pi.naive_search(docs, "personal operator", limit=5)
    assert hits


def test_build_index_summary_counts(tmp_path: Path):
    (tmp_path / "a.py").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.md").write_text("beta beta", encoding="utf-8")
    docs = pi.scan_project(tmp_path)
    s = pi.build_index_summary(docs)
    assert s["documents"] >= 1
    assert s["total_chars"] > 0


def test_should_block_embedding_detects_key():
    blocked, reason = pi.should_block_embedding("prefix sk-123456789012345678901234567890")
    assert blocked is True
    assert reason


def test_answer_operator_question():
    out = pi.answer_operator_question("وش أفضل طريقة لاستخدام Supabase؟")
    assert "answer_ar" in out
    assert "semantic_status_ar" in out
