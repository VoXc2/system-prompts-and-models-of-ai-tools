# Conversations & Sequences

## Conversation Model

A conversation is the unified timeline of all messages between the tenant and a contact across all channels.

### Schema
```python
class Conversation(TenantModel):
    lead_id = Column(UUID, FK("leads.id"), index=True)
    customer_id = Column(UUID, FK("customers.id"), index=True)
    assigned_to = Column(UUID, FK("users.id"))
    channel = Column(String(50))         # whatsapp, email, sms, voice, web_chat
    status = Column(String(50), index=True)  # open, pending, resolved, closed
    subject = Column(String(500))
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    messages_count = Column(Integer, default=0)
    unread_count = Column(Integer, default=0)
    last_message_at = Column(DateTime)
    sentiment = Column(String(50))       # positive, neutral, negative (AI-scored)
    is_ai_managed = Column(Boolean, default=False)
```

### Conversation States
```
open → pending (waiting for response) → resolved → closed
  │                                        ↑
  └── escalated (to human) ────────────────┘
```

## Sequence System

Sequences are automated multi-step follow-up workflows.

### Sequence Model
```python
class Sequence(TenantModel):
    name = Column(String(255))
    industry = Column(String(100))       # sector-specific
    channel = Column(String(50))         # whatsapp, email, multi
    status = Column(String(50), index=True)  # active, paused, completed
    total_steps = Column(Integer, default=0)
    total_enrolled = Column(Integer, default=0)
    settings = Column(JSONB)
```

### Step Types

| Type | Action | Channel |
|------|--------|---------|
| `send_whatsapp` | Send WhatsApp template message | WhatsApp |
| `send_email` | Send email | Email |
| `ai_reply` | AI generates contextual response | Any |
| `create_task` | Create task for assigned agent | Internal |
| `update_status` | Change lead/deal status | Internal |
| `wait` | Pause for specified duration | — |
| `condition` | Branch based on response/status | — |

### Enrollment Flow
```
Lead enters sequence
  → Check suppression list (PDPL)
    → If suppressed: skip, log reason
    → If clear: enroll
      → Execute step 1
        → Wait for delay
          → Check stop conditions
            → If stopped: exit sequence
            → If continue: execute next step
              → ... until last step
                → Mark completed
```

### Stop Conditions
1. Lead replies (reply_received = true)
2. Lead opts out (added to suppression)
3. Lead converted (status = converted)
4. Lead marked unqualified
5. Sequence paused/deactivated by admin
6. Max attempts reached

### Sequence Worker (Current Implementation)
```python
# Runs every 60 seconds
# 1. Query enrollments WHERE next_step_at <= now AND status = "active"
# 2. For each enrollment:
#    a. Check suppression
#    b. Get current step definition
#    c. Execute step action
#    d. Update current_step and next_step_at
#    e. Check if sequence complete
```

## Template System

### Message Template Model
```json
{
  "name": "welcome_clinic",
  "channel": "whatsapp",
  "language": "ar",
  "category": "follow_up",
  "content": "مرحباً {name}! شكراً لتواصلك مع {company}. كيف يمكننا مساعدتك في {service}؟",
  "variables": ["name", "company", "service"],
  "approved": true,
  "whatsapp_template_name": "welcome_v2"
}
```

### Template Variables
- `{name}` — Contact name
- `{company}` — Tenant company name
- `{agent_name}` — Assigned agent name
- `{service}` — Service type from lead data
- `{deal_value}` — Deal value
- `{meeting_date}` — Next scheduled meeting

## API Endpoints

```
# Conversations
GET    /conversations              # List (with filters)
GET    /conversations/{id}         # Detail with messages
POST   /conversations/{id}/reply   # Send reply

# Sequences
GET    /sequences                  # List sequences
POST   /sequences                  # Create sequence
PUT    /sequences/{id}             # Update
POST   /sequences/{id}/enroll      # Enroll leads
GET    /sequences/{id}/enrollments # View enrollments
```
