from app.ai.evolution.signals import collect_evolution_signals, evolution_signals_for_flow


def test_collect_evolution_signals_shape():
    s = collect_evolution_signals()
    assert "agent_framework_versions" in s
    assert "autogen_import_ok" in s


def test_evolution_signals_for_flow():
    lst = evolution_signals_for_flow()
    assert len(lst) == 1
    assert lst[0]["source"] == "dealix_agent_framework_snapshot"
    assert "payload" in lst[0]
