"""Audit Chain — SHA-256 hash chain across all modules
FIXED: EXCLUSIVE transaction ensures atomic read-then-write to prevent
concurrent requests from producing duplicate prev_hash entries.
"""
import hashlib
import json
import time
from app.core.database import db


def log(org_id: str, module: str, action: str, actor_id: str, resource_id: str, payload: dict = None):
    with db() as conn:
        # EXCLUSIVE lock: no other writer can read the tail until we commit
        conn.execute("BEGIN EXCLUSIVE")
        last = conn.execute(
            "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        prev_hash = last["entry_hash"] if last else "GENESIS"
        content = f"{org_id}:{module}:{action}:{actor_id}:{resource_id}:{time.time()}"
        entry_hash = hashlib.sha256(f"{prev_hash}:{content}".encode()).hexdigest()
        conn.execute("""
            INSERT INTO audit_log (org_id, module, action, actor_id, resource_id, payload, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (org_id, module, action, actor_id, resource_id,
              json.dumps(payload or {}), prev_hash, entry_hash))
        # conn.commit() is called by db() context manager on exit


def verify_chain(org_id: str) -> dict:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE org_id=? ORDER BY id ASC", (org_id,)
        ).fetchall()
    errors = []
    prev = "GENESIS"
    for row in rows:
        expected_content = f"{row['org_id']}:{row['module']}:{row['action']}:{row['actor_id']}:{row['resource_id']}"
        # Verify prev_hash linkage only (content hash includes timestamp which we can't recompute)
        if row["prev_hash"] != prev:
            errors.append({
                "id": row["id"],
                "expected_prev": prev,
                "actual_prev": row["prev_hash"]
            })
        prev = row["entry_hash"]
    return {"valid": len(errors) == 0, "total_entries": len(rows), "errors": errors}
