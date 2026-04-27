"""Audit log — records every proposed and executed action."""
import time

_log: list[dict] = []

def log_entry(company: str, action: str, channel: str = "", notes: str = "") -> dict:
    entry = {"id": len(_log) + 1, "company": company, "action": action, "channel": channel, "notes": notes, "timestamp": time.time()}
    _log.append(entry)
    return {"logged": True, "entry_id": entry["id"]}

def get_log(limit: int = 50) -> list[dict]:
    return _log[-limit:]

def get_log_for_company(company: str) -> list[dict]:
    return [e for e in _log if e["company"] == company]
