# Pipeline State Machine

## Default Pipeline Stages

```
new → negotiation → proposal → closed_won
                        │
                        └────→ closed_lost
```

| Stage | Probability | SLA (default) | Actions |
|-------|------------|---------------|---------|
| new | 10% | Respond in 1h | Qualify, score, assign |
| negotiation | 30% | Follow up every 48h | Discovery call, needs analysis |
| proposal | 60% | Follow up in 24h after send | Send proposal, negotiate terms |
| closed_won | 100% | — | Convert to customer, celebrate |
| closed_lost | 0% | — | Log lost reason, reactivation queue |

## Stage Transition Rules

### Allowed Transitions
```python
ALLOWED_TRANSITIONS = {
    "new": ["negotiation", "closed_lost"],
    "negotiation": ["proposal", "closed_lost", "new"],  # can regress
    "proposal": ["closed_won", "closed_lost", "negotiation"],
    "closed_won": [],  # terminal
    "closed_lost": ["new"],  # reactivation
}
```

### Transition Side Effects

| From → To | Side Effects |
|-----------|-------------|
| * → closed_won | Set closed_at, probability=100, create customer if none, notify team |
| * → closed_lost | Set closed_at, probability=0, prompt for lost reason, add to reactivation queue |
| closed_lost → new | Clear closed_at, set probability=10, log reactivation in audit |
| new → negotiation | Log first qualification, start SLA timer |
| negotiation → proposal | Auto-create proposal draft if AI enabled |

## Pipeline Velocity Calculation

```
Velocity (SAR/day) = (Qualified Deals × Avg Deal Size × Win Rate) / Avg Sales Cycle Days
```

### Components
- **Qualified Deals**: Count of deals in negotiation + proposal stages
- **Avg Deal Size**: Mean value of closed_won deals (rolling 90 days)
- **Win Rate**: closed_won / (closed_won + closed_lost) (rolling 90 days)
- **Avg Sales Cycle**: Mean days from created_at to closed_at for won deals (rolling 90 days)

## Revenue Forecasting

### Weighted Pipeline
```
For each open deal:
  weighted_value = deal.value × (deal.probability / 100)
Total weighted pipeline = sum(weighted_values)
```

### Time-Based Forecast
```
30-day forecast = sum(weighted_value) for deals with expected_close_date <= today + 30
60-day forecast = sum(weighted_value) for deals with expected_close_date <= today + 60
90-day forecast = sum(weighted_value) for deals with expected_close_date <= today + 90
```

## Risk Detection

| Risk Signal | Threshold | Action |
|-------------|-----------|--------|
| Stale deal (no activity) | 7 days in negotiation, 3 days in proposal | SLA breach, notify owner |
| Aging deal | > 2x avg sales cycle | Flag as at-risk, escalate to manager |
| No next step | Deal has no scheduled activity | Auto-create follow-up task |
| Sudden regression | Moved backward in pipeline | Require reason, audit log |
| Large deal without proposal | value > 50K SAR in negotiation > 5 days | Suggest proposal creation |

## Custom Pipelines (via Playbooks)
Tenants can define custom stages per industry via the Playbook model:
```json
{
  "custom_stages": ["discovery", "demo", "technical_review", "proposal", "negotiation", "closed_won", "closed_lost"]
}
```

Each custom stage inherits default SLA rules unless overridden in the playbook's KPI targets.
