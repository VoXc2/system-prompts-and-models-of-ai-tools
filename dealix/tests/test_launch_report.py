"""Launch report structure."""

from __future__ import annotations

from auto_client_acquisition.personal_operator.launch_report import build_launch_report, launch_report_markdown_ar


def test_report_has_fifteen_areas():
    report = build_launch_report()
    assert len(report.areas) == 15


def test_score_range():
    report = build_launch_report()
    assert 0 <= report.overall_score <= 100
    for a in report.areas:
        assert 0 <= a.score <= 100


def test_markdown_has_arabic_headers():
    md = launch_report_markdown_ar()
    assert "# تقرير" in md or "تقرير جاهزية" in md
    assert "## ملخص" in md or "ملخص تنفيذي" in md
