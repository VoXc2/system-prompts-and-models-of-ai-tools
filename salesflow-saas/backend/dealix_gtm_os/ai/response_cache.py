"""In-memory response cache — avoids re-analyzing the same company."""
import hashlib
import json
import time
from typing import Optional

_cache: dict[str, dict] = {}

def _key(agent_name: str, input_data: dict) -> str:
    raw = f"{agent_name}:{json.dumps(input_data, sort_keys=True, ensure_ascii=False)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def get_cached(agent_name: str, input_data: dict, ttl_hours: float = 24) -> Optional[dict]:
    k = _key(agent_name, input_data)
    entry = _cache.get(k)
    if not entry:
        return None
    if time.time() - entry["ts"] > ttl_hours * 3600:
        del _cache[k]
        return None
    return entry["data"]

def set_cached(agent_name: str, input_data: dict, result: dict):
    k = _key(agent_name, input_data)
    _cache[k] = {"data": result, "ts": time.time()}

def cache_stats() -> dict:
    return {"entries": len(_cache), "keys": list(_cache.keys())[:10]}
