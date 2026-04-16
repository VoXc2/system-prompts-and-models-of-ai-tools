# نسيج التنفيذ — Execution Fabric

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يحدد هذا الملف كيف تتحول القرارات إلى أفعال — من structured output إلى تنفيذ حقيقي عبر workflows حتمية.

---

## 1. المبدأ الأساسي

> **القرار ≠ التنفيذ.** الذكاء الاصطناعي يقرر، لكن workflow حتمي هو الذي ينفذ.

```
Decision (AI)  →  Structured Output  →  Policy Check  →  Workflow  →  Facade  →  External System
```

لا يوجد مسار مختصر. لا يوجد agent يستدعي API خارجي مباشرة.

---

## 2. أنواع Workflows

### 2.1 Synchronous Workflows (فوري)

تنفذ في نفس الطلب HTTP. مثال: تأهيل lead، حساب score.

```python
# مثال: Lead scoring workflow
@router.post("/leads/{lead_id}/score")
async def score_lead(lead_id: UUID, db: AsyncSession):
    lead = await lead_service.get(db, lead_id)           # Data Plane
    score = await scoring_agent.score(lead)               # Decision Plane
    await lead_service.update_score(db, lead_id, score)   # Execution Plane
    await audit_service.record(db, "lead.scored", lead_id) # Trust Plane
    return {"score": score}
```

### 2.2 Asynchronous Workflows (مؤجل)

تنفذ عبر Celery workers. مثال: إرسال رسائل، تقارير يومية.

| المهمة | التكرار | الملف |
|--------|---------|-------|
| Check pending follow-ups | كل 5 دقائق | `follow_up_tasks.py` |
| Send scheduled messages | كل دقيقة | `message_tasks.py` |
| Daily report | 8 صباحاً | `notification_tasks.py` |
| Affiliate monthly targets | يومياً | `affiliate_tasks.py` |
| Affiliate weekly report | أسبوعياً | `affiliate_tasks.py` |
| AI lead generation | كل 6 ساعات | `affiliate_tasks.py` |
| AI outreach follow-up | كل 30 دقيقة | `affiliate_tasks.py` |
| Auto-bookings | كل 15 دقيقة | `affiliate_tasks.py` |
| Sequence steps | كل 5 دقائق | `sequence_tasks.py` |
| Cleanup expired sequences | يومياً | `sequence_tasks.py` |
| Autopilot pipeline | كل ساعتين | `sequence_tasks.py` |
| Autopilot lead scoring | كل 6 ساعات | `sequence_tasks.py` |

### 2.3 Durable Workflows (طويلة الأمد)

تنفذ عبر OpenClaw durable flows مع checkpointing:

```python
class DurableTaskFlow:
    """Checkpoint-based long-running workflow."""
    
    def checkpoint(self, state: dict):
        """Save state for resume on restart."""
        
    def resume(self):
        """Continue from last checkpoint."""
        
    def complete(self, result: dict):
        """Mark flow as done + generate receipt."""
```

**الـ Flows المعرّفة:**
- `prospecting_crew_v1` — Multi-channel prospecting (WhatsApp, email, LinkedIn, voice)
- `self_improvement_v2` — Continuous self-improvement (6 phases)

---

## 3. Facade Pattern

كل خدمة خارجية تُستدعى عبر facade واحد فقط:

### 3.1 Communication Facades

| Facade | الملف | القنوات |
|--------|-------|---------|
| WhatsApp | `integrations/whatsapp.py` | WhatsApp Business API |
| Email | `integrations/email_sender.py` | SMTP + SendGrid |
| SMS | `integrations/sms.py` | Unifonic (Saudi) |
| Voice | `services/voice_service.py` | ElevenLabs + Azure |
| LinkedIn | `services/linkedin_service.py` | LinkedIn API |

### 3.2 Business Facades

| Facade | الملف | الخدمة |
|--------|-------|--------|
| CRM | `services/salesforce_agentforce.py` | Salesforce Agentforce |
| Payments | `services/stripe_service.py` | Stripe |
| E-Sign | `services/esign_service.py` | DocuSign-like |
| Calendar | `services/meeting_service.py` | Google/Microsoft Calendar |

### 3.3 قواعد Facade

1. **Single point of contact** — لا يوجد مكان آخر يستدعي الخدمة الخارجية
2. **Mock mode** — كل facade يدعم وضع محاكاة للاختبار
3. **Rate limiting** — تحديد معدل الاستدعاء
4. **Error handling** — retry مع backoff
5. **Audit logging** — كل استدعاء مسجل
6. **Consent check** — فحص الموافقة قبل الإرسال (PDPL)

---

## 4. مسار الموافقة (Approval Flow)

### 4.1 المسار الكامل

```
Agent Decision
    │
    ▼
┌──────────────────┐
│  Policy Gate      │
│  (policy.py)      │
│                   │
│  Class A? ──▶ Auto-execute
│  Class B? ──▶ Create ApprovalRequest
│  Class C? ──▶ Block + Alert
└────────┬─────────┘
         │ (Class B)
         ▼
┌──────────────────┐
│  Approval Bridge  │
│  (approval_bridge.py) │
│                   │
│  Canary tenant? ──▶ Auto-execute (with logging)
│  Normal tenant? ──▶ Route to approver
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ApprovalRequest  │
│  (model)          │
│                   │
│  Status: PENDING  │
│  SLA: 24h         │
│  Approver: admin  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Approve  │ Reject
    ▼         ▼
Execute    Log + Alert
    │
    ▼
Domain Event
    │
    ▼
Audit Log
```

### 4.2 الأفعال التي تحتاج موافقة (Class B)

| الفعل | المسار | SLA |
|-------|--------|-----|
| `send_whatsapp` | Revenue OS, Partnership OS | 2h |
| `send_email` | Revenue OS | 4h |
| `send_linkedin` | Revenue OS | 4h |
| `trigger_voice_call` | Revenue OS | 2h |
| `sync_salesforce` | All tracks | 24h |
| `create_charge` | Revenue OS | 1h |
| `publish_content` | Expansion OS | 24h |
| `change_billing_state` | Revenue OS | 1h |
| `send_contract_for_signature` | Revenue OS, CorpDev OS | 24h |

---

## 5. Domain Events

كل فعل مهم يولد domain event غير قابل للتعديل:

```python
await operations_hub.emit_domain_event(
    db=db,
    tenant_id=tenant_id,
    event_type="whatsapp.outbound.deferred_for_approval",
    payload={
        "lead_id": str(lead_id),
        "message_preview": message[:100],
        "approval_request_id": str(request.id),
    }
)
```

### أنواع الأحداث

| النوع | المعنى | المسار |
|-------|--------|--------|
| `lead.qualified` | Lead تأهل | Revenue OS |
| `deal.won` | صفقة مغلقة | Revenue OS |
| `deal.lost` | صفقة خسرت | Revenue OS |
| `whatsapp.outbound.sent` | رسالة أرسلت | Revenue OS |
| `whatsapp.outbound.deferred_for_approval` | رسالة في انتظار الموافقة | Trust Plane |
| `partner.activated` | شريك فُعّل | Partnership OS |
| `commission.paid` | عمولة دُفعت | Partnership OS |
| `consent.granted` | موافقة PDPL | Trust Plane |
| `consent.revoked` | إلغاء موافقة | Trust Plane |

---

## 6. Error Handling & Resilience

### 6.1 Retry Strategy

```python
# Exponential backoff with jitter
retry_delays = [2, 4, 8, 16]  # seconds
max_retries = 4
```

### 6.2 Circuit Breaker

- عند 3 أخطاء متتالية لخدمة خارجية → فتح الدائرة
- محاولة إعادة الاتصال بعد 60 ثانية
- تنبيه فوري عند فتح الدائرة

### 6.3 Dead Letter Queue

- الرسائل التي فشلت بعد كل المحاولات → dead letter queue
- مراجعة يومية من ops team
- تنبيه إذا تجاوز عدد الرسائل الميتة 10

---

## 7. Current vs Target

| المكون | الحالة الحالية | الهدف |
|--------|---------------|-------|
| Sync Workflows | Implemented | — |
| Async Workflows (Celery) | Implemented (12+ schedules) | Add monitoring dashboard |
| Durable Flows (OpenClaw) | Implemented (checkpoint-based) | Full Temporal-like |
| Approval Flow | Implemented | Add SLA tracking |
| Domain Events | Implemented | Add event replay |
| Facade Pattern | Implemented | Add standard interface |
| Error Handling | Implemented (retry) | Add circuit breaker |
| Dead Letter Queue | Planned | Implement |

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)
- الطبقات: [`planes-and-runtime.md`](planes-and-runtime.md)
- نسيج الثقة: [`trust-fabric.md`](trust-fabric.md)
