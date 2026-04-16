# Dealix — Project Memory (Second Brain)

Structured, inspectable, versionable institutional memory.
Every item follows a strict schema. No dumping. No notes without owners.

## Directory Structure

| Directory | Purpose | Example Items |
|---|---|---|
| `architecture/` | System design decisions, diagrams | Service maps, data flow, integration diagrams |
| `adr/` | Architecture Decision Records | ADR-001 Sovereign Growth OS |
| `runbooks/` | Operational procedures | Deployment runbook, incident response |
| `releases/` | Release notes, post-release reviews | v1.0 release notes, rollback reports |
| `postmortems/` | Incident postmortems | Outage analysis, root cause, prevention |
| `growth/` | Partnership & expansion learnings | Partner ROI analysis, expansion outcomes |
| `ma/` | M&A deal learnings, DD patterns | DD checklist improvements, valuation accuracy |
| `security/` | Security findings, threat models | Pentest results, OWASP findings, Shannon reports |
| `patterns/` | Reusable workflow patterns | Approval flow patterns, integration patterns |
| `prompts/` | Effective prompt templates | Agent system prompts, scoring prompts |
| `providers/` | Provider benchmark history | Model comparison results, cost analysis |
| `benchmarks/` | Performance benchmarks | API latency baselines, workflow throughput |
| `experiments/` | A/B tests, pilot results | MemPalace pilot, routing experiments |
| `customers/` | Customer success patterns | Onboarding friction points, churn signals |
| `indexes/` | Cross-cutting indexes | Tag index, owner index |
| `wiki/` | General knowledge base | Team processes, FAQ |

## Memory Item Schema

Every file in this memory system MUST start with this frontmatter:

```yaml
---
title: "Clear, searchable title"
type: adr | runbook | learning | finding | benchmark | pattern | experiment
owner: "person or role"
date: "YYYY-MM-DD"
confidence: high | medium | low | unverified
status: active | archived | superseded
review_date: "YYYY-MM-DD"
tags: [tag1, tag2]
source: "where this knowledge came from"
---
```

## Rules

1. **No dumping** — Every item must be classified and structured
2. **No orphans** — Every item must have an owner
3. **No blind trust** — Every item must have a confidence level
4. **Review dates are mandatory** — Stale items get flagged
5. **Duplicates are merged** — Not accumulated
6. **Retrieval is task-aware** — Filtered by relevance + recency + confidence
7. **Superseded items stay** — Marked `status: superseded` with link to replacement
