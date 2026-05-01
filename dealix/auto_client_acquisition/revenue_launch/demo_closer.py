"""Demo closer — re-export single source of truth from launch_ops."""

from __future__ import annotations

from auto_client_acquisition.launch_ops.demo_flow import (
    build_12_min_demo_flow,
    build_close_script,
    build_discovery_questions,
    build_objection_responses,
)

__all__ = [
    "build_12_min_demo_flow",
    "build_close_script",
    "build_discovery_questions",
    "build_objection_responses",
]
