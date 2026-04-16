# Execution Matrix السيادية — 6 أشهر (Dealix Sovereign Growth, Execution, and Governance OS)

**الإصدار:** v1.0
**الحالة:** Sovereign Transformation Baseline (180 يوم)
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الهدف التنفيذي

تحويل Dealix من مرجعية Tier-1 قوية إلى منصة سيادية تشغيلية عبر 5 planes:

1. Decision Plane
2. Execution Plane
3. Trust Plane
4. Data Plane
5. Operating Plane

مع القاعدة المعمارية الإلزامية:

> AI recommends. Workflows commit. Humans approve critical decisions. Evidence verifies everything.

---

## 2) النوافذ الزمنية (180 يوم)

| المرحلة | النافذة | الغرض |
|---|---|---|
| Phase A | Day 0-30 | تثبيت Control/Operating baseline |
| Phase B | Day 31-90 | إغلاق فجوة docs ↔ runtime |
| Phase C | Day 91-180 | durable execution + trust hardening + executive surface |

---

## 3) Sovereign 6-Month Matrix (Workstream -> Deliverables -> Owner profile -> Evidence Gate -> Exit Criteria -> Dependencies -> SLA -> KPI -> Anti-patterns -> Rollback)

| Workstream | Deliverables (6 months) | Owner profile | Evidence Gate | Exit Criteria | Dependencies | SLA | KPI | Anti-patterns (ممنوع) | Rollback |
|---|---|---|---|---|---|---|---|---|---|
| WS1 — Architecture Closure & Sovereign Control | (1) Current-vs-Target register لكل subsystem. (2) قفل رسمي للـ5 planes و6 tracks و3 agent roles. (3) classes: approval/reversibility/sensitivity. (4) trace/correlation/causation standards. | Enterprise Architect + Program Director | EG-WS1-ARCH-BASELINE: register مكتمل + approved control taxonomy | 100% subsystems بحالة رسمية وowner وgap due-date | blueprint/ADRs/owner directory | تحديث أسبوعي إلزامي، إغلاق high-risk architecture gaps <= 10 أيام عمل | %Subsystems with valid status + owner (target: 100%) | تعدد تعريفات الحالة، أو إضافة subsystem بلا owner | Freeze promotion إلى Pilot لأي subsystem غير مصنف حتى الإغلاق |
| WS2 — Decision Plane Hardening | (1) mandatory structured outputs: memo/evidence/risk/approval/execution_intent. (2) schema registry versioned. (3) bilingual memo compiler. (4) provenance/freshness/confidence scoring. | AI Platform Lead (schema-first, Arabic-capable) | EG-WS2-SCHEMA-MANDATORY: schema contracts + free-text rejection proofs | 0 critical free-text outputs + >=95% schema pass rate | model routing policy + orchestration contracts | schema-breaking fix <= 24h | Schema adherence rate, contradiction rate, Arabic memo quality score | نص حر تشغيلي في تدفقات حرجة، أو score غير موثق المصدر | Revert to previous schema version + disable affected critical flow until pass |
| WS3 — Execution Durability (Temporal target lane) | (1) workflow inventory + migration policy (>15m, >2 systems, compensation, pause/resume, external commitment). (2) first durable pilot flow. (3) idempotency + compensation library. (4) workflow versioning strategy. | Workflow Engineering Lead (durable runtime) | EG-WS3-DURABLE-PILOT: replay/restart/compensation evidence | أول business-critical flow deterministic + resumable + compensatable | queue/runtime infra + connector contracts | critical workflow recovery <= 15m | %Eligible workflows migrated to durable lane, compensation success rate | external commitment عبر agent مباشر، أو queued flow بدون idempotency | Trigger safe compensation + freeze new durable migrations until RCA close |
| WS4 — Trust Fabric Hardening | (1) OPA policy packs baseline. (2) OpenFGA model draft + model pinning policy. (3) Vault target integration path. (4) Keycloak SSO/service identity path. (5) tool verification ledger + contradiction dashboard. | Security Architecture Lead + IAM Lead | EG-WS4-TRUST-PATH: policy/authz logs + contradiction controls | كل action حساس يمر عبر policy + auth + approval + verification | identity provider + secret management + policy repo | policy enforcement on critical paths = 100% | Sensitive-action coverage, unresolved critical contradictions = 0 | policy logic داخل prompts، أو bypass عبر service-local if/else | Force No New Autonomy + route actions to manual approval-only mode |
| WS5 — Data & Connector Fabric | (1) connector facade standard versioned. (2) retry/timeout/idempotency rules. (3) event envelope standard. (4) semantic metrics dictionary (single source). (5) quality checks + lineage discipline. | Data Platform Lead + Integrations Lead | EG-WS5-CONNECTOR-SSOT: facade contracts + quality scorecards | 100% critical connectors عبر facade versioned + quality gate >=98% | ingestion pipelines + schema governance + metrics owners | connector API drift patch <= 72h | Connector compliance %, quality pass %, metric definition drift (target: 0) | raw vendor tool calls، أو metric definitions متعددة لنفس المفهوم | Downgrade to stable connector version + disable unstable integration path |
| WS6 — Enterprise Delivery Fabric | (1) rulesets/CODEOWNERS/required checks/protected branches. (2) environment promotion gates. (3) OIDC path. (4) provenance/attestation readiness. (5) external audit streaming path. | DevSecOps Lead + Release Steward | EG-WS6-GOV-RELEASE: governance checks + deployment gate evidence | لا يوجد production merge/deploy خارج governance gates | CI/CD governance + cloud IAM | rollback initiation <= 10m | Gate pass rate, unauthorized deploy count (target: 0), rollback MTTR | direct push/release bypass، أو merge بلا required checks | Auto-block merge queue + revert to last attested build |
| WS7 — Saudi Enterprise Readiness | (1) PDPL data classification matrix. (2) processing register. (3) residency/transfer controls. (4) NCA ECC readiness matrix. (5) NIST AI RMF + OWASP LLM controls mapping. | Compliance Lead (KSA) + Security Governance | EG-WS7-SAUDI-CONTROLS: control-evidence mapping per sensitive workflow | 100% Saudi-sensitive workflows mapped to controls/evidence/owner | legal/DPO input + policy engine hooks | close high-risk compliance gaps <= 10 business days | %Sensitive workflows with valid control mapping, overdue compliance gaps | تشغيل flow حساس بلا mapping، أو evidence منتهي الصلاحية | Block affected workflow class and move to manual compliance hold |
| WS8 — Executive & Customer Readiness | (1) executive room live. (2) board-ready memos/evidence view/approval center. (3) policy violations board. (4) scorecards + actual vs forecast + risk heatmaps + next-best-action. | Product Director + RevOps/BI Lead | EG-WS8-EXEC-SURFACE: live demo + stakeholder sign-off + data freshness proof | قيادة الشركة ترى قرار/قيمة/مخاطر/اعتماد/أثر تشغيلي من سطح واحد | semantic metrics + trust telemetry + decision outputs | critical dashboard refresh <= 15m | Executive adoption, decision cycle time reduction, forecast variance | لوحات تجميلية بلا lineage، أو KPI متضارب مع SSOT | Revert to previous certified dashboard dataset and freeze KPI changes |

---

## 4) مؤشرات البرنامج السيادي (Program KPIs)

| KPI | Day 30 | Day 90 | Day 180 |
|---|---:|---:|---:|
| Structured decision coverage (critical flows) | 60% | 90% | 100% |
| Durable commitment coverage (eligible workflows) | 15% | 45% | 80% |
| Sensitive action trust coverage | 50% | 85% | 100% |
| Connector facade compliance (critical set) | 40% | 75% | 100% |
| Governance-gated release compliance | 80% | 95% | 100% |
| Saudi-sensitive workflow control mapping | 50% | 85% | 100% |

---

## 5) Anti-Pattern Kill List (قاعدة المنع)

1. Agent يقوم external commitment مباشرة خارج workflow runtime.
2. Critical output بلا schema contract.
3. Sensitive action بلا approval class/reversibility/sensitivity.
4. Connector بلا version + retry + idempotency + audit mapping.
5. Release بلا gate/provenance evidence.
6. KPI من مصدر غير معرّف داخل semantic metrics SSOT.

---

## 6) آلية التحكم الأسبوعية (Steering Logic)

- الأحد: weekly planning على المصفوفة (target/gates/dependencies).
- الثلاثاء: mid-week evidence/risk/SLA checkpoint.
- الخميس: exit decision per workstream (Pass/Conditional/Fail).
- أي Fail مرتين متتاليتين = executive escalation خلال 48 ساعة.

---

## 7) الربط التشغيلي

- Baseline Matrix: `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- Weekly OS: `docs/EXECUTION_MATRIX_WEEKLY_OPERATING_SYSTEM_AR.md`
- Governance/RACI: `docs/COMPLETION_PROGRAM_GOVERNANCE_RACI_AR.md`
- Evidence Gates: `docs/COMPLETION_PROGRAM_EVIDENCE_GATE_CATALOG_AR.md`
- Risk Register: `docs/COMPLETION_PROGRAM_RISK_REGISTER_AR.md`
- SLA Policy: `docs/COMPLETION_PROGRAM_SLA_ESCALATION_POLICY_AR.md`
- Execution Pack: `docs/COMPLETION_PROGRAM_EXECUTION_PACK_TEMPLATE_AR.md`

