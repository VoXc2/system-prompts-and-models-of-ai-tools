# رادار التقنية — Technology Radar (Tier 1)

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يصنف هذا الملف كل تقنية في Dealix حسب حالتها الفعلية — بدون ادعاءات، فقط أدلة.

---

## 1. منهجية التصنيف

مستوحى من Thoughtworks Technology Radar مع 4 حلقات:

| الحلقة | المعنى | الدليل المطلوب |
|--------|--------|---------------|
| **ADOPT** | في الإنتاج، معتمد، مستقر | كود يعمل + اختبارات + نشر |
| **TRIAL** | مستخدم في بيئة تطوير/staging، قيد التجربة | كود يعمل + اختبارات محدودة |
| **ASSESS** | قيد التقييم، spike أو POC | كود تجريبي أو وثيقة تقييم |
| **HOLD** | ممنوع أو مؤجل | قرار معماري موثق |

---

## 2. Core Platform

| التقنية | الحلقة | الإصدار | الاستخدام | الدليل |
|---------|--------|---------|----------|--------|
| **Python** | ADOPT | 3.12 | Backend | `backend/` — 115+ service files |
| **FastAPI** | ADOPT | 0.115.6 | API layer | 50+ route files, 313+ endpoints |
| **PostgreSQL** | ADOPT | 16 | Primary DB | Multi-tenant, 80+ entities |
| **Redis** | ADOPT | 7 | Cache + broker | Celery broker, session cache |
| **Celery** | ADOPT | 5 | Task queue | 8 task files, 12+ schedules |
| **SQLAlchemy** | ADOPT | 2.x | ORM | asyncpg driver, all models |
| **Alembic** | ADOPT | Latest | Migrations | Baseline migration exists |
| **Next.js** | ADOPT | 15 | Frontend | 16 pages, dashboard, auth |
| **TypeScript** | ADOPT | 5.x | Frontend lang | All frontend code |
| **Docker** | ADOPT | Latest | Containerization | docker-compose.yml |
| **Pydantic** | ADOPT | 2.x | Validation | All API schemas |

---

## 3. AI / LLM

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **OpenAI API (GPT-4o)** | ADOPT | Primary LLM for high-quality tasks | `llm/provider.py` — active |
| **Groq (Llama 3.1/3.3 70B)** | ADOPT | Fast classification, Arabic NLP | `llm/provider.py` — primary chain |
| **OpenAI Embeddings** | ADOPT | text-embedding-3-small for RAG | `agents/embeddings.py` |
| **pgvector** | ADOPT | Vector search for RAG | `knowledge_service.py` |
| **Mem0** | ADOPT | Scoped agent/deal memory | `memory_engine.py` |
| **Letta** | TRIAL | Tiered memory retrieval | Referenced in blueprint, integration partial |
| **LangGraph** | TRIAL | Supervisors, subgraphs | Referenced in blueprint, test exists |
| **Ollama (qwen2.5:7b)** | TRIAL | Local fallback inference | `local_inference.py` |
| **Claude (Opus 4.6)** | TRIAL | Complex analysis, sales copy | In provider chain, not primary in code |
| **ElevenLabs / Azure Speech** | TRIAL | Voice synthesis + recognition | `voice_service.py` |

---

## 4. Orchestration / Runtime

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **OpenClaw** | ADOPT | Durable flows, policy, approval | `openclaw/` — config + runtime code |
| **OpenClaw Durable Flows** | ADOPT | Checkpoint-based persistence | `durable_flow.py` — working |
| **OpenClaw Policy Gate** | ADOPT | Action classification (A/B/C) | `policy.py` — 3 action classes |
| **OpenClaw Approval Bridge** | ADOPT | Canary + approval routing | `approval_bridge.py` — working |
| **Temporal** | HOLD | Not adopted — using OpenClaw durable flows instead | No code, no config |
| **Kubernetes** | HOLD | Not adopted — Docker Compose for now | No k8s config |

---

## 5. Governance / Security

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **PDPL Consent Engine** | ADOPT | Consent management | `pdpl/consent_manager.py` |
| **Audit Service** | ADOPT | Full CRUD audit trail | `audit_service.py` |
| **Outbound Governance** | ADOPT | Message approval gate | `outbound_governance.py` |
| **Tool Verification** | ADOPT | Execution receipts | `tool_verification.py` |
| **OPA (Open Policy Agent)** | ASSESS | External policy engine | No code — candidate for Trust Plane upgrade |
| **OpenFGA / Cedar** | ASSESS | Fine-grained authorization | No code — candidate for RBAC upgrade |
| **Vault (HashiCorp)** | ASSESS | Secrets management | Mentioned in checklist, no integration |
| **Keycloak** | HOLD | Identity provider | Not adopted — using custom auth |

---

## 6. Integrations

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **WhatsApp Business API** | ADOPT | Primary comms channel (Saudi) | `integrations/whatsapp.py` |
| **SendGrid / SMTP** | ADOPT | Email delivery | `integrations/email_sender.py` |
| **Unifonic SMS** | ADOPT | SMS (Saudi provider) | `integrations/sms.py` |
| **Stripe** | ADOPT | Payment processing | `stripe_service.py` |
| **Salesforce Agentforce** | TRIAL | CRM sync + agent interop | `salesforce_agentforce.py` |
| **Moyasar** | TRIAL | Saudi payment provider | Config in .env, service partial |
| **LinkedIn API** | TRIAL | Outreach channel | `linkedin_service.py` |
| **Google/MS Calendar** | TRIAL | Meeting booking | `meeting_service.py` |

---

## 7. DevOps / SDLC

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **GitHub Actions** | ADOPT | Secret scanning, repo hygiene | `repo-hygiene.yml` |
| **Docker Compose** | ADOPT | Local full-stack | `docker-compose.yml` |
| **pytest** | ADOPT | Backend testing | 19 test files |
| **ruff** | ADOPT | Python linting | Pre-commit hook |
| **Playwright** | TRIAL | E2E testing | CI workflow configured |
| **CODEOWNERS** | ASSESS | Code ownership | Not implemented yet |
| **Branch Protection** | ASSESS | PR requirements | Not enforced yet |
| **Artifact Attestations** | ASSESS | Supply chain security | Not implemented |
| **OIDC** | ASSESS | Federated auth for CI | Not implemented |

---

## 8. Data / Analytics

| التقنية | الحلقة | الاستخدام | الدليل |
|---------|--------|----------|--------|
| **PostgreSQL 16** | ADOPT | Primary data store | All models |
| **pgvector** | ADOPT | Vector embeddings | Knowledge service |
| **Redis 7** | ADOPT | Cache, broker, sessions | Active |
| **asyncpg** | ADOPT | Async PostgreSQL driver | All DB operations |
| **Great Expectations** | ASSESS | Data quality checks | Not implemented — candidate |
| **OpenLineage** | ASSESS | Data lineage tracking | Not implemented — candidate |
| **OpenMetadata** | ASSESS | Metadata management | Not implemented — candidate |
| **Airbyte** | ASSESS | Data integration | Not implemented — candidate |

---

## 9. ADR Gating Rule

> **قاعدة:** قبل أن تنتقل أي تقنية من ASSESS إلى TRIAL، يجب كتابة ADR يوثق:
> 1. المشكلة التي تحلها
> 2. البدائل المدروسة
> 3. القرار وأسبابه
> 4. العواقب والمخاطر
> 5. معايير النجاح/الفشل
> 6. مالك القرار
>
> → ADR template: [`docs/adr/0001-tier1-execution-policy-spikes.md`](../adr/0001-tier1-execution-policy-spikes.md)

---

## 10. Current vs Target Summary

```
                    ADOPT                TRIAL              ASSESS              HOLD
              ┌────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
Platform      │ FastAPI, PG16  │  │              │  │              │  │              │
              │ Redis, Celery  │  │              │  │              │  │              │
              │ Next.js, Docker│  │              │  │              │  │              │
              ├────────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
AI/LLM        │ OpenAI, Groq   │  │ Claude, Letta│  │              │  │              │
              │ pgvector, Mem0 │  │ LangGraph    │  │              │  │              │
              ├────────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
Orchestration │ OpenClaw       │  │              │  │              │  │ Temporal     │
              │ (flows+policy) │  │              │  │              │  │ Kubernetes   │
              ├────────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
Governance    │ PDPL, Audit    │  │              │  │ OPA, OpenFGA │  │ Keycloak     │
              │ Tool Verify    │  │              │  │ Vault        │  │              │
              ├────────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
Integrations  │ WhatsApp, Email│  │ Salesforce   │  │              │  │              │
              │ SMS, Stripe    │  │ LinkedIn     │  │              │  │              │
              └────────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)
- ADR: [`docs/adr/`](../adr/)
- مصفوفة 90 يوم: [`execution-matrix-90d-tier1.md`](../execution-matrix-90d-tier1.md)
