"""Approval queue — tracks actions that need Sami's approval before sending."""
import time
from typing import Optional

_queue: list[dict] = []

def add_to_queue(company: str, action: str, channel: str, message_preview: str = "") -> dict:
    entry = {"id": len(_queue) + 1, "company": company, "action": action, "channel": channel, "preview": message_preview[:100], "status": "pending", "created_at": time.time()}
    _queue.append(entry)
    return entry

def get_pending() -> list[dict]:
    return [e for e in _queue if e["status"] == "pending"]

def approve(company: str, action: str) -> dict:
    for e in _queue:
        if e["company"] == company and e["action"] == action and e["status"] == "pending":
            e["status"] = "approved"
            e["approved_at"] = time.time()
            return {"approved": True, "entry": e}
    return {"approved": False, "reason": "Not found in queue"}

def reject(company: str, action: str) -> dict:
    for e in _queue:
        if e["company"] == company and e["action"] == action and e["status"] == "pending":
            e["status"] = "rejected"
            return {"rejected": True, "entry": e}
    return {"rejected": False, "reason": "Not found in queue"}
