# Execution Matrix النهائية — Completion Program (Dealix Enterprise Readiness)

**الإصدار:** v1.0
**الحالة:** Final Execution Baseline
**المرجع:** `MASTER-BLUEPRINT.mdc` + `docs/ULTIMATE_EXECUTION_MASTER_AR.md`

---

## 1) هدف البرنامج

تحويل Dealix من حالة **وثائق قوية + رؤية Tier-1** إلى تشغيل إنتاجي مؤسسي عبر 5 طبقات تشغيلية مترابطة:

1. Decision Fabric
2. Execution Fabric
3. Trust Fabric
4. Data & Connector Fabric
5. Enterprise Delivery Fabric

---

## 2) قواعد الحوكمة الإلزامية (Program Locks)

- **Plane Lock:** Decision / Execution / Trust / Data / Operating يجب أن تبقى مصادر قرار وتشغيل منفصلة وواضحة.
- **Track Lock:** تثبيت المسارات الستة للأعمال (Prospecting → Qualification → Proposal → Negotiation → Closing → Post-Sale/PMI).
- **Role Lock:** كل Agent يُصنف إلى `Observer` أو `Recommender` أو `Executor` فقط.
- **Action Metadata Lock:** كل إجراء حساس يجب أن يحمل: `Approval` + `Reversibility` + `Sensitivity` + `Provenance` + `Freshness`.
- **Evidence Lock:** لا يعتمد أي إنجاز بدون Gate أدلة واضح وقابل للتدقيق.

---

## 3) تعريف الحالات الرسمية (Current / Partial / Pilot / Production)

| الحالة | التعريف التشغيلي | دليل الانتقال |
|---|---|---|
| Current | موجود في الوثائق أو PoC دون Gate إنتاجي | وجود تصميم + Gap Log |
| Partial | منفذ جزئياً في الكود دون اكتمال الحوكمة/القياس | اختبار تقني + Known Gaps |
| Pilot | يعمل على مسار حي محدود مع مراقبة فعلية | Telemetry + Incident/Runbook |
| Production | مفعّل بشكل عام مع Controls، SLO، وعمليات Release واضحة | Evidence Pack مكتمل + Sign-off |

---

## 4) Final Execution Matrix (Workstream → Deliverables → Owner → Evidence Gate → Exit Criteria → Dependencies → Risk → SLA)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|---|---|---|---|---|---|---|
| WS1 — Productization & Architecture Closure | (1) Current-vs-Target Architecture Register لكل Subsystem. (2) تثبيت الحالة الرسمية: Current/Partial/Pilot/Production. (3) Lock رسمي للـ5 Planes والـ6 Tracks والـ3 Agent Roles. (4) Runbook توحيد Action Metadata. | Chief Architect + Platform PMO | مراجعة معمارية أسبوعية + نشر سجل التغطية `architecture_register`. | 100% من subsystems موثقة بحالة رسمية + Gap Owner + تاريخ استحقاق. | `MASTER-BLUEPRINT.mdc`, ADRs, owner map. | تضارب تعريفات الفرق أو تضخم scope. | تحديث أسبوعي ثابت (كل خميس) + SLA إغلاق فجوة تصنيف 5 أيام عمل. |
| WS2 — Decision Plane Hardening | (1) اعتماد Structured Outputs إلزامي في التدفقات الحرجة. (2) توحيد schemas: `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json`. (3) Bilingual decision memo compiler. (4) Scoring: provenance/freshness/confidence. | AI Platform Lead + Applied AI Team | Contract tests لكل schema + فحص رفض Free-text في critical flows + عينة تدقيق أسبوعية. | 0% مخرجات تشغيلية غير مهيكلة في المسارات الحرجة + ≥95% schema pass rate في CI. | LLM orchestration layer, schema registry, prompt contracts. | انكسار التوافق الخلفي أو انجراف prompts. | SLA إصلاح schema-breaking خلال 24 ساعة؛ دقة Scores تتم مراجعتها أسبوعياً. |
| WS3 — Execution Plane Hardening | (1) Workflow inventory كامل وتصنيف (short/medium/long-lived). (2) Policy ترحيل: >15 دقيقة أو >2 systems أو compensation-required ⇒ durable queue. (3) Pilot Temporal لمسار اعتماد شريك أو DD Room. (4) Idempotency keys + compensation + versioning strategy. | Workflow Engineering Lead + Backend Core | إثبات replay/restart/recovery + test scenarios لفشل الشبكة + rollback simulation. | أول workflow business-critical يعمل deterministic مع recovery مثبت وrunbook تشغيلي. | task contracts, queue infra, connector readiness. | ازدواجية التنفيذ أو تعويض ناقص. | SLA تعافٍ workflow حرج ≤15 دقيقة؛ SLA lossless execution = 99.9%. |
| WS4 — Trust Fabric Hardening | (1) Policy inventory. (2) OPA policy packs. (3) OpenFGA model draft + relation tuples baseline. (4) Vault integration plan للأسرار والتدقيق. (5) Keycloak SSO/service identity plan. (6) Tool verification ledger v1 + contradiction dashboard. | Security Architecture Lead + IAM Team | Policy decision logs + authz checks + سرية secrets audit + contradiction reports. | كل إجراء حساس يمر عبر policy + authz + verification ledger قبل/بعد التنفيذ. | identity provider, secret engine, policy repo. | فشل في مركزية policy أو bypass عبر كود محلي. | SLA إنفاذ policy على endpoints الحرجة 100%؛ SLA تدوير أسرار 30 يوم كحد أقصى. |
| WS5 — Data & Connector Fabric | (1) Connector facade standard versioned. (2) Retry/timeout/idempotency policies موحدة. (3) Event envelope standard (CloudEvents-style metadata). (4) Schema discipline + semantic metrics dictionary. (5) Data quality checks على datasets الحرجة. | Data Platform Lead + Integrations Lead | Integration contract tests + ingestion audits + quality scorecards + lineage snapshot. | 100% من الموصلات الحرجة تمر عبر facade versioned مع audit mapping واضح. | Postgres/pgvector, ingestion pipelines, connector SDKs. | تغير vendor APIs أو تضارب schemas. | SLA تحديث connector API drift خلال 72 ساعة؛ SLA data quality gate pass ≥98%. |
| WS6 — Enterprise Delivery Fabric | (1) GitHub rulesets + protected release branches. (2) CODEOWNERS + required checks. (3) Environments: dev/staging/canary/prod مع approvals. (4) OIDC federation. (5) Artifact attestations. (6) External audit log streaming. | DevSecOps Lead + Release Manager | Pull request protection evidence + deployment approvals + provenance attestations + SIEM ingest health. | لا يوجد نشر production خارج بوابات approvals/provenance/rulesets. | repo governance, CI workflows, cloud IAM. | ضعف gate coverage أو غياب قابلية التدقيق طويل المدى. | SLA release gate reliability 99.9%؛ SLA rollback initiation ≤10 دقائق. |
| WS7 — Saudi Enterprise Readiness | (1) PDPL control matrix. (2) Personal data processing register. (3) Residency/transfer flags داخل policy engine. (4) NCA ECC readiness gaps register. (5) AI governance mapping (NIST AI RMF + OWASP LLM controls). | Compliance Lead (KSA) + Security Governance | امتثال موثق لكل control + evidence mapping لكل release + readiness review شهرية. | كل workflow حساس سعودي لديه mapping واضح: control → evidence → owner → expiry. | legal counsel, DPO inputs, policy engine hooks. | فجوات امتثال صامتة أو ضعف traceability. | SLA إغلاق high-risk compliance gaps خلال 10 أيام عمل. |
| WS8 — Executive & Customer Readiness | (1) Executive Room حي. (2) Board-ready memo view. (3) Evidence Pack view. (4) Approval Center. (5) Policy Violations board. (6) Partner scorecards + forecast vs actual + risk heatmaps + next-best-action dashboard. | Product Director + RevOps + BI Lead | Demo gate حي مع سيناريوهات تشغيل فعلية + adoption metrics + stakeholder sign-off. | الإدارة والشركاء يرون قرارات/مخاطر/أثر فعلي في لوحة تنفيذ واحدة قابلة للتدقيق. | semantic metrics layer, trust telemetry, decision outputs. | dashboards بلا معنى تشغيلي أو تأخر في البيانات. | SLA تحديث لوحات القرار الحرجة ≤15 دقيقة؛ SLA uptime لوحات تنفيذية 99.5%. |

---

## 5) خطة التنفيذ الأسبوعية (12 أسبوع تشغيل)

| الأسبوع | الهدف التنفيذي | بوابة الدليل المطلوبة |
|---|---|---|
| W1 | تثبيت WS1 baseline + Register كامل للحالة الحالية | Architecture Register منشور + Owner mapping مكتمل |
| W2 | قفل Decision schemas + منع free-text في المسارات الحرجة | CI schema contracts passing + exception list = صفر للحرج |
| W3 | تفعيل memo/evidence/risk/approval packets على أول مسارين | عينات decisions قابلة للتدقيق end-to-end |
| W4 | Inventory workflows + تصنيف short/medium/long-lived | Workflow classification ledger مع مالك لكل مسار |
| W5 | إطلاق Pilot durable workflow (Temporal target) | Recovery + replay evidence + runbook |
| W6 | تفعيل trust hooks (policy/authz/verification) على المسارات الحساسة | contradiction dashboard + policy decision logs |
| W7 | تطبيق connector facade القياسي لأول مجموعة تكاملات حرجة | facade contract tests + retry/idempotency evidence |
| W8 | ضبط quality + semantic metrics + event envelope discipline | quality scorecards + lineage snapshot |
| W9 | إقفال بوابات SDLC المؤسسية (rulesets/approvals/OIDC/attestations) | release gate evidence + attestation verification |
| W10 | تفعيل Saudi readiness controls في policy engine | PDPL/NCA control mapping مع evidence links |
| W11 | تجهيز Executive Room + KPIs تنفيذية موثقة | live demo + acceptance sign-off |
| W12 | Program exit review + قرار انتقال Production واسع | Exit report: gaps=0 high-risk + approved rollout plan |

---

## 6) Program Exit Criteria (Definition of Done — Enterprise Grade)

- كل توصية business-critical تخرج **structured + evidence-backed**.
- كل التزام طويل العمر يمر عبر **deterministic durable workflow**.
- كل action حساس يحمل metadata الحوكمة (`Approval`, `Reversibility`, `Sensitivity`, `Provenance`, `Freshness`).
- كل connector حرج **versioned** مع retry/idempotency/audit mapping.
- كل release يمر عبر rulesets + approvals + OIDC + provenance.
- كل surface قابل للتتبع يملك telemetry موحد وcorrelation IDs.
- كل deployment مؤسسي يمر عبر security review + red-team coverage.
- كل workflow سعودي حساس مرتبط بـ PDPL/NCA controls mapping.

---

## 7) إدارة المخاطر التصعيدية

- أي Workstream يتجاوز SLA مرتين متتاليتين يدخل **Escalation Review** خلال 48 ساعة.
- أي Gap عالي الخطورة في Trust/Compliance يوقف توسيع الأتمتة (No New Autonomy Rule) حتى الإغلاق.
- أي Vendor API break في connector حرج يُفعِّل Emergency Patch Protocol مع نافذة 72 ساعة كحد أقصى.

---

## 8) مخرجات المتابعة الأسبوعية (Execution Pack)

يصدر أسبوعياً Pack موحد يحتوي:

1. Progress by Workstream (Current/Partial/Pilot/Production).
2. Evidence Gates achieved / failed.
3. SLA breaches + root causes + corrective actions.
4. Risks heatmap (technical/compliance/delivery).
5. Next-week commitments with named owners.

> هذه الوثيقة هي خط الأساس التنفيذي الرسمي لبرنامج الإغلاق (Completion Program) وتُحدَّث أسبوعياً بآلية evidence-first.

---

## 9) التشغيل الأسبوعي الجاهز (Operating System)

- Playbook التنفيذي الأسبوعي: `frontend/public/strategy/EXECUTION_MATRIX_WEEKLY_OPERATING_SYSTEM_AR.md`
- قالب المتابعة الجاهز (CSV): `frontend/public/strategy/execution_matrix_tracker_template.csv`
- قاعدة التنفيذ: لا يُعتمد أي تقدم بدون Evidence Gate موثق، وSLA محسوب، وRisk owner واضح.
