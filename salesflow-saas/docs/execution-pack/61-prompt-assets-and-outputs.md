# Prompt Assets & Structured Outputs

## Prompt Asset Directory Structure

```
packages/prompt-assets/
├── system-prompts/
│   ├── qualification/
│   │   ├── score-lead.md
│   │   └── qualify-lead.md
│   ├── content/
│   │   ├── generate-post.md
│   │   ├── generate-comment.md
│   │   └── generate-hooks.md
│   ├── sales/
│   │   ├── draft-followup.md
│   │   ├── draft-proposal.md
│   │   ├── meeting-prep.md
│   │   └── reactivation.md
│   ├── routing/
│   │   ├── classify-intent.md
│   │   └── assign-agent.md
│   ├── analytics/
│   │   ├── executive-summary.md
│   │   └── anomaly-detection.md
│   └── compliance/
│       └── review-content.md
├── output-schemas/
│   ├── lead-score.json
│   ├── comment-draft.json
│   ├── proposal-content.json
│   ├── meeting-brief.json
│   ├── executive-summary.json
│   └── intent-classification.json
├── evals/
│   ├── datasets/
│   │   ├── qualification-golden.jsonl
│   │   ├── comment-quality-golden.jsonl
│   │   └── proposal-quality-golden.jsonl
│   ├── rubrics/
│   │   ├── qualification-rubric.md
│   │   ├── comment-rubric.md
│   │   └── proposal-rubric.md
│   └── results/
│       └── .gitkeep
└── README.md
```

## System Prompt Template Standard

```markdown
# {Agent Name}

## Role
You are {role description}.

## Context
- Tenant: {tenant_name} in {industry} industry
- Language: Arabic (primary), English (secondary)
- Market: Saudi Arabia B2B

## Input
{description of what you'll receive}

## Output Format
Return ONLY valid JSON matching this schema:
{json_schema}

## Rules
1. {rule 1}
2. {rule 2}
...

## Examples
### Input
{example input}

### Expected Output
{example output}
```

## Output Schema Validation

Every AI response is validated:
```python
import jsonschema

def validate_ai_output(response: dict, schema_name: str) -> tuple[bool, list]:
    schema = load_schema(schema_name)
    try:
        jsonschema.validate(response, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
```

If validation fails:
1. Log error in AI trace
2. Retry once with stricter prompt
3. If still fails, return safe default + flag for human review

## Eval Strategy

### Dataset Types
- **Golden dataset**: Hand-curated input/output pairs (ground truth)
- **Regression dataset**: Previously correct outputs that must stay correct
- **Edge cases**: Known tricky inputs (Arabic dialects, mixed languages, etc.)

### Eval Metrics

| Agent | Metric | Target |
|-------|--------|--------|
| Qualification | Score accuracy (vs human label) | > 80% |
| Qualification | Qualification accuracy (qualified/not) | > 85% |
| Comment Draft | Human approval rate | > 70% |
| Comment Draft | Tone correctness | > 90% |
| Proposal Draft | Acceptance after edit rate | > 60% |
| Follow-up Draft | Send rate (approved as-is or with minor edit) | > 65% |
| Intent Classification | Accuracy | > 90% |

### Eval Cadence
- On every prompt change: run regression suite
- Weekly: sample 50 recent AI traces, grade manually
- Monthly: update golden datasets with new examples
- Quarterly: full eval across all agents

## Approval Queue Design

### Approval States
```
pending → approved → executed
    │
    ├── rejected (with reason)
    │
    └── edited → approved → executed
```

### Approval UI Contract
```json
{
  "queue": [
    {
      "id": "uuid",
      "agent": "comment_draft",
      "entity_type": "social_post",
      "entity_id": "uuid",
      "created_at": "2026-03-29T14:00:00Z",
      "content": {
        "original": "AI drafted comment text...",
        "context": "Original post: ...",
        "confidence": 0.82
      },
      "actions": ["approve", "edit", "reject"]
    }
  ]
}
```
