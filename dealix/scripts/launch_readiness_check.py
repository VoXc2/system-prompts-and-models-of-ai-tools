#!/usr/bin/env python3
"""Dealix Launch Readiness — 10-gate Go/No-Go check.

Runs locally + against an optional staging URL. Reports which gates pass/fail
and what the next concrete actions are.

Usage:
    python scripts/launch_readiness_check.py
    python scripts/launch_readiness_check.py --staging-url https://staging.example
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = (
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9]{30,}",
    r"sk-ant-[A-Za-z0-9_\-]{20,}",
    r"AKIA[A-Z0-9]{16}",
    r"AIza[A-Za-z0-9_\-]{30,}",
    r"EAA[A-Za-z0-9]{30,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----",
)

EXCLUDE_DIRS = (".git", ".venv", "node_modules", "__pycache__", ".pytest_cache")


def gate_tests_passed() -> tuple[bool, str]:
    """Run pytest with --noconftest on the new layer tests as a quick proxy."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest",
             "tests/unit/test_launch_ops.py",
             "tests/unit/test_revenue_launch.py",
             "tests/unit/test_security_curator.py",
             "--noconftest", "--no-cov", "-q", "-p", "no:cacheprovider"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
        )
        ok = result.returncode == 0
        last_line = (result.stdout or "").strip().splitlines()[-1:]
        msg = last_line[0] if last_line else "no output"
        return ok, msg
    except Exception as exc:  # noqa: BLE001
        return False, f"pytest error: {exc}"


def gate_routes_check() -> tuple[bool, str]:
    """Run scripts/print_routes.py — should not raise."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/print_routes.py"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            n_routes = result.stdout.count("/api/v1")
            return True, f"{n_routes} v1 routes"
        return False, f"exit={result.returncode}"
    except Exception as exc:  # noqa: BLE001
        return False, f"err: {exc}"


def gate_no_secrets() -> tuple[bool, str]:
    """Scan repo for secret patterns. Skips known-safe directories."""
    findings: list[str] = []
    pat = re.compile("|".join(SECRET_PATTERNS))
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        # Skip docs that intentionally mention patterns as examples.
        if path.suffix in {".md", ".lock", ".pyc", ".png", ".jpg", ".jpeg",
                           ".gif", ".woff", ".woff2", ".ttf"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        if pat.search(text):
            findings.append(str(path.relative_to(REPO_ROOT)))
            if len(findings) >= 3:
                break
    return (not findings), (
        "clean" if not findings else f"FOUND in: {', '.join(findings)}"
    )


def gate_staging_health(staging_url: str | None) -> tuple[bool, str]:
    """Hit /health on staging if a URL is provided."""
    if not staging_url:
        return False, "no --staging-url provided"
    url = staging_url.rstrip("/") + "/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Dealix/Readiness"})
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec
            return resp.status == 200, f"status={resp.status}"
    except Exception as exc:  # noqa: BLE001
        return False, f"err: {exc}"


def gate_supabase_staging() -> tuple[bool, str]:
    """We can only check whether SUPABASE_URL is configured, not connectivity."""
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        return True, "env vars configured"
    return False, "SUPABASE_URL or SERVICE_ROLE_KEY not set in env"


def gate_service_catalog(staging_url: str | None) -> tuple[bool, str]:
    if not staging_url:
        return False, "no --staging-url provided"
    url = staging_url.rstrip("/") + "/api/v1/services/catalog"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Dealix/Readiness"})
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            total = int(data.get("total", 0))
            return total >= 4, f"{total} services"
    except Exception as exc:  # noqa: BLE001
        return False, f"err: {exc}"


def gate_private_beta_page() -> tuple[bool, str]:
    p = REPO_ROOT / "landing" / "private-beta.html"
    if not p.exists():
        return False, "missing"
    text = p.read_text(encoding="utf-8", errors="ignore")
    has_cta = ("احجز" in text) or ("ابدأ" in text) or ("احصل" in text)
    has_pilot = ("Pilot" in text) or ("بايلوت" in text)
    return (has_cta and has_pilot), (
        "ok" if has_cta and has_pilot else "missing CTA or Pilot mention"
    )


def gate_first_20_ready() -> tuple[bool, str]:
    """Soft check: a tracker doc/sheet may exist as evidence."""
    candidates = [
        REPO_ROOT / "docs" / "FIRST_20_OUTREACH_MESSAGES.md",
        REPO_ROOT / "docs" / "REVENUE_TODAY_PLAYBOOK.md",
    ]
    found = [str(c.relative_to(REPO_ROOT)) for c in candidates if c.exists()]
    return bool(found), ", ".join(found) or "no first-20 doc/sheet found"


def gate_live_sends_disabled() -> tuple[bool, str]:
    """Verify env flags for live sends are NOT set to true."""
    flags = [
        "WHATSAPP_ALLOW_LIVE_SEND",
        "GMAIL_ALLOW_LIVE_SEND",
        "CALENDAR_ALLOW_LIVE_INSERT",
        "MOYASAR_ALLOW_LIVE_CHARGE",
        "GBP_ALLOW_LIVE_REPLY",
    ]
    enabled = [f for f in flags if os.getenv(f, "false").lower() == "true"]
    return (not enabled), (
        "all disabled" if not enabled else f"ENABLED: {', '.join(enabled)}"
    )


def gate_payment_manual_ready() -> tuple[bool, str]:
    """Soft check: payment-manual flow module is present + accessible."""
    p = REPO_ROOT / "auto_client_acquisition" / "revenue_launch" / "payment_manual_flow.py"
    return p.exists(), ("module present" if p.exists() else "missing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-url", default=None,
                        help="Optional staging URL for live checks")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of pretty output")
    args = parser.parse_args()

    print("Dealix Launch Readiness — 10 Gates")
    print("─" * 60)

    gates = [
        ("tests_passed", gate_tests_passed()),
        ("routes_check", gate_routes_check()),
        ("no_secrets", gate_no_secrets()),
        ("staging_health", gate_staging_health(args.staging_url)),
        ("supabase_staging", gate_supabase_staging()),
        ("service_catalog", gate_service_catalog(args.staging_url)),
        ("private_beta_page", gate_private_beta_page()),
        ("first_20_ready", gate_first_20_ready()),
        ("live_sends_disabled", gate_live_sends_disabled()),
        ("payment_manual_ready", gate_payment_manual_ready()),
    ]

    passed = sum(1 for _, (ok, _) in gates if ok)
    total = len(gates)
    pct = round(100 * passed / total, 1)

    if args.json:
        out = {
            "passed": passed, "total": total, "pct": pct,
            "gates": [{"id": gid, "passed": ok, "info": info}
                      for gid, (ok, info) in gates],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for gid, (ok, info) in gates:
            mark = "✅" if ok else "🔴"
            print(f"{mark} {gid:<24} {info}")
        print("─" * 60)
        critical = ("no_secrets", "live_sends_disabled", "staging_health")
        critical_failed = [gid for gid, (ok, _) in gates
                           if gid in critical and not ok]
        if critical_failed:
            verdict = f"🔴 NO-GO — critical gates failed: {', '.join(critical_failed)}"
        elif pct >= 70:
            verdict = f"✅ GO (Private Beta) — {passed}/{total} = {pct}%"
        else:
            verdict = f"🟡 FIX-THEN-GO — only {passed}/{total} = {pct}%"
        print(verdict)

    return 0 if passed == total else (1 if passed < 7 else 0)


if __name__ == "__main__":
    sys.exit(main())
