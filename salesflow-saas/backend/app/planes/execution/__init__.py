"""
Execution Plane — Durable workflow runtime.

Current: Celery/LangGraph for short-term tasks.
Target:  Temporal for all durable commitments (approvals, DD, signatures, launches, PMI).

Responsibilities:
- Crash-proof execution with automatic resume
- Long-running workflow orchestration (days/weeks)
- HITL interrupt points via LangGraph checkpoints
- Retry/idempotency for all external calls
- SLA tracking and escalation
"""
