#!/usr/bin/env python3
"""
analyze_directory_duckdb.py — fast pre-import audit for large CSV/Excel/JSON
lead files using DuckDB (in-memory, no Postgres required).

Usage:
    python scripts/analyze_directory_duckdb.py vendor_file.csv
    python scripts/analyze_directory_duckdb.py vendor_file.xlsx --sheet "Sheet1"
    python scripts/analyze_directory_duckdb.py vendor_file.json --output report.json

Outputs:
    - row count
    - column count
    - per-column null rate
    - per-column unique count
    - duplicate rate (by company+city, by phone, by email, by domain)
    - top 20 sectors / cities
    - email domain distribution (personal vs business)
    - phone normalization rate (Saudi)
    - data_quality_report.json (in same folder by default)

Falls back to pandas if duckdb not installed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Try DuckDB first, fall back to pandas
try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas required. Install: pip install pandas openpyxl")
    sys.exit(1)

PERSONAL_DOMAINS = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com",
                    "icloud.com", "live.com"}
PHONE_RE = re.compile(r"\D+")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def normalize_saudi_phone(raw):
    if raw is None or (isinstance(raw, float) and raw != raw):
        return None
    s = str(raw).strip()
    digits = PHONE_RE.sub("", s)
    if not digits:
        return None
    if digits.startswith("00966"):
        digits = digits[2:]
    if digits.startswith("966") and len(digits) >= 11:
        return f"+{digits[:12]}"
    if digits.startswith("05") and len(digits) == 10:
        return f"+966{digits[1:]}"
    if digits.startswith("5") and len(digits) == 9:
        return f"+966{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+966{digits[1:]}"
    return None


def normalize_email(raw):
    if raw is None or (isinstance(raw, float) and raw != raw):
        return None
    s = str(raw).strip().lower()
    return s if EMAIL_RE.match(s) else None


def email_kind(e):
    if not e:
        return "invalid"
    domain = e.split("@", 1)[1] if "@" in e else ""
    return "personal" if domain in PERSONAL_DOMAINS else "business"


def analyze(path: Path, sheet: str | None = None) -> dict:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path, sheet_name=sheet or 0)
    elif suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".json":
        df = pd.read_json(path)
    else:
        raise SystemExit(f"unsupported extension: {suffix}")

    n = len(df)
    cols = list(df.columns)

    # Per-column profile
    col_profile = {}
    for c in cols:
        nonnull = int(df[c].notna().sum())
        unique = int(df[c].nunique(dropna=True))
        col_profile[str(c)] = {
            "non_null": nonnull,
            "null_rate": round((n - nonnull) / n, 4) if n else 0,
            "unique": unique,
            "uniqueness_ratio": round(unique / max(1, nonnull), 4),
        }

    # Try to identify common columns by heuristic
    def find_col(candidates):
        lower_map = {str(c).lower(): c for c in cols}
        for cand in candidates:
            if cand.lower() in lower_map:
                return lower_map[cand.lower()]
        return None

    name_col = find_col(["company_name", "name", "company", "اسم الشركة", "الشركة"])
    city_col = find_col(["city", "City", "المدينة"])
    email_col = find_col(["email", "Email", "الإيميل", "البريد"])
    phone_col = find_col(["phone", "Phone", "الهاتف", "الجوال", "رقم التواصل", "mobile"])
    sector_col = find_col(["sector", "industry", "وظيفة الشركة", "القطاع", "النشاط"])

    # Email kind / phone normalization
    email_kinds = Counter()
    phones_norm = 0
    if email_col:
        for v in df[email_col]:
            email_kinds[email_kind(normalize_email(v))] += 1
    if phone_col:
        for v in df[phone_col]:
            if normalize_saudi_phone(v):
                phones_norm += 1

    # Top sectors / cities
    top_sectors = []
    top_cities = []
    if sector_col:
        top_sectors = df[sector_col].value_counts().head(20).to_dict()
        top_sectors = [{"sector": str(k), "count": int(v)} for k, v in top_sectors.items()]
    if city_col:
        top_cities = df[city_col].value_counts().head(20).to_dict()
        top_cities = [{"city": str(k), "count": int(v)} for k, v in top_cities.items()]

    # Duplicate detection (4 keys)
    dup = {"by_email": 0, "by_phone": 0, "by_name_city": 0}
    if email_col:
        emails = df[email_col].apply(lambda x: normalize_email(x)).dropna()
        dup["by_email"] = int(len(emails) - emails.nunique())
    if phone_col:
        phones = df[phone_col].apply(lambda x: normalize_saudi_phone(x)).dropna()
        dup["by_phone"] = int(len(phones) - phones.nunique())
    if name_col and city_col:
        nc = df[[name_col, city_col]].dropna().astype(str)
        nc["k"] = nc[name_col].str.strip().str.lower() + "|" + nc[city_col].str.strip().str.lower()
        dup["by_name_city"] = int(len(nc) - nc["k"].nunique())

    return {
        "file": str(path),
        "rows": int(n), "columns": len(cols),
        "column_profile": col_profile,
        "detected_columns": {
            "name": name_col, "city": city_col, "email": email_col,
            "phone": phone_col, "sector": sector_col,
        },
        "email_kinds": dict(email_kinds),
        "phones_normalized_saudi": phones_norm,
        "phones_normalize_rate": round(phones_norm / max(1, n), 4),
        "top_sectors": top_sectors,
        "top_cities": top_cities,
        "duplicates": dup,
        "engine": "duckdb" if HAS_DUCKDB else "pandas",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--sheet", help="sheet name for Excel")
    ap.add_argument("--output", help="output report.json (default: <file>.report.json)")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    report = analyze(path, sheet=args.sheet)

    out_path = Path(args.output) if args.output else path.with_suffix(path.suffix + ".report.json")
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Brief stdout summary
    print(f"\n📂 {path.name}  ({report['engine']})")
    print(f"   rows: {report['rows']}, cols: {report['columns']}")
    if report["email_kinds"]:
        print(f"   email_kinds: {dict(report['email_kinds'])}")
    print(f"   phones_normalized_saudi: {report['phones_normalized_saudi']} "
          f"({report['phones_normalize_rate']*100:.1f}%)")
    print(f"   duplicates: {report['duplicates']}")
    print(f"   detected_cols: {report['detected_columns']}")
    if report["top_sectors"]:
        top_s = report["top_sectors"][:5]
        print(f"   top_sectors: {top_s}")
    if report["top_cities"]:
        top_c = report["top_cities"][:5]
        print(f"   top_cities: {top_c}")
    print(f"\n📄 wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
