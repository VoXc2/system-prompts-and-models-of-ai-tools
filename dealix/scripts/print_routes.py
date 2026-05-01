#!/usr/bin/env python3
"""Print FastAPI routes and exit non-zero on duplicate (method, path) pairs."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from api.main import create_app  # noqa: E402


def main() -> int:
    app = create_app()
    rows: list[tuple[str, str]] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if path is None or not methods:
            continue
        for method in sorted(m for m in methods if m != "HEAD"):
            rows.append((method, path))

    rows.sort(key=lambda x: (x[1], x[0]))
    print(f"TOTAL_ROUTE_ROWS {len(rows)}")
    for method, path in rows:
        print(f"{method:8} {path}")

    counts = Counter(rows)
    dups = [(k, v) for k, v in counts.items() if v > 1]
    if dups:
        print("\nDUPLICATE_ROUTES", file=sys.stderr)
        for (method, path), n in sorted(dups, key=lambda x: x[0][1]):
            print(f"  {n}x  {method} {path}", file=sys.stderr)
        return 2
    print("\nROUTE_CHECK_OK no duplicate method+path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
