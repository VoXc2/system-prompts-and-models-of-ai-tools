# Booking, Webhooks & Integrations

## Booking Flow

### Appointment Model (Current)
```python
class Appointment(TenantModel):
    lead_id = Column(UUID, FK("leads.id"), index=True)
    customer_id = Column(UUID, FK("customers.id"), index=True)
    assigned_to = Column(UUID, FK("users.id"))
    title = Column(String(255))
    service_type = Column(String(100))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, default=30)
    status = Column(String(50), default="pending", index=True)
    booked_via = Column(String(50))  # widget, whatsapp, phone, manual
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    location = Column(String(255))
    notes = Column(Text)
    reminder_sent = Column(Boolean, default=False)
```

### Booking State Machine
```
pending → confirmed → completed
    │        │
    └────────┴──→ cancelled
                      │
                      └──→ rescheduled → pending
```

### Availability Logic
```
GET /appointments/availability?date=2026-04-01&service_type=consultation

Response:
{
  "date": "2026-04-01",
  "slots": [
    {"start": "09:00", "end": "09:30", "available": true},
    {"start": "09:30", "end": "10:00", "available": false},
    ...
  ]
}

Availability = working_hours - existing_appointments - blocked_times
```

### Reminder Schedule
- 24 hours before → WhatsApp/SMS reminder
- 1 hour before → WhatsApp/SMS reminder
- 15 minutes before → Push notification (if available)

## Webhook Architecture

### Inbound Webhooks (External → Dealix)

| Provider | Endpoint | Events |
|----------|----------|--------|
| WhatsApp Business API | `/webhooks/whatsapp` | message.received, status.updated |
| Google Calendar | `/webhooks/calendar` | event.created, event.updated |
| Stripe/Moyasar | `/webhooks/billing` | payment.success, subscription.updated |
| Custom | `/webhooks/inbound/{slug}/{source}` | Any |

### Webhook Processing Flow
```
Receive webhook → Verify signature → Store in webhook_events → Process async

webhook_events table:
  - source: "whatsapp" | "calendar" | "billing" | "custom"
  - event_type: provider-specific event name
  - payload: raw JSONB
  - status: "received" → "processing" → "processed" | "failed"
  - retry_count: 0-3
```

### Signature Verification
```python
def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Integration Framework

### Connector Categories

| Category | Examples | Priority |
|----------|----------|----------|
| Messaging | WhatsApp Business API | P0 |
| Calendar | Google Calendar, Outlook | P1 |
| Email | SMTP, AWS SES, SendGrid | P1 |
| Payment | Moyasar, Stripe | P2 |
| CRM Sync | HubSpot, Salesforce (export) | P2 |
| Analytics | Google Analytics, Meta Pixel | P2 |
| Storage | AWS S3, MinIO | P1 |

### Integration Account Model (Current)
```python
class IntegrationAccount(TenantModel):
    provider = Column(String(100), nullable=False, index=True)
    account_name = Column(String(255))
    account_id = Column(String(255))
    access_token = Column(Text)       # encrypted at rest
    refresh_token = Column(Text)      # encrypted at rest
    token_expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    scopes = Column(JSONB, default=list)
    settings = Column(JSONB, default=dict)
    last_synced_at = Column(DateTime(timezone=True))
    # UniqueConstraint: (tenant_id, provider, account_id)
```

### Connector Core Abstraction (Future)

```python
class BaseConnector:
    """Base class for all integration connectors."""

    provider: str
    required_scopes: list[str]

    async def authenticate(self, credentials: dict) -> IntegrationAccount: ...
    async def refresh_token(self, account: IntegrationAccount) -> IntegrationAccount: ...
    async def test_connection(self, account: IntegrationAccount) -> bool: ...
    async def sync(self, account: IntegrationAccount, since: datetime) -> SyncResult: ...
    async def push(self, account: IntegrationAccount, data: dict) -> PushResult: ...

class WhatsAppConnector(BaseConnector):
    provider = "whatsapp"
    required_scopes = ["messages:read", "messages:write"]

class GoogleCalendarConnector(BaseConnector):
    provider = "google_calendar"
    required_scopes = ["calendar.readonly", "calendar.events"]
```

## API Endpoints

```
# Integrations
GET    /integrations                    # List connected integrations
POST   /integrations                    # Connect new integration
DELETE /integrations/{id}               # Disconnect
GET    /integrations/{id}/status        # Check connection health
POST   /integrations/{id}/sync          # Trigger manual sync

# Webhooks
POST   /webhooks/whatsapp              # WhatsApp Business API
POST   /webhooks/inbound/{slug}/{src}  # Generic inbound webhook

# Booking
GET    /appointments/availability       # Available slots
POST   /appointments                    # Book appointment
POST   /appointments/{id}/confirm       # Confirm
POST   /appointments/{id}/complete      # Mark complete
DELETE /appointments/{id}               # Cancel
```

## Failure Modes & Retry

| Failure | Retry Strategy | Max Retries | Fallback |
|---------|---------------|-------------|----------|
| Webhook delivery timeout | Exponential backoff (1s, 5s, 30s) | 3 | Store as failed, alert |
| Token expired | Auto-refresh, retry once | 1 | Mark integration inactive |
| Rate limited | Respect Retry-After header | 3 | Queue for later |
| Sync conflict | Last-write-wins with audit log | 0 | Manual resolution |
