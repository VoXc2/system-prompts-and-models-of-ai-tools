"""paid_beta_daily_scorecard.py — CLI smoke."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "paid_beta_daily_scorecard.py"


def test_scorecard_cli_json_defaults():
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--json"],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["messages_sent"] == 0
    assert set(data.keys()) >= {
        "messages_sent",
        "replies",
        "demos",
        "pilots",
        "payments",
        "proof_packs",
    }


def test_scorecard_cli_overrides():
    r = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--json",
            "--messages",
            "12",
            "--replies",
            "3",
            "--demos",
            "1",
            "--pilots",
            "0",
            "--payments",
            "0",
            "--proof-packs",
            "1",
        ],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["messages_sent"] == 12
    assert data["replies"] == 3
    assert data["demos"] == 1
    assert data["proof_packs"] == 1
