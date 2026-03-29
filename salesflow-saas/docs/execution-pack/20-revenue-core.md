# Revenue Core

## Entity Relationship Map

```
Account (Company/Organization)
  ├── Contacts (People at account)
  ├── Leads (Unqualified opportunities)
  │     └── Activities, Notes, Tasks
  ├── Deals (Qualified opportunities in pipeline)
  │     ├── Activities, Notes, Tasks
  │     ├── Proposals
  │     └── Contracts
  └── Customer (Converted/won account)
        ├── Deals (historical)
        └── Conversations
```

## Core Entities

### Lead
The entry point for all revenue. Every inbound or outbound opportunity starts as a lead.

| Field | Type | Required | Index | Notes |
|-------|------|----------|-------|-------|
| id | UUID | PK | Yes | |
| tenant_id | UUID | Yes | Yes | Isolation |
| name | String(255) | Yes | | Contact name |
| phone | String(20) | | | Primary in Saudi market |
| email | String(255) | | | |
| source | String(100) | | | website, whatsapp, referral, social, import |
| status | String(50) | | Yes | new, contacted, qualified, unqualified, converted, lost |
| score | Integer | | | 0-100, AI-scored |
| assigned_to | UUID FK | | Yes | User responsible |
| notes | Text | | | Free-form notes |
| extra_data | JSONB | | | Custom fields, enrichment data |

### Lead Lifecycle State Machine
```
new → contacted → qualified → converted (to deal/customer)
  │       │           │
  └───────┴───────────┴──→ unqualified → archived
                            │
                            └──→ reactivated → contacted
```

### Deal
A qualified opportunity progressing through the pipeline toward close.

| Field | Type | Required | Index | Notes |
|-------|------|----------|-------|-------|
| id | UUID | PK | Yes | |
| tenant_id | UUID | Yes | Yes | |
| title | String(255) | Yes | | Deal name |
| lead_id | UUID FK | | Yes | Originating lead |
| customer_id | UUID FK | | Yes | Associated customer |
| assigned_to | UUID FK | | | Deal owner |
| value | Numeric(12,2) | | | Deal value in currency |
| currency | String(3) | | | Default SAR |
| stage | String(50) | | Yes | Pipeline stage |
| probability | Integer | | | 0-100% |
| expected_close_date | Date | | | |
| closed_at | DateTime | | | When won/lost |
| notes | Text | | | |

### Deal Lifecycle State Machine
```
new → negotiation → proposal → closed_won
  │       │            │           │
  └───────┴────────────┴───→ closed_lost
                                  │
                                  └──→ reactivated → negotiation
```

### Customer
A converted lead/deal. The account that generates revenue.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | PK | |
| tenant_id | UUID | Yes | |
| lead_id | UUID FK | | Original lead |
| name | String(255) | Yes | Company/person name |
| phone | String(20) | | |
| email | String(255) | | |
| company_name | String(255) | | |
| lifetime_value | Numeric(12,2) | | Total revenue |
| extra_data | JSONB | | Custom fields |

### Activity
Every interaction with a lead, deal, or customer is tracked.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | UUID | PK | |
| tenant_id | UUID | Yes | |
| lead_id | UUID FK | | |
| deal_id | UUID FK | | |
| user_id | UUID FK | | Who performed |
| type | String(50) | Yes | call, email, meeting, note, task, whatsapp |
| subject | String(255) | | |
| description | Text | | |
| scheduled_at | DateTime | | For future activities |
| completed_at | DateTime | | When done |
| is_automated | Boolean | | AI/sequence generated |

## Service Boundaries

| Service | Responsibility |
|---------|---------------|
| LeadService | CRUD, scoring, dedup, assignment, conversion |
| DealService | CRUD, stage transitions, pipeline queries |
| CustomerService | CRUD, conversion from lead, lifetime value |
| ActivityService | CRUD, timeline queries, automation tracking |
| PipelineService | Stage definitions, velocity, forecasting |
| RoutingService | Assignment rules, round-robin, load balancing |

## Dashboard Contracts

### Lead Inbox
- New leads (last 24h, 7d)
- Unassigned leads count
- Leads by source
- Leads by status
- Average response time

### Pipeline Board
- Deals by stage (kanban view)
- Total pipeline value
- Weighted pipeline
- Deals at risk (stale > X days)
- Stage conversion rates

### Account Workspace
- Customer details
- Deal history
- Conversation timeline
- Activity log
- Lifetime value

## Data Integrity Rules
1. Lead email/phone must be checked against suppression before outreach
2. Deal stage transitions must be logged in audit_log
3. Deleting a lead with active deals is blocked
4. Converting a lead creates a customer AND preserves the lead record
5. Score changes > 20 points trigger a notification
