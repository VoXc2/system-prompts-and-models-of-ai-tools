"""Read-only local dependency snapshot — no network; safe for hourly job."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


def _backend_root() -> Path:
    # app/services/upgrade_director/snapshot.py -> parents[3] = backend/
    return Path(__file__).resolve().parents[3]


def _repo_root() -> Path:
    return _backend_root().parent


def collect_local_dependency_snapshot() -> Dict[str, Any]:
    """Parse requirements.txt + frontend package.json core versions."""
    backend = _backend_root()
    repo = _repo_root()
    out: Dict[str, Any] = {"backend_root": str(backend), "repo_root": str(repo)}

    req = backend / "requirements.txt"
    if req.is_file():
        pins: Dict[str, str] = {}
        for line in req.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*[=<>!]+\s*([0-9a-zA-Z\.\-\+]+)", line)
            if m:
                pins[m.group(1).lower()] = m.group(2)
        out["requirements_pins"] = dict(sorted(pins.items())[:80])
    else:
        out["requirements_pins"] = {}

    pkg = repo / "frontend" / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            deps = data.get("dependencies") or {}
            dev = data.get("devDependencies") or {}
            keys = (
                "next",
                "react",
                "react-dom",
                "typescript",
                "@types/node",
                "tailwindcss",
                "vitest",
                "playwright",
            )
            out["frontend"] = {k: deps.get(k) or dev.get(k) for k in keys if (deps.get(k) or dev.get(k))}
        except (json.JSONDecodeError, OSError) as e:
            out["frontend_error"] = str(e)
    else:
        out["frontend"] = {}

    return out
