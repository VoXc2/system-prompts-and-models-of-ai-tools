"""Unit tests for core.config.models.smart_route."""

from __future__ import annotations

from core.config.models import (
    Provider,
    Task,
    _arabic_ratio,
    ordered_providers,
    smart_route,
)


def test_classification_uses_groq():
    cfg = smart_route(Task.CLASSIFICATION)
    assert cfg.provider == Provider.GROQ


def test_arabic_heavy_routes_to_glm():
    arabic_text = "مرحبا بك في دياليكس، نحن نحتاج مساعدة عاجلة"
    cfg = smart_route(Task.SUMMARY, text_sample=arabic_text)
    assert cfg.provider == Provider.GLM


def test_critical_routes_to_anthropic():
    cfg = smart_route(Task.REASONING, critical=True)
    assert cfg.provider == Provider.ANTHROPIC


def test_code_routes_to_deepseek():
    cfg = smart_route(Task.CODE)
    assert cfg.provider == Provider.DEEPSEEK


def test_research_uses_gemini():
    cfg = smart_route(Task.RESEARCH)
    assert cfg.provider == Provider.GEMINI


def test_arabic_ratio():
    assert _arabic_ratio("") == 0.0
    assert _arabic_ratio("hello") == 0.0
    assert _arabic_ratio("مرحبا") > 0.9


def test_ordered_providers_starts_with_primary():
    chain = ordered_providers(Task.CLASSIFICATION)
    assert chain[0] == Provider.GROQ
    assert len(chain) >= 2
