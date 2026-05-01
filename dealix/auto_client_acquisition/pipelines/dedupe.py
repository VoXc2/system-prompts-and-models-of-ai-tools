"""
Dedupe helpers — deterministic + fuzzy.

Match strategies (in priority order):
    1. Exact google_place_id match
    2. Exact normalized domain match
    3. Exact normalized phone (E.164) match
    4. Exact normalized email match
    5. Normalized company-name match (within same city if available)

This is a stdlib-only implementation. It scales fine for tens of thousands of
rows; for hundreds of thousands swap the in-memory dicts for indexed SQL queries.
"""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.pipelines.normalize import (
    fuzzy_company_key,
    normalize_domain,
    normalize_email,
    normalize_saudi_phone,
)


def build_index(accounts: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """
    Build lookup indexes from existing accounts.
    Returns dict with keys: by_place, by_domain, by_phone, by_email, by_name_city.
    Values are dicts mapping key → account_id.
    """
    idx = {
        "by_place": {},
        "by_domain": {},
        "by_phone": {},
        "by_email": {},
        "by_name_city": {},
    }
    for a in accounts:
        aid = a.get("id")
        if not aid:
            continue
        if pid := a.get("google_place_id"):
            idx["by_place"][pid] = aid
        if d := normalize_domain(a.get("domain") or a.get("website")):
            idx["by_domain"][d] = aid
        if p := normalize_saudi_phone(a.get("phone")):
            idx["by_phone"][p] = aid
        if e := normalize_email(a.get("email")):
            idx["by_email"][e] = aid
        nk = fuzzy_company_key(a.get("company_name") or a.get("normalized_name"))
        if nk:
            city = (a.get("city") or "").strip().lower()
            idx["by_name_city"][f"{nk}|{city}"] = aid
            idx["by_name_city"][f"{nk}|"] = aid  # also without city for cross-city match
    return idx


def find_match(
    normalized: dict[str, Any],
    indexes: dict[str, dict[str, str]],
) -> tuple[str | None, str | None]:
    """
    Look up a match in the indexes. Returns (account_id, match_kind) or (None, None).
    """
    if pid := normalized.get("google_place_id"):
        if hit := indexes["by_place"].get(pid):
            return hit, "place_id"
    if d := normalized.get("domain"):
        if hit := indexes["by_domain"].get(d):
            return hit, "domain"
    if p := normalized.get("phone"):
        if hit := indexes["by_phone"].get(p):
            return hit, "phone"
    if e := normalized.get("email"):
        if hit := indexes["by_email"].get(e):
            return hit, "email"
    nk = normalized.get("normalized_name")
    if nk:
        city = (normalized.get("city") or "").strip().lower()
        if hit := indexes["by_name_city"].get(f"{nk}|{city}"):
            return hit, "name_city"
        if hit := indexes["by_name_city"].get(f"{nk}|"):
            return hit, "name_only"
    return None, None
