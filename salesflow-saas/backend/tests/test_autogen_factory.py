"""تهيئة AutoGen — تُتخطى تلقائياً إن لم تُثبَّت autogen-agentchat (مثلاً بيئة قديمة)."""

import pytest


def test_autogen_packages_importable():
    pytest.importorskip("autogen_agentchat")
    import autogen_agentchat
    import autogen_ext

    assert autogen_agentchat.__version__
    assert autogen_ext.__version__


def test_factory_none_without_llm_keys(monkeypatch):
    pytest.importorskip("autogen_agentchat")
    from app.config import get_settings

    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GROQ_API_KEY", "")
    get_settings.cache_clear()
    from app.ai.autogen.factory import dealix_autogen_openai_client

    assert dealix_autogen_openai_client() is None
