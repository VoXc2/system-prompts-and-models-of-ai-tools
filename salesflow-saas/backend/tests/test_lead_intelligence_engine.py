"""Lead intelligence — دمج، CSV، قدرات (بدون مفاتيح خارجية)."""

from app.services.lead_intelligence_engine import (
    merge_dedupe,
    parse_leads_csv,
    engine_capabilities,
)


def test_merge_dedupe_by_phone():
    a = [
        {"name": "A", "phone": "+966501112233", "website": ""},
        {"name": "A2", "phone": "966501112233", "website": ""},
        {"name": "B", "phone": "+966507778899", "website": ""},
    ]
    out = merge_dedupe(a)
    assert len(out) == 2


def test_parse_leads_csv_basic():
    raw = "company_name,phone\nشركة الاختبار,+966501112233\n".encode("utf-8")
    rows, warns = parse_leads_csv(raw)
    assert len(rows) == 1
    assert rows[0].get("phone")
    assert rows[0].get("name") == "شركة الاختبار"


def test_engine_capabilities_shape():
    c = engine_capabilities()
    assert "google_places" in c
    assert "sources" in c
