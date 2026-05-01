#!/usr/bin/env python3
"""Deterministic JSON-shape evals against in-process FastAPI routes (no LLM keys required).

Usage:
  python scripts/run_evals.py
  python scripts/run_evals.py --suite personal_operator
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import httpx  # noqa: E402

from api.main import create_app  # noqa: E402

_DEFAULT_SUITES = ("personal_operator", "revenue_os")


def _load_cases(name: str) -> list[dict]:
    path = _REPO / "evals" / f"{name}_cases.jsonl"
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _check_case(case_id: str, data: dict, rules: dict) -> list[str]:
    errs: list[str] = []
    for key in rules.get("expect_keys") or []:
        if key not in data:
            errs.append(f"{case_id}: missing key {key!r}")
    blob = json.dumps(data, ensure_ascii=False)
    for sub in rules.get("forbid_substrings") or []:
        if sub in blob:
            errs.append(f"{case_id}: forbidden substring {sub!r} in payload")
    score = data.get("overall_score")
    if isinstance(score, int):
        if "max_overall_score" in rules and score > rules["max_overall_score"]:
            errs.append(f"{case_id}: overall_score {score} too high")
        if "min_overall_score" in rules and score < rules["min_overall_score"]:
            errs.append(f"{case_id}: overall_score {score} too low")
    tiers = data.get("tiers")
    if isinstance(tiers, list) and "min_tiers" in rules:
        if len(tiers) < int(rules["min_tiers"]):
            errs.append(f"{case_id}: tiers length {len(tiers)} < min")
    return errs


PATH_BY_SUITE = {
    "personal_operator": [
        ("/api/v1/personal-operator/daily-brief", "po_daily_brief_has_greeting"),
        ("/api/v1/personal-operator/launch-report", "po_launch_report_has_score"),
    ],
    "revenue_os": [
        ("/api/v1/v3/command-center/snapshot", "v3_command_snapshot_shape"),
        ("/api/v1/business/pricing", "business_pricing_tiers"),
    ],
}


async def _run_suite(client: httpx.AsyncClient, suite: str) -> list[str]:
    errs: list[str] = []
    cases_by_id = {c["id"]: c for c in _load_cases(suite)}
    for path, case_id in PATH_BY_SUITE[suite]:
        case = cases_by_id.get(case_id)
        if not case:
            errs.append(f"missing case definition {case_id}")
            continue
        r = await client.get(path)
        if r.status_code != 200:
            errs.append(f"{case_id}: HTTP {r.status_code} for {path}")
            continue
        try:
            data = r.json()
        except json.JSONDecodeError:
            errs.append(f"{case_id}: invalid JSON from {path}")
            continue
        errs.extend(_check_case(case_id, data, case))
    return errs


async def main_async(args: argparse.Namespace) -> int:
    suites = args.suite or list(_DEFAULT_SUITES)
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    all_errs: list[str] = []
    async with httpx.AsyncClient(transport=transport, base_url="http://eval") as client:
        for s in suites:
            all_errs.extend(await _run_suite(client, s))
    if all_errs:
        print("EVAL_FAIL")
        for e in all_errs:
            print(e)
        return 1
    print("EVAL_OK suites=", ",".join(suites))
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--suite",
        action="append",
        choices=list(PATH_BY_SUITE.keys()),
        help="Repeatable; default runs both suites",
    )
    args = p.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
