from app.services.agent_framework_report import build_agent_framework_report


def test_agent_framework_report_shape():
    r = build_agent_framework_report()
    assert "python" in r
    assert "packages" in r
    assert "autogen_import_ok" in r
    assert isinstance(r["packages"], dict)
