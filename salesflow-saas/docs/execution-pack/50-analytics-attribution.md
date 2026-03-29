# Analytics & Attribution

## Event Schema

Every measurable action produces a growth event.

### Canonical Event Types

| Event | Category | Trigger |
|-------|----------|---------|
| `lead.created` | acquisition | New lead from any source |
| `lead.scored` | qualification | AI scoring completed |
| `lead.qualified` | qualification | Status → qualified |
| `lead.assigned` | routing | Agent assigned |
| `lead.converted` | conversion | Lead → customer/deal |
| `deal.created` | pipeline | New deal created |
| `deal.stage_changed` | pipeline | Stage transition |
| `deal.won` | revenue | Deal closed won |
| `deal.lost` | revenue | Deal closed lost |
| `meeting.booked` | engagement | Appointment created |
| `meeting.completed` | engagement | Meeting happened |
| `proposal.sent` | closing | Proposal sent |
| `proposal.viewed` | closing | Proposal opened |
| `contract.signed` | closing | Contract signed |
| `message.sent` | outreach | Message sent on any channel |
| `message.delivered` | outreach | Message delivered |
| `message.replied` | engagement | Contact replied |
| `sequence.enrolled` | automation | Lead entered sequence |
| `sequence.completed` | automation | Sequence finished |
| `social.post_detected` | listening | Relevant post found |
| `social.comment_published` | engagement | Approved comment posted |
| `form.submitted` | acquisition | Public form submission |

### Event Payload
```json
{
  "event_type": "deal.stage_changed",
  "tenant_id": "uuid",
  "timestamp": "2026-03-29T14:30:00Z",
  "entity_type": "deal",
  "entity_id": "uuid",
  "user_id": "uuid",
  "properties": {
    "from_stage": "negotiation",
    "to_stage": "proposal",
    "deal_value": 50000,
    "currency": "SAR"
  },
  "attribution": {
    "source": "google",
    "medium": "cpc",
    "campaign": "clinics_q1"
  }
}
```

## Attribution Model

### First-Touch Attribution
Credit the source that first brought the lead:
- Lead's original `source` field
- First `GrowthEvent` for that lead

### Multi-Touch Attribution (Future)
Weight credit across all touchpoints:
- First touch: 40%
- Middle touches: 20% (split equally)
- Last touch (before conversion): 40%

### Channel Performance Metrics
```
GET /analytics/channels

{
  "channels": [
    {
      "source": "google",
      "medium": "cpc",
      "leads": 150,
      "qualified": 45,
      "deals_created": 20,
      "deals_won": 8,
      "revenue": 400000,
      "cost": 15000,
      "cpl": 100,        // cost per lead
      "cpa": 1875,       // cost per acquisition
      "roas": 26.7       // return on ad spend
    }
  ]
}
```

## Revenue Intelligence Metrics

### Pipeline Velocity
```
Velocity = (Deals × Avg Size × Win Rate) / Avg Cycle Days
```

### Stage Conversion Rates
```
new → negotiation: 60%
negotiation → proposal: 45%
proposal → closed_won: 35%
Overall: 9.5%
```

### Response Time Metrics
- Avg first response time
- Avg follow-up interval
- % within SLA

### Follow-Up Compliance
- Tasks completed on time %
- Sequence completion rate
- No-response rate by agent

## Dashboard Specifications

### CEO Dashboard
| Widget | Data | Refresh |
|--------|------|---------|
| Revenue this month | Sum of closed_won deals | Real-time |
| Pipeline value | Sum of open deal values | Real-time |
| Pipeline velocity | Calculated metric | Hourly |
| 30/60/90 forecast | Weighted pipeline by date | Hourly |
| Win rate trend | 12-week rolling | Daily |
| Top deals at risk | Stale deals by value | Real-time |

### Revenue Ops Dashboard
| Widget | Data |
|--------|------|
| Funnel conversion rates | Stage-to-stage % |
| Stage aging | Avg days in each stage |
| SLA compliance | % within SLA by stage |
| Agent performance | Leads handled, response time, conversion |
| Channel attribution | Leads + revenue by source |

### Sales Rep Dashboard
| Widget | Data |
|--------|------|
| My pipeline | Own deals by stage |
| Follow-up queue | Overdue + due today tasks |
| Today's meetings | Scheduled appointments |
| My SLA status | Green/yellow/red by metric |
| Activity stats | Calls, messages, meetings this week |

### Operator Dashboard (Dealix Internal)
| Widget | Data |
|--------|------|
| All tenants health | Active, at risk, churning |
| SLA breaches across tenants | Aggregate breaches |
| AI cost this month | Total spend by provider |
| Integration health | Connected, failing, expired |
| Onboarding progress | Tenants in setup phase |
