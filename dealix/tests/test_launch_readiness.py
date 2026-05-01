"""Launch readiness script — verdict and catalog gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def _load_launch_readiness():
    path = _ROOT / "scripts" / "launch_readiness_check.py"
    spec = importlib.util.spec_from_file_location("launch_readiness_check", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_run_readiness_default_go_private_beta():
    mod = _load_launch_readiness()
    report = mod.run_readiness(base_url=None, run_secret_scan=False)
    assert report["verdict"] == "GO_PRIVATE_BETA", report
    assert all(g["ok"] for g in report["gates"] if g.get("scope") in ("repo", "settings", "local"))


def test_catalog_validator_requires_tower_fields():
    mod = _load_launch_readiness()
    bad = mod._validate_catalog_payload({"tower": {"services": [{"service_id": "x"}]}})
    assert bad["ok"] is False
    good = mod._validate_catalog_payload(
        {
            "tower": {
                "services": [
                    {
                        "service_id": "demo",
                        "pricing_range_sar": {"min": 0, "max": 100},
                        "proof_metrics": ["x"],
                        "approval_policy": "draft_only",
                    }
                ]
            }
        }
    )
    assert good["ok"] is True


@pytest.mark.asyncio
async def test_operator_mode_profiles_self_growth_and_delivery(async_client):
    """Router exposes self_growth and service_delivery mode profiles."""
    for mode in ("self_growth", "service_delivery"):
        r = await async_client.post(
            "/api/v1/operator/chat/message",
            json={"message": "مرحبا", "mode": mode},
        )
        assert r.status_code == 200
        body = r.json()
        mp = body.get("mode_profile") or {}
        assert mp.get("mode") == mode
        assert mp.get("demo") is True
