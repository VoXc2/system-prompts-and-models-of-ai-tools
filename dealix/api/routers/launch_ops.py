"""Launch ops API — private beta, demo, outreach, go/no-go."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.launch_ops.demo_flow import build_demo_script
from auto_client_acquisition.launch_ops.go_no_go import evaluate_go_no_go
from auto_client_acquisition.launch_ops.launch_scorecard import build_launch_scorecard
from auto_client_acquisition.launch_ops.outreach_messages import build_first_twenty_outreach
from auto_client_acquisition.launch_ops.private_beta import build_private_beta_offer

router = APIRouter(prefix="/api/v1/launch", tags=["launch_ops"])


@router.get("/private-beta/offer")
async def launch_private_beta_offer() -> dict[str, Any]:
    return build_private_beta_offer()


@router.get("/demo-script")
async def launch_demo_script() -> dict[str, Any]:
    return build_demo_script()


@router.get("/outreach/first-20")
async def launch_outreach_first_20() -> dict[str, Any]:
    return build_first_twenty_outreach()


@router.get("/go-no-go")
async def launch_go_no_go_get() -> dict[str, Any]:
    return evaluate_go_no_go(None)


@router.post("/go-no-go")
async def launch_go_no_go_post(flags: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return evaluate_go_no_go(flags or {})


@router.get("/scorecard")
async def launch_scorecard() -> dict[str, Any]:
    return build_launch_scorecard()
