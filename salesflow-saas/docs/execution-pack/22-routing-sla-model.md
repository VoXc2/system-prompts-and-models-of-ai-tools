# Routing & SLA Model

## Lead Routing Rules

### Assignment Strategies

| Strategy | Description | Config |
|----------|-------------|--------|
| **round_robin** | Rotate among active agents | Team or all users |
| **load_balanced** | Assign to agent with fewest open leads | Weight by capacity |
| **skill_based** | Match lead industry/source to agent expertise | Agent skills config |
| **territory** | Assign by geography/region | Territory mapping |
| **manual** | Owner/admin assigns manually | Default for small teams |

### Routing Flow
```
Lead created
  → Check auto_assign setting
    → If enabled:
      → Match routing strategy
      → Check agent availability (active, not at capacity)
      → Assign to best match
      → Start SLA timer
      → Notify assigned agent
    → If disabled:
      → Land in unassigned queue
      → Notify admins
```

## SLA Architecture

### SLA Policy Model
```python
class SLAPolicy(TenantModel):
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), index=True)  # lead, deal
    stage = Column(String(50), index=True)         # specific stage or null
    priority = Column(String(20), default="normal") # low, normal, high, urgent
    first_response_minutes = Column(Integer, default=60)
    follow_up_minutes = Column(Integer, default=1440)     # 24h
    stage_max_minutes = Column(Integer)                     # max time in stage
    resolution_minutes = Column(Integer)                    # max time to close
    escalation_enabled = Column(Boolean, default=True)
    escalation_to = Column(UUID, FK("users.id"))
    business_hours_only = Column(Boolean, default=True)
    business_hours = Column(JSONB)  # {"start":"09:00","end":"17:00","timezone":"Asia/Riyadh"}
```

### SLA Timer Logic

```
When lead enters stage:
  1. Find matching SLA policy (entity_type + stage + priority)
  2. Calculate deadline = now + policy.first_response_minutes
  3. If business_hours_only: skip non-working hours
  4. Store deadline in Redis with TTL
  5. Worker checks every 5 minutes for expired SLAs

When SLA breached:
  1. Create SLABreach record
  2. If escalation_enabled: notify escalation_to
  3. Update breach counter on dashboard
  4. Log to audit trail
```

### SLA Breach Model
```python
class SLABreach(TenantModel):
    policy_id = Column(UUID, FK("sla_policies.id"), index=True)
    entity_type = Column(String(50), index=True)
    entity_id = Column(UUID, index=True)
    assigned_to = Column(UUID, FK("users.id"), index=True)
    breach_type = Column(String(50), index=True)  # first_response, follow_up, stage_timeout
    breached_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    exceeded_by_minutes = Column(Integer)
    escalated = Column(Boolean, default=False)
```

## Default SLA Policies

| Entity | Stage | Priority | First Response | Follow-Up | Stage Max |
|--------|-------|----------|---------------|-----------|-----------|
| lead | new | urgent | 15 min | 4h | 24h |
| lead | new | high | 30 min | 8h | 48h |
| lead | new | normal | 1h | 24h | 72h |
| lead | contacted | normal | — | 48h | 7 days |
| deal | negotiation | normal | — | 48h | 14 days |
| deal | proposal | normal | — | 24h | 7 days |

## SLA Dashboard Widgets

### Active Breach Counter
- Total active breaches (red badge)
- Breaches by type (pie chart)
- Breaches by agent (leaderboard)

### Response Time Metrics
- Avg first response time (trend)
- Avg follow-up interval (trend)
- % within SLA (gauge)

### Stage Aging
- Deals in stage > threshold (table)
- Leads unresponded > threshold (table)
- Escalation queue (action items)

## API Endpoints

```
GET    /sla/policies           # List SLA policies
POST   /sla/policies           # Create policy (admin+)
PUT    /sla/policies/{id}      # Update policy (admin+)
GET    /sla/breaches           # List breaches (filterable)
GET    /sla/stats              # SLA statistics
```

## Testing Requirements
- [ ] SLA timer starts when lead enters tracked stage
- [ ] Business hours calculation correctly skips weekends
- [ ] Breach is created exactly when timer expires
- [ ] Escalation notification fires on breach
- [ ] Resolving entity resolves the breach
- [ ] Stats endpoint correctly aggregates breach data
