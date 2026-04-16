# Execution Matrix السيادية — برنامج 6 أشهر (Dealix Sovereign OS)

**الإصدار:** v1.0  
**الحالة:** Sovereign Execution Baseline (0–180 days)  
**المرجع:** `frontend/public/strategy/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الهدف التنفيذي

تحويل Dealix من مرجعية Tier-1 قوية إلى **Sovereign Growth, Execution, and Governance OS** قابل للتشغيل المؤسسي في السعودية والخليج، عبر:

1. Decision Plane
2. Execution Plane
3. Trust Plane
4. Data Plane
5. Operating Plane

---

## 2) نطاق البرنامج الزمني (6 أشهر)

| المرحلة | الأفق | مخرجات إجبارية |
|---|---|---|
| Phase A | 0–30 يوم | قفل الحوكمة والسياسات والتصنيف والـ model routing v1 |
| Phase B | 30–90 يوم | تحويل القرارات إلى structured evidence-backed execution |
| Phase C | 90–180 يوم | durable execution + trust controls + executive operating surface |

---

## 3) الأعمدة التشغيلية الإلزامية

صيغة التنفيذ المعتمدة لكل Workstream:

`Workstream -> Deliverables -> Owner profile -> Evidence Gate -> Exit Criteria -> Dependencies -> SLA -> KPI -> Anti-patterns -> Rollback`

---

## 4) Sovereign 6-Month Execution Matrix

| Workstream | Deliverables (0–180d) | Owner profile | Evidence Gate | Exit Criteria | Dependencies | SLA | KPI | Anti-patterns (ممنوع) | Rollback |
|---|---|---|---|---|---|---|---|---|---|
| WS1 — Architecture Closure Program | A) current-vs-target register لكل subsystem. B) قفل رسمي: 5 planes + 6 tracks + role classes + metadata classes. C) تحديث ADRs وربطها بالواقع التشغيلي. | Enterprise Architect + Platform PMO Lead | EG-WS1-ARCH-01 + EG-WS1-LOCK-02 + ADR diff review | 100% subsystem status coverage (Current/Partial/Pilot/Production) بدون تعارضات مفتوحة | Master blueprint, ADR ownership, system inventory | تحديث register أسبوعي؛ إغلاق أي conflict خلال <=5 أيام عمل | % تغطية الأنظمة؛ % تضارب التعريفات المغلقة؛ زمن إغلاق gap | تعدد مصادر الحقيقة، أو Claims بلا mapping | الرجوع لآخر register معتمد وإيقاف ترقية الحالة لحين إعادة التدقيق |
| WS2 — Decision Plane Hardening | A) Structured outputs mandatory (`memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json`). B) decision memo compiler ثنائي اللغة. C) provenance/freshness/confidence scoring v1. | AI Platform Lead + Decision Intelligence Lead | EG-WS2-SCHEMA-01 + EG-WS2-FREETEXT-02 + sampled decision audits | 0 critical free-text outputs + schema pass rate >=95% + decision packets traceable end-to-end | LLM orchestration contracts, schema registry, model routing policy | schema-breaking fix <=24h؛ audit exceptions مغلقة <=72h | schema pass rate؛ contradiction rate؛ decision-to-approval lead time | JSON شكلي غير typed، أو Evidence غير مربوط بالقرار | freeze على القرار المتأثر، downgrade إلى آخر schema version مستقرة |
| WS3 — Execution Plane Hardening | A) workflow inventory وتصنيفها (short/medium/long-lived). B) ترحيل flows الحرجة إلى durable lane (Temporal target). C) idempotency + compensation + pause/resume strategy. | Workflow Engineering Lead + Runtime Reliability Lead | EG-WS3-WFINV-01 + EG-WS3-DURABLE-02 + recovery runbook test | أول 2 workflows حرجة تعمل deterministic + replay/restart مثبتين + no lost commitments | Queue/runtime infra, service boundaries, connector readiness | TTD<=1h للحوادث الحرجة؛ recovery <=15m للمسارات المصنفة حرجة | % flows المصنفة؛ % flows migrated; recovery success rate | commitment خارجي عبر جلسة agent مباشرة، أو workflow بلا compensation | route-to-safe-mode، تعليق commitments الجديدة، replay من آخر checkpoint |
| WS4 — Trust Fabric Hardening | A) policy inventory + OPA packs. B) authorization model draft (OpenFGA style). C) tool verification ledger + contradiction dashboard. D) vault/keycloak integration path. | Security Architecture Lead + IAM/Authorization Lead | EG-WS4-POLICY-01 + EG-WS4-VERIFY-02 + access review pack | 100% sensitive paths خلف policy/authz hooks + unresolved critical contradictions = 0 | Identity provider, secret management path, policy repo | P1 trust gaps: detect<=15m/respond<=30m/resolve<=4h | policy coverage %؛ authz denial correctness؛ unresolved contradictions | policy logic داخل prompts، bypass محلي في الخدمة، أو shared secrets | تفعيل No New Autonomy Rule + rollback policy bundle + revoke credentials |
| WS5 — Data & Connector Fabric | A) connector facade standard versioned. B) retry/timeout/idempotency/audit mapping. C) semantic metrics dictionary موحد. D) quality gates + lineage snapshots. | Data Platform Lead + Integrations Lead | EG-WS5-CONN-01 + EG-WS5-DQ-02 + semantic metric certification | 100% critical connectors وراء facade + quality gate >=98% + metric definitions موحدة | Postgres/pgvector model, ingestion/connectors, data contracts | API drift patch <=72h؛ quality incident triage <=24h | connector compliance %؛ data quality score؛ metric dispute count | tool-to-vendor direct calls، metrics متعددة التعريف، أو hidden transformations | switch connector to previous stable wrapper + disable unsafe sync jobs |
| WS6 — Enterprise Delivery Fabric | A) rulesets/CODEOWNERS/required checks/protected branches. B) env promotion discipline dev->staging->canary->prod. C) OIDC + artifact provenance + external audit streaming. | DevSecOps Lead + Release Steward | EG-WS6-REL-01 + EG-WS6-PROV-02 + deployment gate report | لا يوجد merge/release production خارج الحوكمة + provenance 100% لإصدارات prod | CI/CD platform, cloud IAM, security scanners | rollback initiation <=10m؛ release gate reliability >=99.9% | % guarded merges؛ % provenanced deploys؛ failed gate escapes=0 | direct push، manual prod drift، أو bypass checks | auto-revert release + environment freeze + mandatory postmortem |
| WS7 — Saudi Enterprise Readiness | A) PDPL control matrix + processing register. B) NCA ECC readiness matrix. C) NIST AI RMF + OWASP LLM controls mapping لكل release. D) residency/transfer controls داخل policy engine. | Compliance Lead (KSA) + Cyber Governance Lead | EG-WS7-PDPL-01 + EG-WS7-NCA-02 + compliance evidence pack | كل workflow سعودي حساس لديه mapping واضح (control->evidence->owner->expiry) بدون high-risk open gap | Legal counsel, DPO, policy hooks, data classification | high-risk compliance gaps <=10 أيام عمل | compliance control coverage %؛ overdue controls count؛ exception aging | compliance docs بلا تنفيذ policy، أو sensitive flow بلا residency flag | suspend affected flow + exception register + executive risk acceptance only |
| WS8 — Executive & Customer Readiness | A) Executive Room حي (memo/evidence/approval/risk/forecast). B) policy violations board + partner scorecards. C) next-best-action + actual-vs-forecast loop. | Product Director + RevOps Lead + BI Lead | EG-WS8-EXEC-01 + EG-WS8-KPI-02 + executive sign-off record | board-ready operating surface live مع adoption ثابت وقرارات قابلة للتدقيق | semantic metrics layer, trust telemetry, decision outputs | KPI refresh <=15m للحرج؛ dashboard uptime >=99.5% | adoption rate؛ decision cycle time؛ forecast error delta | dashboards للعرض فقط بلا traceability، أو KPI بلا source-of-truth | rollback إلى baseline executive views + disable non-verified widgets |

---

## 5) موجة التنفيذ الشهرية (6 أشهر)

| الشهر | التركيز | شرط المرور |
|---|---|---|
| M1 | Governance/Architecture/Policy classes lock | لا تضارب معماري مفتوح عالي الخطورة |
| M2 | Structured decision outputs + evidence compiler | لا critical free-text، Schema pass >=95% |
| M3 | Connector discipline + semantic metric standard | كل connector حرج تحت facade versioned |
| M4 | Durable workflow pilot + trust hooks | deterministic recovery مثبت + policy coverage كامل للمسارات الحرجة |
| M5 | Enterprise release controls + Saudi controls operationalization | production gate governance مكتملة + compliance gaps high=0 |
| M6 | Executive operating surface + program exit audit | readiness sign-off (Program + Compliance + Release + Executive) |

---

## 6) Definition of Done (Sovereign 6-Month Exit)

- كل قرار business-critical structured + typed + evidence-backed.
- كل commitment طويل العمر durable + resumable + compensatable.
- كل action حساس policy/auth/approval guarded.
- كل connector versioned وله retry/idempotency/audit mapping.
- كل release production له rulesets + OIDC + attestations + protected environments.
- كل surface حرج traceable عبر trace/correlation IDs.
- كل workflow سعودي حساس mapped إلى PDPL/NCA controls مع evidence live.

---

## 7) الربط التشغيلي

- Matrix baseline: `frontend/public/strategy/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- Weekly OS: `frontend/public/strategy/EXECUTION_MATRIX_WEEKLY_OPERATING_SYSTEM_AR.md`
- Governance & RACI: `frontend/public/strategy/COMPLETION_PROGRAM_GOVERNANCE_RACI_AR.md`
- Evidence Gate Catalog: `frontend/public/strategy/COMPLETION_PROGRAM_EVIDENCE_GATE_CATALOG_AR.md`
- Risk Register: `frontend/public/strategy/COMPLETION_PROGRAM_RISK_REGISTER_AR.md`
- SLA Policy: `frontend/public/strategy/COMPLETION_PROGRAM_SLA_ESCALATION_POLICY_AR.md`
- Execution Pack Template: `frontend/public/strategy/COMPLETION_PROGRAM_EXECUTION_PACK_TEMPLATE_AR.md`
