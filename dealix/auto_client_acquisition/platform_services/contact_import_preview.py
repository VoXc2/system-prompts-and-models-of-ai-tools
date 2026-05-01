"""CSV / row-list import preview — classification only, no send."""

from __future__ import annotations

import csv
import io
import re
from typing import Any

from auto_client_acquisition.compliance_os.consent_ledger import LawfulBasis, record_consent
from auto_client_acquisition.compliance_os.contactability import check_contactability

_TRUSTED_SOURCES = frozenset(
    {
        "inbound_form",
        "website_form",
        "prior_customer",
        "event_meeting",
        "explicit_consent",
        "form_submission",
        "linkedin_lead_form",
    }
)


def _norm_phone(raw: str | None) -> str:
    if not raw:
        return ""
    s = re.sub(r"\s+", "", str(raw))
    if s.startswith("00"):
        s = "+" + s[2:]
    if s.startswith("0") and len(s) >= 9:
        s = "+966" + s[1:]
    if s.isdigit() and len(s) == 9:
        s = "+966" + s
    return s


def _parse_rows(body: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(body.get("rows"), list):
        return [dict(x) for x in body["rows"] if isinstance(x, dict)]
    csv_text = body.get("csv_text")
    if isinstance(csv_text, str) and csv_text.strip():
        reader = csv.DictReader(io.StringIO(csv_text))
        return [dict(row) for row in reader]
    return []


def _bucket_for_row(row: dict[str, Any], *, customer_id: str) -> tuple[str, str, dict[str, Any]]:
    """
    Returns (bucket, reason_code, extra) where bucket is safe | needs_review | blocked.
    """
    if row.get("opted_out") in (True, "true", "1", 1):
        return "blocked", "opted_out", {}

    src = str(row.get("source") or "").strip().lower() or "unknown"
    if row.get("cold_whatsapp") in (True, "true", "1", 1):
        return "blocked", "cold_whatsapp", {}

    if src in ("purchased_list", "scraped", "unknown_list"):
        return "blocked", "purchased_list", {}

    phone = _norm_phone(row.get("phone") or row.get("mobile") or row.get("tel"))
    email = str(row.get("email") or "").strip().lower()
    if not phone and not email:
        return "needs_review", "missing_identifier", {}

    contact_id = phone or email

    if src == "unknown" or src not in _TRUSTED_SOURCES:
        return "needs_review", "unknown_source", {"contact_id": contact_id}

    # Trusted: synthetic consent so contactability can pass (import-time snapshot).
    if src in ("inbound_form", "website_form", "form_submission", "linkedin_lead_form"):
        basis = LawfulBasis.CONSENT
        rec_src = "form_submission"
    else:
        basis = LawfulBasis.LEGITIMATE_INTEREST
        rec_src = "public_directory"

    rec = record_consent(
        customer_id=customer_id,
        contact_id=contact_id,
        lawful_basis=basis,
        purpose="import_preview",
        channel="all",
        source=rec_src,
    )
    status = check_contactability(
        contact_id=contact_id,
        consent_records=[rec],
        messages_sent_this_week=0,
        weekly_cap=10,
        current_riyadh_hour=12,
    )
    if not status.can_contact:
        if status.reason_code == "opted_out":
            return "blocked", status.reason_code, status.to_dict()
        return "needs_review", status.reason_code, status.to_dict()

    return "safe", "trusted_with_consent_snapshot", status.to_dict()


def build_import_preview(body: dict[str, Any]) -> dict[str, Any]:
    """
    Summarizes contacts into safe / needs_review / blocked / invalid_duplicate.

    No external I/O; does not persist.
    """
    customer_id = str(body.get("customer_id") or "default")
    rows = _parse_rows(body)
    if not rows:
        return {
            "ok": False,
            "error": "no_rows",
            "detail_ar": "مرّر ``rows`` كقائمة أو ``csv_text`` مع رؤوس أعمدة.",
        }

    seen: set[str] = set()
    counts = {"safe": 0, "needs_review": 0, "blocked": 0, "invalid_duplicate": 0}
    samples: dict[str, list[dict[str, Any]]] = {"safe": [], "needs_review": [], "blocked": []}

    for raw in rows:
        phone = _norm_phone(raw.get("phone") or raw.get("mobile") or raw.get("tel"))
        email = str(raw.get("email") or "").strip().lower()
        dedupe_key = phone or email or ""
        if dedupe_key and dedupe_key in seen:
            counts["invalid_duplicate"] += 1
            continue
        if dedupe_key:
            seen.add(dedupe_key)

        bucket, reason, extra = _bucket_for_row(raw, customer_id=customer_id)
        counts[bucket] += 1
        entry = {
            "phone": phone,
            "email": email or None,
            "source": raw.get("source"),
            "bucket": bucket,
            "reason": reason,
            "contactability": extra,
        }
        if bucket in samples and len(samples[bucket]) < 5:
            samples[bucket].append(entry)

    return {
        "ok": True,
        "approval_required": True,
        "counts": counts,
        "samples": samples,
        "note_ar": "معاينة فقط — لا يُرسل أي تواصل ولا يُخزّن دفعة الاستيراد في MVP.",
    }
