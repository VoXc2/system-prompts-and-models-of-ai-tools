#!/usr/bin/env python3
"""Dealix launch readiness — HTTP gates, landing files, catalog shape, live-send flag.

Prints verdict: GO_PRIVATE_BETA | NO_GO | PAID_BETA_READY
  - GO_PRIVATE_BETA: local (in-process) checks pass; safe for private beta motion.
  - PAID_BETA_READY: same + --base-url remote GETs all succeeded (deploy verified).
  - NO_GO: any required gate failed.

Exit code: 0 only when verdict is GO_PRIVATE_BETA or PAID_BETA_READY.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

REQUIRED_GET_PATHS: tuple[str, ...] = (
    "/health",
    "/api/v1/customer-ops/onboarding/checklist",
    "/api/v1/customer-ops/support/sla",
    "/api/v1/customer-ops/connectors/status",
    "/api/v1/services/catalog",
    "/api/v1/launch/private-beta/offer",
    "/api/v1/security-curator/demo",
)

LANDING_FILES: tuple[str, ...] = (
    "companies.html",
    "marketers.html",
    "private-beta.html",
)

# High-signal leak patterns (lines only; may false-positive in docs — use with care).
_SECRET_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk_live_[0-9a-zA-Z]{20,}"),
    re.compile(r"SUPABASE_SERVICE_ROLE_KEY\s*=\s*['\"]?[^\s'\"]{20,}"),
    re.compile(r"OPENAI_API_KEY\s*=\s*['\"]?sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*['\"]?sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)

_EXCLUDE_DIR_NAMES = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", "htmlcov", ".pytest_cache", ".mypy_cache"}
)


def _configure_stdio_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass


def _gate(name: str, ok: bool, detail: str = "") -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def _validate_catalog_payload(data: dict[str, Any]) -> dict[str, Any]:
    tower = data.get("tower")
    if not isinstance(tower, dict):
        return _gate("catalog_tower", False, "missing_or_invalid_tower")
    services = tower.get("services")
    if not isinstance(services, list) or not services:
        return _gate("catalog_tower_services", False, "empty_or_missing_services")
    required_keys = ("service_id", "pricing_range_sar", "proof_metrics", "approval_policy")
    for i, svc in enumerate(services):
        if not isinstance(svc, dict):
            return _gate("catalog_service_shape", False, f"item_{i}_not_dict")
        missing = [k for k in required_keys if k not in svc or svc[k] in (None, "", [], {})]
        if missing:
            return _gate(
                "catalog_service_fields",
                False,
                f"{svc.get('service_id', i)}:missing={','.join(missing)}",
            )
        pr = svc.get("pricing_range_sar")
        if not isinstance(pr, dict) or "min" not in pr or "max" not in pr:
            return _gate("catalog_pricing_range", False, str(svc.get("service_id")))
        pm = svc.get("proof_metrics")
        if not isinstance(pm, list) or not pm:
            return _gate("catalog_proof_metrics", False, str(svc.get("service_id")))
    return _gate("catalog_tower_services", True, f"count={len(services)}")


def _check_landing_files(repo: Path) -> dict[str, Any]:
    missing = [f for f in LANDING_FILES if not (repo / "landing" / f).is_file()]
    if missing:
        return _gate("landing_files", False, ",".join(missing))
    return _gate("landing_files", True, ",".join(LANDING_FILES))


def _check_whatsapp_live_flag() -> dict[str, Any]:
    from core.config.settings import get_settings

    if get_settings().whatsapp_allow_live_send:
        return _gate(
            "whatsapp_allow_live_send",
            False,
            "must_be_false_for_private_beta_gate",
        )
    return _gate("whatsapp_allow_live_send", True, "false")


def _scan_repo_secrets(repo: Path, *, max_file_bytes: int = 400_000) -> dict[str, Any]:
    hits: list[str] = []
    for root, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIR_NAMES]
        for name in filenames:
            if not name.endswith((".py", ".yml", ".yaml", ".json", ".md", ".toml", ".env", ".example")):
                continue
            path = Path(root) / name
            try:
                raw = path.read_bytes()
            except OSError:
                continue
            if len(raw) > max_file_bytes:
                continue
            try:
                text = raw.decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            for line_no, line in enumerate(text.splitlines(), 1):
                for pat in _SECRET_LINE_PATTERNS:
                    if pat.search(line):
                        rel = path.relative_to(repo)
                        hits.append(f"{rel}:{line_no}")
                        break
                if len(hits) >= 25:
                    return _gate("secret_scan", False, ";".join(hits[:25]))
    if hits:
        return _gate("secret_scan", False, ";".join(hits[:25]))
    return _gate("secret_scan", True, "no_pattern_hits")


def _probe_paths(get_response: Any, label: str) -> list[dict[str, Any]]:
    """get_response(path) -> object with .status_code and .json()."""
    gates: list[dict[str, Any]] = []
    for path in REQUIRED_GET_PATHS:
        try:
            r = get_response(path)
            http_ok = r.status_code == 200
            if not http_ok:
                gates.append(
                    {
                        "name": f"http_{label}_{path}",
                        "ok": False,
                        "detail": f"HTTP {r.status_code}",
                        "scope": label,
                        "path": path,
                    }
                )
                continue
            if path == "/api/v1/services/catalog":
                try:
                    body = r.json()
                except Exception as exc:  # noqa: BLE001
                    gates.append(
                        {
                            "name": f"http_{label}_{path}",
                            "ok": False,
                            "detail": f"json_error:{exc}",
                            "scope": label,
                            "path": path,
                        }
                    )
                    continue
                cg = _validate_catalog_payload(body)
                gates.append({**cg, "scope": label, "path": path})
                continue
            gates.append(
                {
                    "name": f"http_{label}_{path}",
                    "ok": True,
                    "detail": "200",
                    "scope": label,
                    "path": path,
                }
            )
        except Exception as exc:  # noqa: BLE001
            gates.append(
                {
                    "name": f"http_{label}_{path}",
                    "ok": False,
                    "detail": str(exc),
                    "scope": label,
                    "path": path,
                }
            )
    return gates


def run_readiness(
    *,
    base_url: str | None = None,
    run_secret_scan: bool = False,
) -> dict[str, Any]:
    """Run all gates. `base_url` if set triggers remote probe in addition to local ASGI."""
    gates: list[dict[str, Any]] = []
    gates.append({**_check_landing_files(_REPO), "scope": "repo"})
    gates.append({**_check_whatsapp_live_flag(), "scope": "settings"})
    if run_secret_scan:
        gates.append({**_scan_repo_secrets(_REPO), "scope": "repo"})

    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        gates.append(
            {
                "name": "testclient",
                "ok": False,
                "detail": str(exc),
                "scope": "deps",
            }
        )
        return _finalize(gates, remote_attempted=False)

    from api.main import create_app

    app = create_app()
    with TestClient(app) as client:
        gates.extend(_probe_paths(lambda p: client.get(p), "local"))

    remote_attempted = False
    bu = (base_url or "").strip().rstrip("/")
    if bu:
        remote_attempted = True
        try:
            import httpx

            with httpx.Client(timeout=30.0, follow_redirects=True) as rclient:
                gates.extend(
                    _probe_paths(lambda p: rclient.get(f"{bu.rstrip('/')}{p}"), "remote")
                )
        except ImportError as exc:
            gates.append(
                {
                    "name": "httpx_remote",
                    "ok": False,
                    "detail": str(exc),
                    "scope": "remote",
                }
            )
        except Exception as exc:  # noqa: BLE001
            gates.append(
                {
                    "name": "http_remote_client",
                    "ok": False,
                    "detail": str(exc),
                    "scope": "remote",
                }
            )

    return _finalize(gates, remote_attempted=remote_attempted)


def _finalize(
    gates: list[dict[str, Any]],
    *,
    remote_attempted: bool,
) -> dict[str, Any]:
    # Local bundle: repo files, settings, deps, in-process ASGI probes only.
    local_ok = all(g.get("ok") for g in gates if g.get("scope") in ("repo", "settings", "deps", "local"))
    remote_gates = [g for g in gates if g.get("scope") == "remote"]
    remote_ok = bool(remote_gates) and all(g.get("ok") for g in remote_gates)

    if not local_ok:
        verdict = "NO_GO"
    elif remote_attempted:
        verdict = "PAID_BETA_READY" if remote_ok else "NO_GO"
    else:
        verdict = "GO_PRIVATE_BETA"

    return {
        "verdict": verdict,
        "gates": gates,
        "remote_attempted": remote_attempted,
        "remote_all_ok": remote_ok if remote_attempted else None,
    }


def main() -> int:
    _configure_stdio_utf8()
    parser = argparse.ArgumentParser(description="Dealix launch readiness gates")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("STAGING_BASE_URL", "").strip().rstrip("/"),
        help="Staging/production URL (optional). If set, remote GETs must pass for PAID_BETA_READY.",
    )
    parser.add_argument(
        "--secrets",
        action="store_true",
        help="Scan repo for common secret patterns (slow; may false-positive in docs).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable report only.",
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Also print the legacy manual checklist to stderr.",
    )
    args = parser.parse_args()

    report = run_readiness(base_url=args.base_url or None, run_secret_scan=args.secrets)
    verdict = report["verdict"]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"VERDICT: {verdict}\n")
        for g in report["gates"]:
            mark = "OK" if g.get("ok") else "FAIL"
            scope = g.get("scope", "")
            name = g.get("name", "")
            detail = g.get("detail", "")
            print(f"  [{mark}] ({scope}) {name}  {detail}".strip())

    if args.checklist:
        print("\n--- Manual checklist (reference) ---", file=sys.stderr)
        print(
            "  pytest -q | print_routes | smoke_inprocess | smoke_staging --base-url",
            file=sys.stderr,
        )

    return 0 if verdict in ("GO_PRIVATE_BETA", "PAID_BETA_READY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
