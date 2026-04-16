# Dealix Completion Program — Execution Matrix النهائية (Enterprise-Grade)

**الحالة:** نسخة تشغيلية معتمدة للتنفيذ  
**النسخة:** v1.0  
**النطاق:** تحويل Dealix من وثائق مرجعية قوية إلى قدرات تشغيلية مثبتة في الإنتاج

---

## 1) الهدف التنفيذي

هذه الوثيقة تحوّل برنامج الإغلاق (Completion Program) إلى مصفوفة تنفيذ عملية بصيغة:

`Workstream -> Deliverables -> Owner -> Evidence Gate -> Exit Criteria -> Dependencies -> Risk -> SLA`

النتيجة المطلوبة: منصة قابلة للتدقيق والتشغيل المؤسسي عبر **Decision Fabric + Execution Fabric + Trust Fabric + Data Fabric + Enterprise Delivery Fabric**.

---

## 2) تعريف حالات التنفيذ (Status Taxonomy)

| الحالة | التعريف التشغيلي |
|---|---|
| `Current` | موجود كوثائق/تصميم أو كود أولي غير محكوم بالبوابات |
| `Partial` | جزء من المسار مطبق، لكن دون تغطية كاملة أو دون evidence gate |
| `Pilot` | مطبق على مسار/عميل/بيئة محددة مع قياس واضح |
| `Production` | مطبق كسياسة افتراضية في الإنتاج مع telemetry + audit + release gates |

---

## 3) Master Execution Matrix

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|---|---|---|---|---|---|---|
| WS1 — Productization & Architecture Closure | 1) `current-vs-target architecture register` 2) تصنيف كل subsystem إلى `Current/Partial/Pilot/Production` 3) تثبيت 5 planes + 6 business tracks + أدوار الوكلاء (Observer/Recommender/Executor) + action metadata القياسية | Enterprise Architect + Product Ops | نشر register في المستودع + مراجعة معتمدة من Architecture Review + تحديث ADRs المرتبطة | لا يوجد subsystem بلا حالة واضحة أو owner أو plan-of-record | وثائق الـ blueprint الحالية + ADR baseline | خطر الغموض المعماري بين الفرق | تحديث أسبوعي للـ register خلال أول 6 أسابيع، ثم نصف شهري |
| WS2 — Decision Plane Hardening | 1) schemas إلزامية لمخرجات القرار (`memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json`) 2) structured outputs mandatory للـ critical flows 3) مولد bilingual decision memo | AI Platform Lead + Applied AI Lead | اختبارات schema validation + traces تُظهر 0 free-text operational outputs في المسارات الحرجة | 100% من قرارات المسارات الحرجة typed + auditable + resumable | OpenAI Responses integration + orchestrator hooks + schema registry | خطر قرارات غير قابلة للتدقيق أو انحراف prompts | p95 زمن توليد القرار ضمن target service budget، وخطأ schema < 1% |
| WS3 — Execution Plane Hardening | 1) inventory كامل للـ workflows 2) تصنيف short/medium/long-lived 3) قاعدة ترحيل: أي workflow >15 دقيقة أو >2 systems أو يحتاج compensation يهاجر لـ Temporal 4) Pilot workflow واحد enterprise-grade | Workflow Platform Lead + Backend Lead | نجاح pilot شامل: start/resume/retry/compensation + chaos test report + runbook | workflow pilot يعمل deterministic مع idempotency/versioning policy معتمدة | WS1 + WS2 + بنية workers/queues + observability | خطر فقدان الالتزامات طويلة العمر أو تكرار التنفيذ | SLO نجاح workflows الحرجة >= 99.5% مع RTO/RPO معتمدين |
| WS4 — Trust Fabric Hardening | 1) policy inventory 2) OPA policy packs 3) OpenFGA authorization model 4) Vault integration plan 5) Keycloak SSO/service identity 6) tool verification ledger v1 + contradiction dashboard | Security Architect + IAM Lead | قرارات policy/auth موثقة ومقاسة + audit logs + اختبارات رفض/سماح + ledger artifacts | كل action حساس يمر عبر policy decision + authorization graph + verification ledger | WS1 + WS2 + WS3 + IAM/Security infra | خطر excessive agency أو صلاحيات غير مضبوطة | قرارات policy/auth p95 < 120ms، ونسبة audit coverage = 100% للأفعال الحساسة |
| WS5 — Data & Connector Fabric | 1) standard موحد لـ connector facades 2) versioning لكل connector 3) retry/timeout/idempotency policy 4) event envelope (CloudEvents-style) 5) schema discipline + quality checks | Data Platform Lead + Integrations Lead | اختبارات contract لكل connector + dashboards للـ data quality + lineage updates | لا توجد tool calls مباشرة للبائعين في المسارات الحرجة دون facade/versioning | WS2 + WS3 + WS4 + data governance | خطر انهيار صامت بسبب vendor API drift | التزام SLA للتكاملات الحرجة (availability + latency + retry success) موثق ومراقب |
| WS6 — Enterprise Delivery Fabric | 1) GitHub rulesets 2) CODEOWNERS 3) required checks 4) release branches protections 5) environments (dev/staging/canary/prod) 6) OIDC federation 7) artifact attestations 8) audit log streaming خارجي | DevSecOps Lead + Release Manager | سياسات الحماية مفعلة فعلياً + إثبات deployment approvals + سجلات تدقيق مُصدّرة | لا يتم release للبيئات الحساسة دون gates والتوقيع provenance | WS1 + WS4 + البنية السحابية | خطر إصدارات غير محكومة أو غير قابلة للتتبع | MTTR / change failure rate ضمن أهداف SRE المعتمدة |
| WS7 — Saudi Enterprise Readiness | 1) PDPL data classification matrix 2) processing register 3) residency/transfer flags في policy layer 4) NCA ECC readiness gaps register 5) mapping مع NIST AI RMF + OWASP LLM Top 10 | GRC Lead + Privacy Officer + Security Lead | أدلة ضوابط الامتثال + اختبارات policy flags + review قانوني/تقني دوري | كل workflow حساس سعودي لديه control mapping قابل للتدقيق | WS4 + WS5 + WS6 + legal/compliance operations | خطر عدم الجاهزية التعاقدية مع الجهات الحساسة | SLA مراجعة امتثال ربع سنوية + pre-release compliance gate إلزامي |
| WS8 — Executive & Customer Readiness | 1) executive room حي 2) board-ready memo view 3) evidence pack view 4) approval center 5) policy violations board 6) partner scorecards 7) actual vs forecast + risk heatmaps | Product Lead + Analytics Lead + CX Lead | demo تشغيلي موثق + stakeholder sign-off + adoption metrics baseline | الإدارة ترى لوحات تشغيلية مرتبطة بقرارات وأفعال قابلة للتدقيق | WS2 + WS3 + WS4 + WS5 + WS6 | خطر فصل الإدارة عن الواقع التشغيلي | تحديث لوحات الإدارة أسبوعيًا + SLA دقة بيانات تقارير الإدارة |

---

## 4) Weekly Delivery Matrix (12-Week Execution)

| Week | Workstream Focus | Deliverables (هذا الأسبوع) | Evidence Gate (هذا الأسبوع) | Exit Criteria |
|---|---|---|---|---|
| W1 | WS1 | نشر architecture register v1 + baseline statuses + owner map | PR معتمد + review minutes | baseline معتمد لكل subsystem |
| W2 | WS1 + WS2 | تثبيت action metadata القياسية + schemas v1 للقرارات الحرجة | schema tests pass + ADR update | مسار قرار حرج واحد typed بالكامل |
| W3 | WS2 | structured outputs mandatory في 2 مسارات حرجة + memo compiler v1 | trace sampling + lint rule/guardrail | 0 free-text operational output في المسارات المغطاة |
| W4 | WS3 | inventory workflows + تصنيف short/medium/long + migration backlog | workflow register + triage sign-off | قائمة migration معتمدة بالأولوية |
| W5 | WS3 | بناء Temporal pilot (partner approval أو DD room) + idempotency policy | pilot E2E run + retry/resume evidence | نجاح pilot في staging |
| W6 | WS3 + WS4 | compensation policy + policy inventory + OPA/OpenFGA model draft | failure injection report + policy test report | pilot resilient + trust model draft معتمد |
| W7 | WS4 | tool verification ledger v1 + contradiction detector + Vault/Keycloak integration plan | ledger events + contradiction dashboard screenshot | 100% من أدوات pilot تصدر verification artifacts |
| W8 | WS5 | connector facade standard + versioning rule + retry/timeout templates | contract tests + connector scorecard | 2 connectors حرجة خلف facade versioned |
| W9 | WS5 + WS6 | event envelope standard + schema governance + rulesets/CODEOWNERS/environments | policy-as-code checks + protected branch proof | release gate baseline مفعّل |
| W10 | WS6 + WS7 | OIDC + attestations + audit streaming + PDPL/NCA matrices v1 | provenance evidence + compliance review note | لا release حرج بدون attestation/compliance gate |
| W11 | WS7 + WS8 | NIST/OWASP mapping + executive room v1 + approval center v1 | executive demo + governance walkthrough | قبول تنفيذي أولي وتشغيل لوحة المخاطر |
| W12 | WS8 + Cross-cutting | readiness review النهائي + go/no-go package + Q+1 backlog | enterprise readiness report + sign-off | انتقال رسمي من `Pilot` إلى `Production` للمسارات المؤهلة |

---

## 5) Owner Model (Roles)

| Role | المسؤولية الأساسية |
|---|---|
| Enterprise Architect | اتساق البنية، إغلاق فجوة current-target، ADR governance |
| AI Platform Lead | decision schemas، structured outputs، جودة القرار |
| Workflow Platform Lead | ترحيل workflows طويلة العمر، resilience، deterministic execution |
| Security/IAM Lead | OPA/OpenFGA/Vault/Keycloak، ضبط الثقة والتفويض |
| Data/Integrations Lead | connector facades، event/data contracts، جودة البيانات |
| DevSecOps/Release Manager | SDLC governance، release protections، attestations |
| GRC/Privacy Lead | PDPL/NCA/NIST/OWASP mapping وتشغيل الضوابط |
| Product/Analytics Lead | executive artifacts، adoption metrics، customer readiness |

---

## 6) Evidence Gate Checklist (الحد الأدنى الإلزامي)

لا يُعتبر أي deliverable مكتملًا بدون:

1. Artifact قابل للمراجعة (مستند/تقرير/Dashboard/Trace/Log).  
2. Owner sign-off + reviewer مستقل (two-person integrity).  
3. قياس قبل/بعد أو baseline واضح.  
4. ربط مباشر بمخاطر مسجلة في `risk register`.  
5. تحديث الحالة في register (`Current/Partial/Pilot/Production`).

---

## 7) Definition of Done — Enterprise Readiness Exit

الخروج النهائي من البرنامج يتحقق فقط عند اكتمال البنود التالية:

- كل توصية business-critical تخرج structured وevidence-backed.
- كل التزام long-running يمر عبر deterministic durable workflow.
- كل action حساس يحمل metadata: Approval + Reversibility + Sensitivity + Provenance + Freshness.
- كل connector حرج versioned وله retry/idempotency/audit mapping.
- كل release حرج يمر عبر rulesets + approvals + OIDC + provenance attestation.
- كل surface حرج مغطى بـ telemetry مع trace/correlation IDs.
- كل workflow سعودي حساس موصول بمصفوفة PDPL/NCA controls قابلة للتدقيق.

---

## 8) Governance Cadence

- **تشغيلي أسبوعي:** تحديث matrix progress + blockers + risk heatmap.
- **تنفيذي نصف شهري:** قرار أولويات (re-sequencing) بناءً على evidence.
- **حوكمة شهرية:** مراجعة سياسات الثقة والامتثال والإصدارات.
- **ربع سنوي:** إعادة تقييم exit criteria ورفع معيار الجودة المؤسسية.

---

**ملاحظة تشغيلية:** هذه الوثيقة مرجع تنفيذي حي؛ أي تعديل في الأولويات يجب أن يُوثق كتغيير في matrix وليس كملاحظة خارجية.
