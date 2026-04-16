# Dealix Live Surfaces Tracker

**Version**: 1.0  
**Status**: Active  
**Purpose**: Track mandatory enterprise surfaces and acceptance criteria.

Legend:
- `Not Started`
- `In Progress`
- `Live (Baseline)`
- `Live (Governed)`

---

| Surface | Owner Plane | Status | Minimum Acceptance Criteria |
|--------|-------------|--------|-----------------------------|
| Executive Room | Decision + Data | Not Started | Board-ready view with decision impact, alternatives, risks, owner, due date |
| Approval Center | Trust + Execution | Not Started | Approval queue with `A0-A3`, policy refs, audit trail, SLA timers |
| Evidence Pack Viewer | Trust + Data | Not Started | Immutable evidence links, timestamps, source lineage |
| Partner Room | Decision + Execution | Not Started | Partner lifecycle workflow state, scorecard, margin contribution |
| DD Room | Execution + Trust | Not Started | Controlled DD streams, role-based access, checklist progress |
| Risk Board | Trust + Data | Not Started | Live risk heatmap with severity, mitigation owner, aging |
| Policy Violations Board | Trust | Not Started | Violations list with policy IDs, block status, remediation SLA |
| Actual vs Forecast Dashboard | Data + Decision | Not Started | Actual vs forecast with confidence, variance explanation |
| Revenue Funnel Control Center | Decision + Execution | Not Started | End-to-end funnel KPIs and action queue |
| Partnership Scorecards | Data + Decision | Not Started | Fit score, contribution margin, health trend, renewal risk |
| M&A Pipeline Board | Execution + Data | Not Started | Stage pipeline, valuation range, DD status, offer readiness |
| Expansion Launch Console | Execution + Trust | Not Started | Readiness checks, canary state, stop-loss actions |
| PMI 30/60/90 Engine | Execution | Not Started | Plan state, dependencies, escalation aging, synergy tracking |
| Tool Verification Ledger | Trust | Not Started | Receipt log for all sensitive tool calls with trace refs |
| Connector Health Board | Operating + Data | Not Started | Connector latency/error/retry/idempotency visibility |
| Release Gate Dashboard | Operating | Not Started | Rulesets/checks/deploy protection/provenance gate status |
| Saudi Compliance Matrix | Trust + Data | Not Started | PDPL/NCA mappings to controls and evidence |
| Model Routing Dashboard | Decision + Operating | Not Started | Latency, schema adherence, tool reliability, cost per successful task |

---

## Tracking Rules

1. A surface cannot move to `Live (Governed)` without:
   - traceability (`trace_id`, `correlation_id`)
   - approval metadata support (when sensitive)
   - evidence linking
2. Sensitive surfaces must fail closed when policy or auth checks are missing.
3. Weekly review of this tracker is mandatory in the operating cadence.

