# الطبقات والتشغيل — Planes & Runtime Architecture

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16

---

## 1. النموذج ذو الخمس طبقات

Dealix مبني على 5 طبقات (planes) مستقلة ومتكاملة:

```
┌─────────────────────────────────────────────────────────────┐
│                     DECISION PLANE                           │
│  AI Agents │ LLM Routing │ Scoring │ Recommendations         │
│  19 agents │ 5-tier provider chain │ Arabic NLP              │
│  الحالة: Implemented                                         │
├─────────────────────────────────────────────────────────────┤
│                     EXECUTION PLANE                          │
│  FastAPI │ Celery Workers │ OpenClaw Durable Flows           │
│  Deterministic workflows │ Facade-gated external calls       │
│  الحالة: Implemented                                         │
├─────────────────────────────────────────────────────────────┤
│                      TRUST PLANE                             │
│  Policy Gate │ Approval Routing │ Audit Logs │ PDPL          │
│  Tool Verification │ Evidence Packs │ Consent Engine          │
│  الحالة: Partial (core implemented, advanced planned)        │
├─────────────────────────────────────────────────────────────┤
│                       DATA PLANE                             │
│  PostgreSQL 16 │ pgvector │ Mem0 │ Letta │ Redis             │
│  Multi-tenant │ CRM grounding │ RAG │ Knowledge Service      │
│  الحالة: Implemented                                         │
├─────────────────────────────────────────────────────────────┤
│                    OPERATING PLANE                            │
│  GitHub Actions │ Docker │ Health Checks │ Observability      │
│  CI/CD │ Monitoring │ SLA Alerts │ Deployment                │
│  الحالة: Partial (basic CI, health checks)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Decision Plane — طبقة القرار

### المسؤولية
التفكير، التصنيف، التوصية، التحليل — **بدون التزام خارجي**.

### المكونات

| المكون | الملف | الوصف | الحالة |
|--------|-------|-------|--------|
| Agent Registry | `backend/app/ai/agent_executor.py` | 19 وكيل مسجل | Implemented |
| Manus Orchestrator | `backend/app/services/agents/manus_orchestrator.py` | تنسيق متعدد الوكلاء | Implemented |
| Hermes Router | `backend/app/services/hermes_orchestrator.py` | توجيه حسب النية | Implemented |
| LLM Provider | `backend/app/services/llm/provider.py` | سلسلة 5 مزودين | Implemented |
| Model Router | `backend/app/services/ai/model_router.py` | توجيه حسب المهمة | Implemented |
| Arabic NLP | `backend/app/services/ai/arabic_nlp.py` | نية، مشاعر، كيانات | Implemented |
| Lead Scoring | `backend/app/services/ai/lead_scoring.py` | درجة 0-100 | Implemented |
| Forecasting | `backend/app/services/ai/forecasting.py` | توقع إيرادات | Implemented |

### القاعدة الذهبية
> **Agent يقترح structured output فقط** — لا يرسل رسالة، لا يعدل DB، لا يستدعي API خارجي مباشرة.

---

## 3. Execution Plane — طبقة التنفيذ

### المسؤولية
تنفيذ الأفعال المعتمدة عبر workflows حتمية.

### المكونات

| المكون | الملف | الوصف | الحالة |
|--------|-------|-------|--------|
| FastAPI | `backend/app/main.py` | 313+ endpoint | Implemented |
| Celery Workers | `backend/app/workers/` | 8 task files, 12+ schedules | Implemented |
| Durable Flows | `backend/app/openclaw/durable_flow.py` | Checkpoint-based persistence | Implemented |
| Sequence Engine | `backend/app/services/sequence_engine.py` | Email/SMS sequences | Implemented |
| Autopilot | `backend/app/services/autopilot.py` | Autonomous pipeline | Implemented |
| Integration Facades | `backend/app/integrations/` | WhatsApp, Email, SMS | Implemented |

### Facade Pattern

كل خدمة خارجية تُستدعى عبر facade واحد فقط:

```
Agent Decision
    │
    ▼
Policy Gate (Class A/B/C)
    │
    ▼
Execution Workflow
    │
    ▼
┌─────────────────────────────────────┐
│          Integration Facades         │
│                                     │
│  whatsapp.py  │  email_sender.py    │
│  sms.py       │  stripe_service.py  │
│  salesforce_agentforce.py           │
│  voice_service.py                   │
└─────────────────────────────────────┘
```

---

## 4. Trust Plane — طبقة الثقة

### المسؤولية
ضمان أن كل فعل مصرح، مسجل، قابل للتدقيق، ومتوافق مع السياسات.

### المكونات

| المكون | الملف | الوصف | الحالة |
|--------|-------|-------|--------|
| Policy Gate | `backend/app/openclaw/policy.py` | تصنيف Class A/B/C | Implemented |
| Approval Bridge | `backend/app/openclaw/approval_bridge.py` | توجيه الموافقات | Implemented |
| Outbound Governance | `backend/app/services/outbound_governance.py` | بوابة الرسائل الصادرة | Implemented |
| Audit Service | `backend/app/services/audit_service.py` | سجل تدقيق كامل | Implemented |
| PDPL Consent | `backend/app/services/pdpl/consent_manager.py` | إدارة الموافقات | Implemented |
| Data Rights | `backend/app/services/pdpl/data_rights.py` | حقوق صاحب البيانات | Implemented |
| Tool Verification | `backend/app/services/tool_verification.py` | تحقق من الأدوات | Implemented |
| Tool Receipts | `backend/app/services/tool_receipts.py` | إيصالات التنفيذ | Implemented |
| Security Gate | `backend/app/services/security_gate.py` | فحص أمني | Implemented |
| Domain Events | `backend/app/services/operations_hub.py` | أحداث غير قابلة للتعديل | Implemented |

### المكونات المستقبلية

| المكون | الوصف | الحالة | الأولوية |
|--------|-------|--------|---------|
| External Policy Engine (OPA) | سياسات خارجية بدل hardcoded | Planned | P2 |
| Fine-grained Auth (OpenFGA/Cedar) | تفويض دقيق | Planned | P2 |
| Evidence Pack Viewer | عرض أدلة القرار | Planned | P1 |
| Contradiction Detection | كشف التناقضات | Planned | P2 |

→ التفصيل الكامل: [`trust-fabric.md`](trust-fabric.md)

---

## 5. Data Plane — طبقة البيانات

### المسؤولية
تخزين، استرجاع، وضمان جودة البيانات عبر كل المسارات.

### المكونات

| المكون | التقنية | الوصف | الحالة |
|--------|---------|-------|--------|
| Primary DB | PostgreSQL 16 + asyncpg | 80+ entities, multi-tenant | Implemented |
| Vector Search | pgvector | RAG + semantic search | Implemented |
| Cache/Broker | Redis 7 | Cache + Celery broker | Implemented |
| Scoped Memory | Mem0 | Per agent/deal/customer | Implemented |
| Tiered Memory | Letta | Progressive retrieval | Implemented |
| Knowledge | KnowledgeService | Sector assets + articles | Implemented |
| Migrations | Alembic | Versioned schema changes | Implemented |

### مبادئ البيانات

1. **Tenant isolation**: كل table يحمل `tenant_id` — لا استثناءات
2. **Money = Numeric**: لا Float أبداً للمبالغ المالية
3. **Timezone = Asia/Riyadh**: التوقيت الافتراضي
4. **Currency = SAR**: العملة الافتراضية
5. **UUID primary keys**: لكل entity
6. **Audit timestamps**: `created_at`, `updated_at` على كل table

### المكونات المستقبلية

| المكون | الوصف | الحالة |
|--------|-------|--------|
| Metric Dictionary | قاموس مقاييس موحد | Planned |
| Data Quality (Great Expectations) | فحوصات جودة بيانات | Planned |
| Lineage (OpenLineage/OpenMetadata) | تتبع مصدر البيانات | Planned |
| Connector Facade Standard | معيار موحد للموصلات | Planned |

---

## 6. Operating Plane — طبقة التشغيل

### المسؤولية
نشر، مراقبة، وصيانة النظام.

### المكونات

| المكون | الوصف | الحالة |
|--------|-------|--------|
| GitHub Actions | Secret scanning + repo hygiene | Implemented |
| Docker Compose | Full stack locally | Implemented |
| Health Checks | `/api/v1/health`, `/api/v1/ready` | Implemented |
| SLA Alerts | `sla_escalation_alerts.py` | Implemented |
| Observability | `observability.py` | Implemented |
| Go-Live Matrix | Launch readiness verification | Implemented |

### المكونات المستقبلية

| المكون | الوصف | الحالة |
|--------|-------|--------|
| Full CI/CD Pipeline | Test + lint + build + deploy | Planned |
| CODEOWNERS | Code owner assignments | Planned |
| Branch Protection | Required reviews + checks | Planned |
| Environment Configs | Staging/production gates | Planned |
| Artifact Attestations | Supply chain security | Planned |

---

## 7. Runtime Flow

```
User/System Event
       │
       ▼
┌─────────────┐
│  API Layer   │──── Operating Plane (health, metrics)
│  (FastAPI)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│  Decision    │───▶│  Trust Plane  │
│   Plane      │    │  (policy,     │
│  (AI agents) │    │   approval,   │
└──────┬──────┘    │   audit)      │
       │           └──────┬───────┘
       ▼                  │
┌─────────────┐           │
│  Execution   │◀──────────┘
│   Plane      │
│  (workflows) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Data Plane  │
│  (store,     │
│   memory,    │
│   RAG)       │
└─────────────┘
```

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)
- نسيج التنفيذ: [`execution-fabric.md`](execution-fabric.md)
- نسيج الثقة: [`trust-fabric.md`](trust-fabric.md)
- رادار التقنية: [`technology-radar-tier1.md`](technology-radar-tier1.md)
