"""
Dump all Dealix contract JSON Schemas to dealix/contracts/schemas/.

Run: python -m dealix.contracts.dump_schemas
"""

from __future__ import annotations

import json
from pathlib import Path

from dealix.contracts import AuditEntry, DecisionOutput, EventEnvelope, EvidencePack


def main() -> None:
    out = Path(__file__).parent / "schemas"
    out.mkdir(exist_ok=True)

    targets = {
        "decision_output.schema.json": DecisionOutput,
        "event_envelope.schema.json": EventEnvelope,
        "evidence_pack.schema.json": EvidencePack,
        "audit_entry.schema.json": AuditEntry,
    }

    for filename, model in targets.items():
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"https://dealix.sa/schemas/{filename}"
        path = out / filename
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✓ {path}")


if __name__ == "__main__":
    main()
