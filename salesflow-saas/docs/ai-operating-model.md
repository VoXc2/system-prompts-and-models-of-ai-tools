# Dealix — AI Operating Model

> **Owner:** Platform & Runtime Squad
> **Review cadence:** Quarterly
> **Related:** `AGENTS.md`, `docs/governance/`, `docs/EXECUTION-MATRIX.md`

---

## 1. Provider Routing

### Decision Matrix

| Condition | Route To | Reason |
|---|---|---|
| Strategic reasoning, complex analysis, board memos | Claude Opus 4.6 (cloud) | Frontier reasoning quality |
| Fast classification, scoring, routing | Groq (cloud) | Low latency, high throughput |
| Privacy-sensitive internal analysis | Local inference (OpenAI-compatible) | Data stays on-premise |
| Arabic-heavy content (summarization, classification) | Local or Groq with Arabic profiles | Dialect-aware processing |
| Coding tasks | DeepSeek or Claude Sonnet (cloud) | Cost-effective for code |
| Fallback (any provider down) | OpenAI GPT-4o | Reliable backup |
| Cost containment (batch, low-priority) | Local inference | Zero marginal cost |

### Routing Rules

1. **Task classifier** determines: `code | reasoning | classification | arabic_nlp | summarization | research | strategic`
2. **Sensitivity classifier** determines: `public | internal | confidential | regulated`
3. Route `confidential` + `regulated` → local inference first, cloud only with explicit policy approval
4. Route `strategic` → Claude Opus (highest quality reasoning)
5. All routes log: `provider`, `model`, `latency_ms`, `cost_usd`, `success`, `retry_count`

### Provider Scorecard (updated quarterly)

| Provider | Latency p95 | Success Rate | Cost/1K tokens | Arabic Quality | Security |
|---|---|---|---|---|---|
| Claude Opus 4.6 | — | — | — | — | — |
| Groq | — | — | — | — | — |
| Local (Ollama/etc) | — | — | $0 | — | — |
| OpenAI GPT-4o | — | — | — | — | — |
| DeepSeek | — | — | — | — | — |

> Fill with actual benchmarks after Phase 2. Do not claim numbers without evidence.

---

## 2. Tool Verification Layer

### Purpose

Prevent the single most dangerous failure mode in agentic systems: **hallucinated operations** — when an agent claims an action happened but it didn't, or happened differently.

### Verification Record Schema

```json
{
  "run_id": "uuid",
  "agent_id": "string",
  "task_id": "uuid",
  "timestamp": "ISO-8601",
  "intended_action": "string (what the agent was asked to do)",
  "claimed_action": "string (what the agent says it did)",
  "actual_tool_calls": [
    {
      "tool": "string",
      "parameters_hash": "sha256",
      "output_summary": "string",
      "exit_code": "int | null",
      "side_effects": ["file_created:path", "api_called:endpoint", "db_modified:table"]
    }
  ],
  "verification_status": "verified | partially_verified | unverified | contradicted",
  "contradiction_details": "string | null",
  "evidence_paths": ["path/to/file", "audit_entry_id"],
  "reviewed_by": "human_email | auto_verifier",
  "reviewed_at": "ISO-8601 | null"
}
```

### Verification Statuses

| Status | Meaning | Action |
|---|---|---|
| `verified` | Actual execution matches claim with evidence | Continue |
| `partially_verified` | Some claims verified, some unverifiable | Log warning, flag for review |
| `unverified` | Cannot confirm execution happened | Block downstream actions until reviewed |
| `contradicted` | Evidence contradicts the claim | Alert immediately, escalate to human |

### What Gets Verified

- **Always:** DB mutations, external API calls, file creation/deletion, message sends, approval actions
- **Sampling:** Read-only queries, internal calculations, memo generation
- **Never skipped:** Financial commitments, legal documents, partner/customer communications

---

## 3. Release Gate Discipline

### Pre-Release Checklist (automated where possible)

| Gate | Tool/Method | Blocking? |
|---|---|---|
| Unit tests pass | pytest | Yes |
| Integration tests pass | pytest + fixtures | Yes |
| Type checks | mypy / pyright | Yes |
| Linting | ruff / eslint | Yes |
| Dependency audit | pip-audit / npm audit | Yes (critical/high) |
| Secret scanning | gitleaks / GitHub secret scanning | Yes |
| Schema validation | JSON Schema checks on event contracts | Yes |
| Migration safety | Alembic dry-run | Yes |
| Security review (manual) | For auth/payment/admin changes | Yes |
| White-box security scan | Shannon-style (when integrated) | Yes for staging→prod |
| Arabic UI audit | Manual checklist | Yes for user-facing changes |
| Performance regression | Benchmark comparison | Warning |
| Evidence pack completeness | For strategic decisions | Yes for Class B/C actions |

### Environment Promotion

```
feature branch → dev → staging → canary (10%) → production (100%)
```

Each promotion requires:
- All gates passed at current level
- Rollback plan documented
- Rollback tested (for staging→canary and canary→prod)

---

## 4. Memory Governance

### Structure

```
/memory/
  architecture/     # System design decisions, diagrams
  adr/              # Architecture Decision Records
  runbooks/         # Operational procedures
  releases/         # Release notes, post-release reviews
  postmortems/      # Incident postmortems
  growth/           # Partnership & expansion learnings
  ma/               # M&A deal learnings, DD patterns
  security/         # Security findings, threat models
  patterns/         # Reusable workflow patterns
  prompts/          # Effective prompt templates
  providers/        # Provider benchmark history
  benchmarks/       # Performance benchmarks
  experiments/      # A/B tests, pilot results
  customers/        # Customer success patterns
```

### Memory Item Schema

Every memory item must contain:

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Clear, searchable title |
| `type` | Yes | adr / runbook / learning / finding / benchmark / pattern |
| `owner` | Yes | Person or role responsible |
| `date` | Yes | Creation date |
| `confidence` | Yes | high / medium / low / unverified |
| `summary` | Yes | 2-3 sentence summary |
| `source` | Yes | Where this knowledge came from |
| `tags` | Yes | Searchable tags |
| `review_date` | Yes | When to re-evaluate |
| `status` | Yes | active / archived / superseded |

### Memory Rules

1. No dumping without classification
2. No memory item without an owner
3. No memory item without a confidence level
4. Stale items (past review_date) get flagged automatically
5. Duplicates are merged, not accumulated
6. Retrieval is task-aware (filtered by relevance + recency + confidence)

---

## 5. Observability Standards

### Required Telemetry

| Layer | What to trace | Tool |
|---|---|---|
| API | Request/response, latency, errors | OpenTelemetry |
| Agents | Agent invocations, think() calls, message routing | Custom spans |
| Events | Event publish/subscribe, processing time | Event bus metrics |
| Tools | External API calls, DB queries, file operations | OpenTelemetry |
| Governance | Approval requests, decisions, SLA tracking | Audit log + metrics |
| Workflows | State transitions, retries, compensations | Workflow runtime metrics |

### Correlation

Every request must carry:
- `trace_id` (across all systems)
- `correlation_id` (business-level grouping)
- `causation_id` (parent event/action that triggered this)
- `tenant_id` (isolation)

### Dashboards (minimum viable)

1. **Platform health** — API latency, error rates, workflow success rates
2. **Agent performance** — Task completion, think() latency, confidence distribution
3. **Governance** — Approval queue depth, SLA compliance, policy violations
4. **Provider** — Model usage, cost, latency, failure rates by provider
