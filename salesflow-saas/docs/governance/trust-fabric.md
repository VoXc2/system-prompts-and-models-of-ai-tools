# نسيج الثقة — Trust Fabric

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يحدد هذا الملف بنية الثقة في Dealix — كيف نضمن أن كل فعل مصرح، مسجل، قابل للتحقق، ومتوافق.

---

## 1. المبدأ الأساسي

> **Trust is not assumed — it is verified, logged, and proven.**

الثقة في Dealix ليست افتراضية. كل فعل يمر عبر 5 بوابات:

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Policy   │───▶│ Approval  │───▶│ Execution │───▶│ Evidence  │───▶│  Audit   │
│  Gate    │    │ Routing   │    │ Verification│   │   Pack    │    │   Log    │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

---

## 2. بوابة السياسة (Policy Gate)

### 2.1 تصنيف الأفعال

**ملف:** `backend/app/openclaw/policy.py`

| الفئة | الأفعال | القاعدة | الحالة |
|-------|---------|--------|--------|
| **Class A** (تلقائي) | read_status, collect_signals, summarize, classify, tag, research, generate_draft, plan, predictive_analysis | تنفيذ فوري بدون موافقة | Implemented |
| **Class B** (موافقة) | send_whatsapp, send_email, send_linkedin, trigger_voice_call, sync_salesforce, create_charge, publish_content, change_billing_state, send_contract_for_signature | يحتاج موافقة بشرية + audit trail | Implemented |
| **Class C** (ممنوع) | exfiltrate_secrets, delete_data_without_audit, bypass_auth, publish_without_approval, destructive_unchecked | ممنوع دائماً — يولد تنبيه أمني | Implemented |

### 2.2 التطبيق

```python
# من policy.py
SAFE_AUTO_ACTIONS = {
    "read_status", "collect_signals", "summarize",
    "classify", "tag", "research", "generate_draft",
    "plan", "predictive_analysis"
}

APPROVAL_GATED = {
    "send_whatsapp", "send_email", "create_charge",
    "sync_salesforce", "send_contract_for_signature", ...
}

FORBIDDEN = {
    "exfiltrate_secrets", "delete_data_without_audit",
    "bypass_auth", ...
}
```

---

## 3. توجيه الموافقات (Approval Routing)

### 3.1 البنية

**ملف:** `backend/app/openclaw/approval_bridge.py`

```python
class ApprovalBridge:
    def evaluate(self, action, context) -> ApprovalDecision:
        if action in SAFE_AUTO_ACTIONS:
            return ApprovalDecision(allowed=True)
        
        if action in FORBIDDEN:
            return ApprovalDecision(allowed=False, reason="Forbidden action")
        
        if context.tenant_id in CANARY_TENANTS:
            return ApprovalDecision(allowed=True, canary=True)
        
        return ApprovalDecision(
            allowed=False,
            requires_approval=True,
            reason="Approval required"
        )
```

### 3.2 Approval Packet Schema

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "action": "send_whatsapp",
  "agent_id": "arabic_whatsapp",
  "payload": {
    "recipient": "+966...",
    "message_preview": "...",
    "consent_verified": true
  },
  "sensitivity": "high",
  "reversibility": "none",
  "requester": "agent:arabic_whatsapp",
  "approver": "role:admin",
  "sla_hours": 2,
  "status": "pending",
  "created_at": "2026-04-16T10:00:00Z",
  "evidence": {
    "consent_id": "uuid",
    "lead_score": 85,
    "scoring_model": "v2.1"
  }
}
```

### 3.3 SLA Enforcement

| الفعل | SLA | عند التجاوز |
|-------|-----|------------|
| send_whatsapp | 2 ساعات | تنبيه + تصعيد للمدير |
| create_charge | 1 ساعة | تنبيه + تجميد |
| send_contract | 24 ساعة | تنبيه |
| sync_salesforce | 24 ساعة | إعادة جدولة |

---

## 4. تحقق الأدوات (Tool Verification)

### 4.1 Tool Verification Receipt

**ملف:** `backend/app/services/tool_verification.py`, `tool_receipts.py`

كل أداة تُنفذ تولد receipt:

```json
{
  "receipt_id": "uuid",
  "tool_name": "whatsapp_send",
  "agent_id": "arabic_whatsapp",
  "tenant_id": "uuid",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "policy_class": "B",
  "approval_id": "uuid",
  "consent_verified": true,
  "pdpl_check": "passed",
  "execution_time_ms": 342,
  "status": "success",
  "timestamp": "2026-04-16T10:05:00Z",
  "correlation_id": "uuid",
  "trace_id": "uuid"
}
```

### 4.2 Trace/Correlation IDs

```
Trace ID (per user session)
    │
    ├── Correlation ID (per decision chain)
    │       │
    │       ├── Decision → Agent output
    │       ├── Approval → ApprovalRequest
    │       ├── Execution → Tool Receipt
    │       └── Evidence → Evidence Pack
    │
    └── Audit Entries (linked by trace_id)
```

---

## 5. حزمة الأدلة (Evidence Pack)

كل قرار حرج ينتج evidence pack:

```json
{
  "evidence_pack_id": "uuid",
  "decision_type": "lead_qualification",
  "trace_id": "uuid",
  "agent_id": "lead_qualification",
  "tenant_id": "uuid",
  "timestamp": "2026-04-16T10:00:00Z",
  
  "input": {
    "lead_id": "uuid",
    "data_snapshot": { "name": "...", "company": "...", "signals": [...] }
  },
  
  "decision": {
    "score": 85,
    "qualification": "hot",
    "confidence": 0.92,
    "model_version": "v2.1",
    "reasoning": "High engagement signals + matching ICP"
  },
  
  "verification": {
    "policy_check": "passed",
    "consent_check": "not_required",
    "approval_required": false,
    "tool_receipts": ["uuid1", "uuid2"]
  },
  
  "provenance": {
    "data_sources": ["crm", "whatsapp_history", "website_visits"],
    "data_freshness": "2026-04-16T09:55:00Z",
    "model_id": "lead_scoring_v2.1"
  },
  
  "contradiction_check": {
    "contradictions_found": false,
    "notes": null
  }
}
```

---

## 6. سجل التدقيق (Audit Service)

### 6.1 البنية

**ملف:** `backend/app/services/audit_service.py`

```python
class AuditService:
    async def record_audit(
        self, db, tenant_id, user_id, 
        action, entity_type, entity_id,
        changes, ip_address
    ):
        """Record immutable audit entry."""
    
    async def count_audits_since(self, db, tenant_id, since):
        """Count audit entries since timestamp."""
    
    async def list_recent_audits(self, db, tenant_id, limit, offset):
        """Paginated audit trail."""
```

### 6.2 ما يُسجَّل

| الحدث | التفاصيل | مَن |
|-------|---------|-----|
| كل تعديل DB | before/after values | user or agent |
| كل استدعاء خارجي | request/response | system |
| كل موافقة/رفض | decision + reason | approver |
| كل فحص consent | result + consent_id | system |
| كل تسجيل دخول | IP + user agent | user |
| كل تغيير صلاحيات | old/new permissions | admin |

---

## 7. PDPL Compliance Engine

### 7.1 إدارة الموافقات

**ملف:** `backend/app/services/pdpl/consent_manager.py`

```python
class ConsentManager:
    async def grant_consent(self, db, lead_id, purpose, channel, expiry_months=12):
        """Grant consent with automatic 12-month expiry."""
    
    async def revoke_consent(self, db, consent_id, reason):
        """Revoke consent with full audit trail."""
    
    async def check_consent(self, db, lead_id, purpose, channel):
        """Check consent BEFORE any outbound action."""
    
    async def audit_consent_change(self, db, consent_id, action, actor_id, ip):
        """Log every consent change."""
```

### 7.2 قواعد PDPL

| القاعدة | التطبيق | الحالة |
|---------|---------|--------|
| موافقة قبل أي رسالة صادرة | `check_consent()` before send | Implemented |
| تتبع الغرض والقناة | Purpose + channel in consent | Implemented |
| انتهاء تلقائي بعد 12 شهر | `expires_at` field | Implemented |
| حقوق صاحب البيانات | Access, correct, delete | Implemented |
| سجل تدقيق كامل | `PDPLConsentAudit` table | Implemented |
| عقوبة: SAR 5 مليون | Penalty tracking | Documented |
| الدول المسموح النقل إليها | {SA, AE, BH, KW, OM, QA} | Implemented |

### 7.3 حقوق صاحب البيانات

**ملف:** `backend/app/services/pdpl/data_rights.py`

| الحق | SLA | التطبيق |
|------|-----|---------|
| الوصول | 30 يوم | Export user data as JSON |
| التصحيح | 30 يوم | Update records + audit |
| الحذف | 30 يوم | Soft delete + anonymize |
| الاعتراض | 30 يوم | Revoke consent + flag |

---

## 8. المكونات الحية (5 عناصر أساسية)

هذه هي الحد الأدنى المطلوب لتقول "Trust Plane يعمل":

| # | المكون | الحالة | الدليل |
|---|--------|--------|--------|
| 1 | **Approval packet schema** | Implemented | `ApprovalRequest` model + `approval_bridge.py` |
| 2 | **Tool verification receipt** | Implemented | `tool_verification.py` + `tool_receipts.py` |
| 3 | **Evidence pack** | Partial | Schema defined, viewer planned |
| 4 | **Contradiction flag** | Planned | Schema includes field, detection not active |
| 5 | **Trace/correlation IDs** | Partial | Domain events have IDs, full chain linking planned |

---

## 9. Current vs Target

| المكون | Current | Target |
|--------|---------|--------|
| Policy Gate | Hardcoded Python (3 classes) | External OPA engine (Planned) |
| Approval Routing | OpenClaw bridge + DB | SLA-tracked + escalation |
| Fine-grained Auth | Role-based (admin/user) | Attribute-based OpenFGA/Cedar (Planned) |
| Tool Verification | Receipt generation | Full ledger + contradiction detection |
| Evidence Packs | Schema defined | Live viewer + reproducibility test |
| Audit Logs | Full CRUD audit | Searchable + alerting |
| PDPL Consent | Complete engine | Control matrix dashboard |
| Contradiction Detection | Schema placeholder | Active detection |

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)
- الطبقات: [`planes-and-runtime.md`](planes-and-runtime.md)
- نسيج التنفيذ: [`execution-fabric.md`](execution-fabric.md)
- الامتثال السعودي: [`saudi-compliance-and-ai-governance.md`](saudi-compliance-and-ai-governance.md)
