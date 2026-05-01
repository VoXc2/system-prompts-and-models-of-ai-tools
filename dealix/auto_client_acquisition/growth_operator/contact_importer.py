"""
Contact Importer — safely intake uploaded customer phone/email lists.

Steps:
  1. normalize_phone — Saudi-friendly E.164 normalizer
  2. dedupe_contacts — drop exact phone duplicates (keep richest record)
  3. classify_contact_source — existing / lead / inbound / event / cold / unknown
  4. detect_opt_out — flags contacts marked as opted-out / blocked
  5. summarize_import — top-level report ready for the dashboard
"""

from __future__ import annotations

import re
from typing import Any

# ── Phone normalization ──────────────────────────────────────────
_DIGITS_RE = re.compile(r"\D+")


def normalize_phone(raw: str | None) -> str:
    """
    Normalize Saudi phone numbers to E.164-like form starting with 966.

    Accepts: +966500000001, 0500000001, 500000001, 00966500000001,
             +966 (50) 000-0001, etc.
    Returns: bare digits (e.g. "966500000001") or "" if invalid.
    """
    if not raw:
        return ""
    s = _DIGITS_RE.sub("", str(raw))
    if not s:
        return ""
    # Strip leading 00 (international prefix)
    if s.startswith("00"):
        s = s[2:]
    # Already starts with 966
    if s.startswith("966") and len(s) == 12:
        return s
    # Local 0-prefixed (e.g. 0512345678)
    if s.startswith("0") and len(s) == 10:
        return "966" + s[1:]
    # Bare 9-digit local mobile (e.g. 512345678)
    if len(s) == 9 and s.startswith("5"):
        return "966" + s
    # Already bare with country code but no leading +
    if len(s) == 12 and s.startswith("966"):
        return s
    return s if 10 <= len(s) <= 15 else ""


# ── Dedup ────────────────────────────────────────────────────────
def dedupe_contacts(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Drop exact phone duplicates. When two records share a phone, keep the one
    with more non-empty fields (richer record).
    """
    seen: dict[str, dict[str, Any]] = {}
    for c in contacts:
        phone = normalize_phone(c.get("phone", ""))
        if not phone:
            # Records with no phone are kept as-is, keyed by name+email
            key = f"name:{c.get('name','').strip().lower()}|email:{c.get('email','').strip().lower()}"
            if key not in seen:
                seen[key] = c
            continue
        c_norm = dict(c)
        c_norm["phone"] = phone
        existing = seen.get(phone)
        if existing is None:
            seen[phone] = c_norm
        else:
            existing_filled = sum(1 for v in existing.values() if v)
            new_filled = sum(1 for v in c_norm.values() if v)
            if new_filled > existing_filled:
                seen[phone] = c_norm
    return list(seen.values())


# ── Source classification ────────────────────────────────────────
SOURCE_LABELS: tuple[str, ...] = (
    "existing_customer",
    "old_lead",
    "inbound_lead",
    "event_lead",
    "cold_list",
    "referral",
    "unknown",
)


def classify_contact_source(contact: dict[str, Any]) -> str:
    """Classify a contact's source. Conservative: unknown by default."""
    src = str(contact.get("source", "")).lower().strip()
    rel = str(contact.get("relationship_status", "")).lower().strip()
    last = contact.get("last_contacted_at")

    if rel in ("existing", "customer", "client", "active") or src in (
        "existing_customer", "customer", "active_customer",
    ):
        return "existing_customer"
    if rel in ("inbound", "form_submission") or src in (
        "inbound", "website_form", "form_submission",
    ):
        return "inbound_lead"
    if src in ("event", "exhibition", "conference", "trade_show"):
        return "event_lead"
    if src in ("referral", "introduction"):
        return "referral"
    if rel in ("lead", "prospect") or last:
        return "old_lead"
    if src in ("cold", "scraped", "purchased_list"):
        return "cold_list"
    return "unknown"


# ── Opt-out detection ────────────────────────────────────────────
_OPT_OUT_TOKENS = {
    "opt_out", "opted_out", "unsubscribed", "blocked", "do_not_contact",
    "stop", "remove", "إلغاء", "اشتراك", "ايقاف", "إيقاف",
}


def detect_opt_out(contact: dict[str, Any]) -> bool:
    """Return True if the record is flagged as opted-out / blocked."""
    flag = str(contact.get("opt_in_status", "")).lower().strip()
    if flag in _OPT_OUT_TOKENS:
        return True
    if str(contact.get("status", "")).lower() in _OPT_OUT_TOKENS:
        return True
    notes = str(contact.get("notes", "")).lower()
    if any(tok in notes for tok in _OPT_OUT_TOKENS):
        return True
    return False


# ── Summary ──────────────────────────────────────────────────────
def summarize_import(contacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Top-level report for the upload dashboard. Pure function."""
    total = len(contacts)
    deduped = dedupe_contacts(contacts)
    by_source: dict[str, int] = {label: 0 for label in SOURCE_LABELS}
    opt_out_count = 0
    invalid_phone = 0

    for c in deduped:
        if detect_opt_out(c):
            opt_out_count += 1
        if not c.get("phone") or len(str(c.get("phone"))) < 9:
            invalid_phone += 1
        src = classify_contact_source(c)
        by_source[src] = by_source.get(src, 0) + 1

    return {
        "raw_total": total,
        "after_dedupe": len(deduped),
        "duplicates_removed": total - len(deduped),
        "invalid_phone": invalid_phone,
        "opt_out_count": opt_out_count,
        "by_source": by_source,
        "ready_to_review": len(deduped) - opt_out_count - invalid_phone,
    }
