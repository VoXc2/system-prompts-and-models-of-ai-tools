"""Pipeline tracing — tracks cost, latency, decisions per run."""
import time
import uuid
import json
import logging

logger = logging.getLogger("dealix.gtm_os.trace")

class PipelineTrace:
    def __init__(self, pipeline_name: str, company: str = ""):
        self.trace_id = str(uuid.uuid4())[:8]
        self.pipeline = pipeline_name
        self.company = company
        self.start_time = time.time()
        self.steps: list[dict] = []
        self.total_cost = 0.0

    def log_step(self, agent: str, result_summary: str, cost: float = 0.0, latency_ms: float = 0.0):
        step = {
            "agent": agent,
            "result": result_summary[:200],
            "cost_sar": round(cost, 6),
            "latency_ms": round(latency_ms, 1),
            "timestamp": time.time(),
        }
        self.steps.append(step)
        self.total_cost += cost

    def finish(self) -> dict:
        elapsed = time.time() - self.start_time
        report = {
            "trace_id": self.trace_id,
            "pipeline": self.pipeline,
            "company": self.company,
            "total_time_s": round(elapsed, 2),
            "total_cost_sar": round(self.total_cost, 6),
            "steps": len(self.steps),
            "step_details": self.steps,
        }
        logger.info(f"[TRACE:{self.trace_id}] {self.pipeline} for {self.company}: {elapsed:.1f}s, {self.total_cost:.4f} SAR, {len(self.steps)} steps")
        return report
