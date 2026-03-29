# Proposal & Close Support

## Proposal Lifecycle

```
draft → sent → viewed → negotiating → accepted → signed
  │       │       │          │
  └───────┴───────┴──────────┴──→ rejected → revised → sent
```

### Proposal Model (Current)
```python
class Proposal(TenantModel):
    deal_id = Column(UUID, FK("deals.id"), index=True)
    lead_id = Column(UUID, FK("leads.id"), index=True)
    title = Column(String(255))
    content = Column(JSONB)              # Structured proposal content
    total_amount = Column(Numeric(12, 2))
    currency = Column(String(3), default="SAR")
    status = Column(String(50), default="draft", index=True)
    valid_until = Column(Date)
    sent_at = Column(DateTime)
    viewed_at = Column(DateTime)
```

### Proposal Content Structure
```json
{
  "sections": [
    {
      "title": "ملخص تنفيذي",
      "content": "..."
    },
    {
      "title": "نطاق العمل",
      "items": [
        {"description": "إعداد نظام إدارة العملاء", "amount": 15000},
        {"description": "تدريب الفريق", "amount": 5000}
      ]
    },
    {
      "title": "الجدول الزمني",
      "content": "14 يوم عمل"
    }
  ],
  "total": 20000,
  "currency": "SAR",
  "terms": "الدفع: 50% مقدم، 50% عند التسليم",
  "valid_days": 14
}
```

## Contract Flow (Post-Proposal)

```
draft → sent → viewed → signed (all parties) → active → completed/expired
```

### Contract Model (Current)
```python
class Contract(TenantModel):
    deal_id = Column(UUID, FK("deals.id"), index=True)
    customer_id = Column(UUID, FK("customers.id"), index=True)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(100))  # service_agreement, nda, sow
    content = Column(Text)
    total_value = Column(Numeric(14, 2))
    status = Column(String(50), default="draft", index=True)
    public_url = Column(Text)            # Shareable signing link
    signed_at = Column(DateTime)
    expires_at = Column(DateTime)
```

### Signature Model
```python
class Signature(TenantModel):
    contract_id = Column(UUID, FK("contracts.id"), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255))
    signer_phone = Column(String(20))
    signature_data = Column(Text)        # Base64 signature image or typed name
    ip_address = Column(INET)
    signed_at = Column(DateTime)
```

## Follow-Up After Proposal

### Automated Sequence
```
Day 0: Proposal sent → log activity, notify agent
Day 1: Check if viewed
  → If viewed: notify agent "Proposal viewed!"
  → If not: send reminder to contact
Day 3: If no response → send follow-up message
Day 7: If no response → escalate to manager, suggest call
Day 14: If no response and past valid_until → mark expired, add to reactivation
```

## Follow-Up After Meeting

### Post-Meeting Actions (AI-Assisted)
1. **Meeting summary** — AI generates summary from notes/transcript
2. **Action items** — Extract and create tasks
3. **Follow-up message** — AI drafts thank-you + next steps
4. **Deal update** — Suggest stage change based on meeting outcome

### Meeting Prep (AI Agent)
Before a scheduled meeting:
1. Compile lead/customer history
2. Recent conversations and sentiment
3. Deal stage and value
4. Suggested talking points
5. Competitive intelligence (if available)

## Service Modules

| Service | Responsibility |
|---------|---------------|
| ProposalService | CRUD, generation (AI-assisted), tracking |
| ContractService | CRUD, signing flow, expiry management |
| SignatureService | Signature capture, verification, audit |
| CloseSupport | Orchestrate proposal→contract→close flow |

## API Endpoints

```
# Proposals
GET    /proposals                  # List proposals
POST   /proposals                  # Create (optionally AI-generated)
PUT    /proposals/{id}             # Update
POST   /proposals/{id}/send        # Send to contact
GET    /proposals/{id}/track       # View tracking (opened, etc.)

# Contracts
GET    /contracts                  # List contracts
POST   /contracts                  # Create from proposal or template
POST   /contracts/{id}/send        # Send for signature
GET    /contracts/public/{token}   # Public signing page (no auth)
POST   /contracts/public/{token}/sign  # Submit signature
```
