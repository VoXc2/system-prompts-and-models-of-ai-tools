# Evidence Pack Specification

> The formal spec for what an Evidence Pack contains, who produces it, who reads it, and how long it lives.

---

## 1. Purpose

An Evidence Pack is the auditable, read-only bundle attached to every Tier-A or Tier-B decision in Dealix. It answers four questions, in one artifact:

1. **What was decided?** (pointer to the DecisionOutput)
2. **On what basis?** (sources, excerpts, hashes, freshness)
3. **What did the system actually do?** (tool calls, intended vs actual, side-effects)
4. **How can a human understand it?** (bilingual memo in board-grade Arabic + English)

---

## 2. Structure

Defined in code at `dealix/contracts/evidence_pack.py::EvidencePack`.

Fields:

| Field | Type | Description |
|---|---|---|
| `pack_id` | string | Unique, format `pack_<16 hex>` |
| `decision_id` | string | FK → DecisionOutput |
| `entity_id` | string | Business entity (lead / deal / partner) |
| `tenant_id` | string | Multi-tenant scope |
| `agent_name` | string | Producing agent |
| `model` / `model_version` | string | LLM provenance |
| `sources` | list[EvidenceSource] | Everything consulted |
| `tool_calls` | list[ToolCallRecord] | Every tool invocation with intended vs actual |
| `prompts` | list[PromptRecord] | Prompt templates used |
| `data_freshness_window_hours` | int | Max age of sources at decision time |
| `reviewer_id` / `reviewed_at` | string | Optional HITL reviewer |
| `memo` | BilingualMemo | Title + body + exec summary AR + EN |
| `trace_id` | string | OTel trace linking decision → evidence |
| `created_at` | ISO-8601 | Immutable |

---

## 3. When is a pack produced?

**Mandatory** for any decision where any of the following are true:
- `approval_class` ∈ {A2, A3}
- `reversibility_class` = R3
- `sensitivity_class` = S3
- `confidence` < 0.7 on a high-stakes decision

**Optional but recommended** for A1 decisions that a manager may want to audit.

Skip for A0 / R0 / S0 routine decisions (e.g. every lead intake doesn't need a full pack).

---

## 4. Who produces it?

The agent that emits the DecisionOutput is responsible for assembling a draft pack. In practice this happens in three steps:

1. Agent emits `DecisionOutput` with a list of `Evidence` items.
2. A pack assembler (in `dealix.contracts.evidence_pack`) promotes those items into `EvidenceSource` records and appends `tool_calls` from the ToolVerificationLedger for the same `decision_id`.
3. If the decision requires HITL, the pack is marked unresolved until `reviewer_id` is set.

---

## 5. Content rules

### 5.1 Source rules
- MUST include source name (`source`), and either a URI or an internal reference.
- MUST include a verbatim excerpt, max 2000 characters.
- SHOULD include a content hash (SHA-256) of the full retrieved content.
- MUST include a retrieval timestamp.
- Confidence in [0.0, 1.0] required.

### 5.2 Tool call rules
- MUST record both `intended_action` and `actual_action`.
- MUST flag contradictions (`contradiction_flag = True` when they differ).
- MUST list side-effects plainly (e.g. "created contact id=123 in HubSpot").

### 5.3 Memo rules
- Bilingual AR + EN.
- Board-grade tone; Gulf business register for Arabic.
- Length: executive summary ≤ 120 words each; body ≤ 600 words each.
- Must reference the decision's top 3 evidence items inline.

---

## 6. Storage

- Phase 0–1: in-memory during request; JSON persisted to Postgres `evidence_packs` table (TODO).
- Phase 2+: object storage (S3-compatible) for full binary attachments (e.g. retrieved PDFs), with DB row pointing to the object key.
- Retention: 7 years, aligned with commercial record retention and PDPL legal hold.

---

## 7. Access control

- Evidence Pack Viewer UI reads by `pack_id`.
- Authorization via OpenFGA (Phase 2): `can_view_evidence_pack(user, pack_id)`.
- Phase 0–1 fallback: role-based — `viewer`, `approver`, `admin` on the relevant tenant.

---

## 8. Export

- **Read-only** by default. Exporting a pack:
  - Is an S2+ action (it's the customer's commercial data).
  - Requires approval class ≥ A1.
  - Is logged to the audit trail.

- Export formats:
  - JSON (the canonical format)
  - PDF (generated on demand for handoff to a human)
  - Arabic PDF respects RTL, Gulf typography, board-document layout.

---

## 9. Integrity

- `pack_id` is immutable.
- Any edit creates a new pack version with a new `pack_id`; the old one remains accessible.
- Optional: sign packs with a per-tenant signing key for tamper evidence (Phase 2+).

---

## 10. Anti-patterns

- ❌ Assembling a pack from nothing but the LLM's own prose ("I found that X is true") — must cite sources.
- ❌ Tool calls recorded only on success — failures are evidence too.
- ❌ Memo in only one language.
- ❌ Editing a pack in place instead of versioning.
- ❌ Storing raw S3 content (personal data) in the memo — store pointers + hashes.

---

## 11. Example

See `dealix/contracts/evidence_pack.py` for the Pydantic model. A minimal example:

```python
from dealix.contracts import EvidencePack, EvidenceSource, ToolCallRecord
from dealix.contracts.evidence_pack import BilingualMemo, PromptRecord

pack = EvidencePack(
    decision_id="dec_abc123",
    entity_id="lead_xyz789",
    agent_name="icp_matcher",
    model="claude-sonnet-4-5",
    sources=[
        EvidenceSource(
            source="crm.hubspot.contact",
            uri="hubspot://contacts/456",
            excerpt="Company size: 120 employees; industry: healthcare",
            content_hash="sha256:...",
        ),
    ],
    tool_calls=[
        ToolCallRecord(
            tool_name="hubspot.get_contact",
            intended_action="retrieve contact 456 read-only",
            actual_action="retrieved contact 456 read-only",
            outputs={"id": "456", "industry": "healthcare"},
            verification_status="verified",
        ),
    ],
    prompts=[PromptRecord(template_name="icp_reasoning", template_version="1.0")],
    memo=BilingualMemo(
        title_ar="توصية الملاءمة - مستشفى الرياض",
        title_en="Fit Recommendation — Riyadh Hospital",
        body_ar="...",
        body_en="...",
        executive_summary_ar="الشركة تطابق ملفنا المستهدف بدرجة 0.84 (Tier A)...",
        executive_summary_en="Company matches our ICP at 0.84 (Tier A)...",
    ),
)
```
