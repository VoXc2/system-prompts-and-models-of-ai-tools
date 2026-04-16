# المسارات الستة — Dealix Six Tracks

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يحدد هذا الملف المسارات التشغيلية الستة التي تغطي كامل نشاط الشركة — من الإيرادات إلى الحوكمة.

---

## نظرة عامة

Dealix ليس مجرد CRM — هو **نظام تشغيل مؤسسي كامل** مبني على 6 مسارات متوازية:

```
┌────────────────────────────────────────────────────────────────┐
│                    DEALIX SIX TRACKS                            │
│                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Revenue  │ │Partnership│ │ CorpDev  │                       │
│  │    OS    │ │    OS    │ │  M&A OS  │                       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                       │
│       │            │            │                              │
│  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐                       │
│  │Expansion │ │  PMI /   │ │Executive │                       │
│  │    OS    │ │  PMO OS  │ │Governance│                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
│                                                                │
│  ───── Decision Plane ─────── Trust Plane ─────                │
│  ───── Execution Plane ────── Data Plane ──────                │
│  ───────────── Operating Plane ────────────────                │
└────────────────────────────────────────────────────────────────┘
```

---

## Track 1: Revenue OS

**المهمة:** تحويل العملاء المحتملين إلى إيرادات قابلة للقياس.

### المراحل

| المرحلة | الوصف | الوكلاء | الحالة |
|---------|-------|---------|--------|
| Prospecting | اكتشاف عملاء محتملين | Lead Qualification, Outreach Writer | Implemented |
| Qualification | تصنيف وتقييم | Lead Scoring, Sector Strategist | Implemented |
| Proposal | صياغة العروض | Proposal Drafter, CPQ Engine | Implemented |
| Negotiation | التفاوض والاعتراضات | Objection Handler, Deal Agent | Implemented |
| Closing | إغلاق الصفقة | Deal Service, E-Sign | Implemented |
| Post-Sale | ما بعد البيع والتوسع | Customer Onboarding, Revenue Attribution | Implemented |

### المقاييس

| المقياس | الهدف | الحالة |
|---------|-------|--------|
| Lead-to-Close rate | >15% | Tracked via pipeline |
| Average deal cycle | <30 days | Measured |
| Revenue per agent | Measurable | ROI engine active |
| Forecast accuracy | >80% (30-day) | Forecasting service active |

### المكونات الحية

- `backend/app/services/lead_service.py` — Lead CRUD + scoring
- `backend/app/services/deal_service.py` — Deal pipeline management
- `backend/app/services/ai/lead_scoring.py` — AI scoring (0-100)
- `backend/app/services/cpq/` — Quote + proposal generation
- `backend/app/services/predictive_revenue_service.py` — Revenue forecasting
- `backend/app/services/executive_roi_service.py` — ROI dashboards

---

## Track 2: Partnership OS

**المهمة:** بناء وإدارة شبكة شراكات استراتيجية.

### المراحل

| المرحلة | الوصف | الوكلاء | الحالة |
|---------|-------|---------|--------|
| Scout | اكتشاف شركاء محتملين | Affiliate Recruitment Evaluator | Implemented |
| Qualify | تقييم الشريك | Scoring + policy check | Implemented |
| Engage | تفعيل الشراكة | Onboarding Coach | Implemented |
| Manage | إدارة الأداء | Commission engine, performance tracking | Implemented |

### المقاييس

| المقياس | الهدف | الحالة |
|---------|-------|--------|
| Partner activation rate | >60% | Tracked |
| Commission accuracy | 100% | Automated |
| Partner satisfaction | >8/10 | Planned |
| Revenue from partners | >20% of total | Tracked |

### المكونات الحية

- `backend/app/services/affiliate_service.py` — Partner management
- `backend/app/models/affiliate.py` — Partner, performance, deal models
- `backend/app/workers/affiliate_tasks.py` — Automated commission + reporting
- `ai-agents/prompts/affiliate-recruitment-evaluator.md` — Evaluation agent
- `ai-agents/prompts/affiliate-onboarding-coach.md` — Onboarding agent

---

## Track 3: CorpDev / M&A OS

**المهمة:** تقييم وتنفيذ فرص الاستحواذ والاندماج.

### المراحل

| المرحلة | الوصف | الوكلاء | الحالة |
|---------|-------|---------|--------|
| Target | تحديد الأهداف | Acquisition Scouting | Implemented |
| Evaluate | التقييم المالي والاستراتيجي | Company Profiler, ROI Engine | Implemented |
| Negotiate | التفاوض | Deal Negotiator, Strategic Simulator | Implemented |
| Integrate | الدمج بعد الاستحواذ | Integration Concierge | Implemented |

### المكونات الحية

- `backend/app/services/strategic_deals/acquisition_scouting.py`
- `backend/app/services/strategic_deals/company_profiler.py`
- `backend/app/services/strategic_deals/company_twin.py` — Digital twin modeling
- `backend/app/services/strategic_deals/roi_engine.py`
- `backend/app/services/strategic_deals/strategic_simulator.py`
- `backend/app/services/strategic_deals/deal_negotiator.py`

---

## Track 4: Expansion OS

**المهمة:** دخول أسواق جديدة وتوسيع الحضور الجغرافي.

### المراحل

| المرحلة | الوصف | المكونات | الحالة |
|---------|-------|----------|--------|
| Market Research | بحث السوق الجديد | Company Research, OSINT | Implemented |
| Localization | توطين المنتج | Arabic NLP, Localization utils | Implemented |
| Launch | إطلاق في السوق | Go-Live Matrix, Launch checklist | Implemented |
| Scale | توسيع العمليات | Multi-tenant, territory management | Implemented |

### المكونات الحية

- `backend/app/services/company_research.py` — Market intelligence
- `backend/app/services/osint_service.py` — Open-source intelligence
- `backend/app/services/ai/arabic_nlp.py` — Arabic processing
- `backend/app/services/territory_manager.py` — Territory assignment
- `backend/app/services/go_live_matrix.py` — Launch readiness

---

## Track 5: PMI / PMO OS

**المهمة:** إدارة المشاريع والتكامل بعد الاستحواذ.

### المراحل

| المرحلة | الوصف | المكونات | الحالة |
|---------|-------|----------|--------|
| Integrate | دمج الأنظمة | CRM Sync, Integration Service | Implemented |
| Track | تتبع التقدم | Operations Hub, Domain Events | Implemented |
| Optimize | تحسين العمليات | Self-Improvement Loop, Analytics | Implemented |
| Report | تقارير تنفيذية | Management Summary Agent, Executive ROI | Implemented |

### المكونات الحية

- `backend/app/services/operations_hub.py` — Domain event emission
- `backend/app/services/crm_sync_service.py` — Salesforce sync
- `backend/app/services/analytics_service.py` — Business intelligence
- `backend/app/services/executive_roi_service.py` — Executive dashboards
- `backend/app/services/strategy_summary.py` — Strategy reporting

---

## Track 6: Executive / Governance OS

**المهمة:** اتخاذ القرار، الموافقة، المراقبة، والتوجيه.

### المراحل

| المرحلة | الوصف | المكونات | الحالة |
|---------|-------|----------|--------|
| Decide | اتخاذ القرار بمعلومات كاملة | AI recommendations, dashboards | Implemented |
| Approve | الموافقة على الأفعال الحساسة | Approval Center, Policy Gate | Implemented |
| Monitor | مراقبة مستمرة | Health checks, SLA alerts | Implemented |
| Steer | توجيه استراتيجي | Strategy Summary, Forecasting | Implemented |

### المكونات الحية

- `backend/app/openclaw/policy.py` — Policy classification (Class A/B/C)
- `backend/app/openclaw/approval_bridge.py` — Approval routing
- `backend/app/services/outbound_governance.py` — Outbound governance
- `backend/app/services/audit_service.py` — Audit trail
- `backend/app/services/sla_escalation_alerts.py` — SLA enforcement
- `backend/app/services/observability.py` — Monitoring

---

## ربط المسارات بالطبقات الخمس

| الطبقة | Revenue | Partnership | CorpDev | Expansion | PMI/PMO | Executive |
|--------|---------|-------------|---------|-----------|---------|-----------|
| **Decision** | Lead scoring, proposals | Partner eval | M&A analysis | Market research | Analytics | AI recommendations |
| **Execution** | Pipeline workflow | Commission automation | Deal workflow | Launch workflow | CRM sync | Approval workflow |
| **Trust** | PDPL consent | Partner compliance | Due diligence | Localization QA | Audit trail | Policy gates |
| **Data** | CRM, pipeline data | Partner performance | Company profiles | Market data | Project metrics | KPI dashboards |
| **Operating** | CI/CD, monitoring | Scheduled tasks | Security scans | Health checks | Observability | SLA alerts |

---

## Current vs Target

| المسار | Current State | Phase 1 Target (90d) | Full Vision |
|--------|-------------|---------------------|-------------|
| **Revenue OS** | Implemented | Live with 3+ tenants | Self-optimizing |
| **Partnership OS** | Implemented | 10+ active partners | Marketplace |
| **CorpDev / M&A OS** | Implemented (services) | 1 pilot evaluation | Autonomous scouting |
| **Expansion OS** | Partial (Saudi only) | GCC expansion plan | Multi-region |
| **PMI / PMO OS** | Implemented (basic) | Full project tracking | Predictive PMO |
| **Executive / Governance OS** | Partial (approval + audit) | Full dashboard | Self-steering |

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../MASTER_OPERATING_PROMPT.md)
- الطبقات الخمس: [`governance/planes-and-runtime.md`](governance/planes-and-runtime.md)
- نسيج التنفيذ: [`governance/execution-fabric.md`](governance/execution-fabric.md)
- مصفوفة 90 يوم: [`execution-matrix-90d-tier1.md`](execution-matrix-90d-tier1.md)
