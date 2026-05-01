# Dealix Autonomous Revenue Company OS

> **الفئة الجديدة:** Dealix ليس CRM ولا أداة واتساب ولا AI agent ولا lead scraper.
> هو **شركة نمو رقمية ذاتية التشغيل** تدخل أي بزنس، تفهمه، تبني خطة نمو، تشغّل الخدمات المناسبة، تطلب موافقات، تنسق القنوات، تفتح شراكات، ترتب اجتماعات، تجهز مدفوعات، وتثبت العائد.

---

## 1. القيم الأساسية للنظام

```
Signal → Context → Service Recommendation → Workflow →
Risk Check → Draft → Approval → Execution/Export →
Outcome → Proof → Learning → Upgrade
```

كل event داخل Dealix يمر بهذه السلسلة. لا توجد فجوة بين "إشارة" و"إيراد".

---

## 2. الطبقات الـ12

| الطبقة | الموقع |
|--------|--------|
| Autonomous Service Operator | `auto_client_acquisition/autonomous_service_operator/` |
| Service Tower | `auto_client_acquisition/service_tower/` |
| Service Excellence OS | `auto_client_acquisition/service_excellence/` |
| Targeting OS | `auto_client_acquisition/targeting_os/` |
| Safe Tool Gateway | `auto_client_acquisition/platform_services/tool_gateway.py` |
| Agent Runtime | كل layer يحدد الـ agents فيه |
| Workflow Engine | `service_orchestrator + workflow_runner` |
| Revenue Graph | `revenue_company_os/action_graph.py` |
| Proof Ledger | `revenue_company_os/proof_ledger.py` + `platform_services/proof_ledger.py` |
| Self-Improving Layer | `revenue_company_os/self_improvement_loop.py` + `growth_curator/` |
| Revenue Launch System | `revenue_launch/` + `launch_ops/` |
| Growth Memory | `revenue_company_os/growth_memory.py` |

---

## 3. Autonomous Service Operator

**16 module + 28 endpoint.** البوت المركزي:

- **`intent_classifier`** — 16 intent عبر Arabic + English keywords (deterministic).
- **`conversation_router`** — كل intent → handler + خدمة موصى بها.
- **`session_state`** — 13 حالة جلسة + audit history.
- **`intake_collector`** — أسئلة intake لكل intent + validation.
- **`approval_manager`** — كروت ≤3 أزرار + decisions (approve/edit/skip/reject).
- **`service_orchestrator`** — pipeline 11-step canonical.
- **`workflow_runner`** — advance + completion check.
- **`tool_action_planner`** — يحظر LinkedIn scraping/auto-DM، يطلب approval لـ high-risk، draft فقط للآمنة.
- **`proof_pack_dispatcher`** — Proof Pack envelope per service.
- **`upsell_engine`** — 3 verdicts (upsell_now / iterate_first / gentle_upsell).
- **`whatsapp_renderer`** — ≤3 buttons، Arabic body.
- **`operator_memory`** — sessions + facts + preferences + audit.
- **`service_bundles`** — 6 bundles (Growth Starter, Data to Revenue, Executive Growth OS, Partnership Growth, Local Growth OS, Full Growth Control Tower).
- **`executive_mode`** — CEO command center.
- **`client_mode`** — Growth Manager dashboard.
- **`agency_mode`** — multi-client + co-branded Proof Pack + revenue share.

---

## 4. Revenue Company OS

**10 module + 19 endpoint.** الذكاء عبر القنوات:

- **`event_to_card`** — 13 event types → Arabic decision cards (≤3 buttons).
- **`command_feed_engine`** — daily aggregation + sort by risk.
- **`action_graph`** — 14 typed edges signal → action → outcome → proof.
- **`revenue_work_units`** — 19 RWU types (Salesforce-inspired) + aggregation.
- **`channel_health`** — cross-channel reputation snapshot.
- **`opportunity_factory`** — turn signals into opportunity cards.
- **`service_factory`** — instantiate any service for a customer.
- **`proof_ledger`** — Revenue Proof scoreboard per customer.
- **`growth_memory`** — cross-customer aggregates (anonymized): best message/channel/objections.
- **`self_improvement_loop`** — weekly Arabic recommendations from real metrics.

---

## 5. Service Bundles (6 customer-facing offerings)

| Bundle | Best for | Price (SAR) |
|--------|----------|-------------|
| Growth Starter | أي شركة تجرب لأول مرة | 499–1,500 |
| Data to Revenue | شركات لديها قائمة | 1,500–3,000 |
| Executive Growth OS | CEO / Growth Manager شهرياً | 2,999 |
| Partnership Growth | شركات تنمو عبر الشركاء | 3,000–7,500 |
| Local Growth OS | عيادات/متاجر/فروع | 999–2,999 |
| Full Growth Control Tower | مؤسسات 30+ يوم | 12,000–25,000 |

---

## 6. الأمان (Critical Gates)

كل tool action يمر:
```
Intent → Policy → Approval → Execution → Audit
```

أوضاع التنفيذ:
- `suggest_only`
- `draft_only`
- `approval_required`
- `approved_execute` (env flag مفعّل + اعتماد)
- `blocked`

**الممنوع تماماً (حتى مع env flag):**
- LinkedIn scraping / auto-DM / auto-connect.
- cold WhatsApp بدون opt-in.
- Moyasar live charge من API.
- إرسال Gmail بدون اعتماد بشري.

---

## 7. Endpoints الجديدة

### Autonomous Service Operator (28)
```
POST /api/v1/operator/chat/{message, decision, classify}
POST /api/v1/operator/sessions/{new, {id}/transition, {id}/context}
GET  /api/v1/operator/sessions/{id}
POST /api/v1/operator/cards/{approval, whatsapp/render}
GET  /api/v1/operator/intake/questions/{intent}
POST /api/v1/operator/intake/validate
POST /api/v1/operator/service/start
POST /api/v1/operator/tools/plan
POST /api/v1/operator/proof-pack/dispatch
POST /api/v1/operator/upsell/{recommend, card}
GET  /api/v1/operator/bundles
POST /api/v1/operator/bundles/recommend
POST /api/v1/operator/mode/{ceo, ceo/daily-brief, ceo/risks, client, agency, agency/add-client, agency/revenue-share, agency/co-branded-proof}
GET  /api/v1/operator/whatsapp/daily-brief/demo
GET  /api/v1/operator/proof-pack/demo
```

### Revenue Company OS (19)
```
GET  /api/v1/revenue-os/command-feed/demo
POST /api/v1/revenue-os/{events/ingest, command-feed/build}
GET  /api/v1/revenue-os/work-units/{types, demo}
POST /api/v1/revenue-os/work-units/{build, aggregate}
GET  /api/v1/revenue-os/proof-ledger/demo
GET  /api/v1/revenue-os/action-graph/{edge-types, demo}
POST /api/v1/revenue-os/channel-health/snapshot
GET  /api/v1/revenue-os/channel-health/demo
POST /api/v1/revenue-os/opportunity-factory
GET  /api/v1/revenue-os/opportunity-factory/demo
POST /api/v1/revenue-os/service-factory
GET  /api/v1/revenue-os/service-factory/demo
GET  /api/v1/revenue-os/growth-memory/demo
POST /api/v1/revenue-os/self-improvement/weekly-report
GET  /api/v1/revenue-os/self-improvement/demo
```

---

## 8. اختبارات

`tests/unit/test_autonomous_service_operator.py` — 50 tests.
`tests/unit/test_revenue_company_os.py` — 31 tests.

تغطية:
- Intent classification (8 intents).
- Bundle recommendation per persona.
- Tool planner blocks LinkedIn scrape/auto-DM.
- Approval cards ≤3 buttons.
- Sessions transition + audit.
- Modes (CEO / Client / Agency) with revenue share calc.
- Event → card with risk levels.
- Action Graph what-works.
- RWU aggregation + revenue total.
- Self-improvement recommendations.

---

## 9. الفرق الشاسع عن المنافسين

| المنافس | ماذا يملك | أين Dealix يتفوق |
|---------|-----------|-----------------|
| CRM | بيانات وفرص | يقول ماذا تفعل اليوم |
| WhatsApp tool | إرسال | يقرر هل ترسل، لمن، ولماذا، وبأي موافقة |
| Email assistant | يكتب رد | يحول الإيميل إلى pipeline + meeting + Proof |
| Agency | تنفيذ يدوي | نظام قابل للتكرار + Proof Pack |
| Generic AI agent | ينفذ prompts | عنده خدمات + سياسات + Proof + موافقات + تحسين ذاتي |
| HubSpot/Gong/Salesforce | منصات قوية | سعودي/عربي/SMB/Service-first/WhatsApp-aware |

---

## 10. الخلاصة

Dealix الآن **فئة جديدة**:
- 12 طبقة معمارية متكاملة.
- 905 اختبار ناجح.
- 47 endpoint جديد في هذه الجولة.
- Approval-first في كل قناة.
- Self-improving أسبوعياً.
- Revenue Work Units قابلة للقياس.
- Proof Ledger يُثبت العائد.
- 6 bundles + Service Excellence Score يحكم كل خدمة.

**لا يبيع features. يبيع نتائج منظمة.**
