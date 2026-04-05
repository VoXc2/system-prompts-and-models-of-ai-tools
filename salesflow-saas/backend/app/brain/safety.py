"""Rate limits, retry caps, isolation — lightweight process-local; Redis later for multi-worker."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Dict, Tuple
from uuid import UUID


@dataclass
class TenantRateState:
    window_start: float = field(default_factory=time.monotonic)
    count: int = 0


class BrainSafety:
    """Per-tenant sliding window for brain event ingest (default 120/min)."""

    def __init__(self, max_events_per_minute: int = 120) -> None:
        self.max_events = max_events_per_minute
        self._windows: DefaultDict[str, TenantRateState] = defaultdict(TenantRateState)

    def allow(self, tenant_id: UUID | str) -> bool:
        tid = str(tenant_id)
        now = time.monotonic()
        st = self._windows[tid]
        if now - st.window_start > 60.0:
            st.window_start = now
            st.count = 0
        if st.count >= self.max_events:
            return False
        st.count += 1
        return True


# Singleton for API
brain_safety = BrainSafety()

# Retry policy for skills (used by agent_manager)
DEFAULT_MAX_SKILL_ATTEMPTS = 3
DEFAULT_SKILL_TIMEOUT_S = 60
