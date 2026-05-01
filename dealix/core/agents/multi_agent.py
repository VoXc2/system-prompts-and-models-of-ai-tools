"""
Multi-Agent Orchestrator — coordinates multiple agents on a shared context.
منسق الوكلاء — ينسق تنفيذ عدة وكلاء على سياق مشترك.
"""

from __future__ import annotations

import asyncio
from typing import Any

from core.agents.base import BaseAgent
from core.logging import get_logger

logger = get_logger(__name__)


class MultiAgentOrchestrator:
    """
    Coordinates execution of multiple agents.
    Supports: sequential, parallel, and conditional execution.
    """

    def __init__(self) -> None:
        self.agents: dict[str, BaseAgent] = {}
        self.log = logger.bind(component="orchestrator")

    def register(self, key: str, agent: BaseAgent) -> None:
        """Register an agent under a key | سجّل وكيلاً باسم."""
        self.agents[key] = agent
        self.log.info("agent_registered", key=key, agent_id=agent.agent_id)

    def get(self, key: str) -> BaseAgent:
        agent = self.agents.get(key)
        if agent is None:
            raise KeyError(f"Agent not registered: {key}")
        return agent

    async def run_sequential(
        self, steps: list[tuple[str, dict[str, Any]]], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Run steps sequentially, passing context forward.
        نفّذ الخطوات متتابعة، ومرّر السياق بينها.
        """
        ctx = context or {}
        for key, kwargs in steps:
            agent = self.get(key)
            self.log.info("run_step", step=key)
            result = await agent.run(**{**kwargs, "context": ctx})
            ctx[key] = result
        return ctx

    async def run_parallel(self, calls: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
        """
        Run multiple agents concurrently.
        نفّذ عدة وكلاء بالتوازي.
        """

        async def _run(key: str, kwargs: dict[str, Any]) -> tuple[str, Any]:
            agent = self.get(key)
            return key, await agent.run(**kwargs)

        tasks = [_run(k, kw) for k, kw in calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        out: dict[str, Any] = {}
        for item in results:
            if isinstance(item, Exception):
                self.log.exception("parallel_agent_failed", error=str(item))
                continue
            key, result = item
            out[key] = result
        return out
