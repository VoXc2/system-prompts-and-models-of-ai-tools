# AI Evals & Approvals Framework

## Eval Architecture

```
Production AI Call
  → Output generated
    → Auto-validation (schema + safety)
      → If approval required → Approval Queue
      → If auto-approved → Execute
    → Trace logged
      → Sampled for eval
        → Graded (auto + human)
          → Feedback loop → Prompt improvement
```

## Auto-Validation Checks

| Check | Applied To | Action on Fail |
|-------|-----------|----------------|
| JSON schema validation | All structured outputs | Retry once, then flag |
| Content safety | Public-facing content | Block, flag for review |
| Language check | Arabic outputs | Retry with language emphasis |
| PII detection | All outputs | Redact, log warning |
| Hallucination signals | Factual claims | Flag for human review |
| Brand safety | Social comments | Block, require manual approval |

## Approval Framework

### Which Actions Require Approval

| Action | First Time | Subsequent | Confidence > 0.9 |
|--------|-----------|------------|-------------------|
| Send WhatsApp (sequence) | Yes | No (auto) | No (auto) |
| Post social comment | Always | Always | Always |
| Draft proposal | Always | Always | Still requires review |
| Reactivation message | Yes | No (auto) | No (auto) |
| Lead qualification | No | No | No |
| Meeting prep | No | No | No |
| Executive summary | No | No | No |

### Approval Queue Storage
Approvals are stored in the existing models:
- `CommentDraft.status = "pending"` → Social comment approval
- `Proposal.status = "draft"` → Proposal approval
- Future: generic `ApprovalRequest` model for extensibility

### Approval SLA
- Social comments: Review within 2 hours during business hours
- Proposals: Review within 4 hours
- Messages: Review within 1 hour
- Alert if approval queue > 10 items

## Trace-Based Quality Review

### Sampling Strategy
```
Daily: Sample 5% of all AI traces (min 20, max 200)
Stratify by:
  - Agent type (ensure coverage)
  - Status (over-sample errors)
  - Confidence (over-sample low confidence)
  - Human override (100% sample rate)
```

### Grading Rubric Template
```markdown
## Grading: {Agent Name} Output

### Correctness (1-5)
- 5: Perfect output, no changes needed
- 4: Minor issues, usable as-is
- 3: Needs editing but core is correct
- 2: Significant errors, mostly needs rewrite
- 1: Wrong/harmful/irrelevant

### Relevance (1-5)
- 5: Perfectly relevant to context
- 4: Relevant with minor tangents
- 3: Somewhat relevant
- 2: Mostly irrelevant
- 1: Completely off-topic

### Tone (1-5) [for content agents]
- 5: Perfect professional Arabic tone
- 4: Good tone, minor awkwardness
- 3: Acceptable but could be better
- 2: Inappropriate tone
- 1: Offensive or harmful tone
```

### Regression Prevention
When a graded trace scores 4+ on all dimensions:
1. Add to golden dataset
2. Include in regression suite
3. New prompt versions must maintain quality on these examples

When a trace scores 2 or below:
1. Root-cause analysis
2. Add to edge-case dataset
3. Adjust prompt or add guardrail
4. Re-run regression suite

## Cost Governance

### Budget Controls
```python
MONTHLY_AI_BUDGET = {
    "trial": 10.00,        # USD
    "basic": 50.00,
    "professional": 200.00,
    "enterprise": 1000.00,
    "managed": 2000.00,
}
```

### Cost Alert Thresholds
- 50% budget used → Info notification
- 80% budget used → Warning to admin
- 95% budget used → Throttle non-critical AI calls
- 100% budget used → Only critical agents (qualification, routing) continue

### Cost Optimization
1. Use cheapest viable model for each task
2. Cache repeated queries (same input → same output for deterministic tasks)
3. Batch similar requests where possible
4. Review high-cost agents monthly for prompt optimization
