# Dealix Sovereign Growth OS — Master Execution Blueprint

**الإصدار:** v1.0 (صياغة مؤسسية قابلة للتنفيذ)  
**الحالة:** وثيقة تشغيل مرجعية (Architecture + Governance + Delivery)  
**النطاق:** المنتج، المنصة، التشغيل الهندسي، القرار التنفيذي

---

## 1) التعريف الرسمي للشكل النهائي

**Dealix** في شكله النهائي ليس CRM ذكيًا، بل:

> **Sovereign Growth OS**: منصة تشغيل نمو سيادية، متعددة الوكلاء، repo-native، local-aware، evidence-driven، policy-governed، Arabic-first، وproduction-safe.

### المسارات الستة المعتمدة
1. Revenue OS
2. Partnership OS
3. Corporate Development / M&A OS
4. Market Expansion OS
5. Executive PMO OS
6. Governance / Risk / Compliance OS

### السلوك التشغيلي المستهدف
- التقاط الفرص (Signals)
- التحليل والتقييم الاستراتيجي/المالي
- التصعيد للإنسان عند الحساسية (HITL)
- التنفيذ الآلي حيث يُسمح
- قياس الأثر
- التعلم وتحديث السياسات والأنماط

---

## 2) المعمارية النهائية (8 طبقات)

### A) Repo-native Engineering Layer
**المكونات:** `AGENTS.md`, `CLAUDE.md`, `.claude/settings*.json`, `hooks`, `commands`, `skills`, memory bootstrap.  
**معيار القبول:** لا يوجد prompt drift، وكل تنفيذ حساس يمر عبر hook.

### B) Orchestration Layer
**المكونات:** event bus، state store، workflow engine، retries/timeouts، interrupts/HITL، durable execution، resumability، run IDs.  
**معيار القبول:** لا يوجد agent حر خارج state machine.

### C) Provider Routing Layer
**المكونات:** provider registry، model catalog، task-to-model policies، latency/reliability metrics، fallback chains، cost guardrails، local/cloud switch.  
**معيار القبول:** لا vendor lock-in، وكل مهمة تذهب للموديل الأنسب.

### D) Local / Private Inference Layer
**المكونات:** OpenAI-compatible local endpoint، health checks، privacy-aware routing، Arabic-heavy routing، graceful degradation.  
**مبدأ التنفيذ:** اعتماد **Local Inference Adapter** بدل الارتباط المبكر باسم منتج واحد.

### E) Memory / Second Brain Layer
**المكونات:** memory domains + metadata schema + dedup + linking + archival.  
**معيار القبول:** ذاكرة منظمة قابلة للفحص وليست notes متناثرة.

### F) Tool Verification Layer
**المكونات:** intended action، claimed action، actual call، params، outputs، side effects، timestamps، verification status، contradiction flags.  
**الحالات:** verified / partially verified / unverified / contradicted.

### G) Security Gate Layer
**المكونات:** secret scan، dependency review، auth/API/webhook/upload/admin review، white-box stage، exploit-backed validation، release blocking rules.  
**معيار القبول:** لا promotion دون evidence أمني كافٍ.

### H) Executive Growth Layer
**المكونات:** Revenue/Partnership/M&A/Expansion agents + Strategic PMO + Executive intelligence + Board memo engine.

---

## 3) نموذج الوكلاء النهائي (16 وكيلًا كحد أدنى)

### Revenue Family
1. Lead Intelligence Agent
2. Outreach Orchestrator
3. Proposal & Commercial Design Agent
4. Customer Expansion Agent

### Partnerships Family
5. Partnership Scout Agent
6. Alliance Structuring Agent
7. Partner Performance Agent
8. Channel Economics Agent

### M&A / CorpDev Family
9. M&A Target Screener Agent
10. Due Diligence Analyst Agent
11. Valuation & Synergy Agent
12. Negotiation Strategy Agent
13. Post-Merger Integration Agent

### Execution / Governance Family
14. Strategic PMO Agent
15. Policy & Compliance Agent
16. Executive / Board Intelligence Agent

### Output Contract إلزامي لكل وكيل
- Objective
- Context
- Inputs used
- Assumptions
- Recommendation
- Alternatives
- Expected financial impact
- Risk register
- Confidence score
- Required approvals
- Next best action
- Rollback / exit path
- Audit metadata

---

## 4) Event Model + State Machines

### 4.1 Event taxonomy (مرجعية أولية)

**Signals**
- `signal.market_shift_detected`
- `signal.partner_interest_detected`
- `signal.customer_cluster_detected`
- `signal.competitor_move_detected`
- `signal.acquisition_candidate_detected`

**Partnerships**
- `partnership.scouted`
- `partnership.scored`
- `partnership.structure_simulated`
- `partnership.exec_review_required`
- `partnership.signed`
- `partnership.performance_below_plan`

**M&A**
- `ma.target_detected`
- `ma.screening_completed`
- `ma.dd_started`
- `ma.red_flag_critical`
- `ma.valuation_ready`
- `ma.board_decision_required`
- `ma.deal_signed`
- `ma.integration_started`
- `ma.synergy_variance_detected`

**Expansion**
- `growth.market_candidate_identified`
- `growth.entry_mode_recommended`
- `growth.playbook_generated`
- `growth.launch_authorized`
- `growth.stop_loss_triggered`

**Governance**
- `governance.policy_check_passed`
- `governance.policy_violation_detected`
- `governance.hitl_required`
- `governance.hitl_approved`
- `governance.hitl_rejected`
- `governance.audit_snapshot_created`

**Execution**
- `execution.plan_created`
- `execution.owner_assigned`
- `execution.milestone_due`
- `execution.sla_breached`
- `execution.rollback_initiated`

### 4.2 Lifecycles

**Partnership lifecycle**
`detected → enriched → scored → shortlisted → structure_drafted → business_case_ready → approval_pending → negotiation_live → signed → launched → performance_review → expanded|terminated`

**M&A lifecycle**
`detected → screened → shortlisted → intro_initiated → diligence_prep → diligence_in_progress → valuation_completed → IC_review_pending → board_review_pending → offer_submitted → signed → closed → integrated → synergy_tracking`

**Expansion lifecycle**
`candidate → scored → entry_mode_selected → economics_modeled → compliance_cleared → launch_prepared → launched → stabilization → scale|stop`

---

## 5) Decision Stack التنفيذي (إلزامي)

كل توصية استراتيجية تمر عبر 8 فلاتر:
1. Strategic fit
2. Financial attractiveness
3. Execution feasibility
4. Risk & compliance acceptability
5. Capital efficiency
6. Urgency / timing
7. Management bandwidth
8. Reversibility / rollback feasibility

**مخرجات القرار:**
- pursue / don’t pursue
- pursue now / later
- intensity level
- budget envelope
- required terms
- stop conditions

---

## 6) Financial Decision Engine

### مكونات المحرك
- Scenario engine
- Sensitivity analysis
- Forecast confidence weighting
- Payback calculator
- Capital-at-risk calculator
- Downside case engine
- Synergy tracking engine

### حالات الاستخدام
- **Revenue:** pipeline velocity, close lift, partner-sourced ARR, CAC compression
- **Partnerships:** referral vs reseller economics, margin contribution, partner payback, concentration risk
- **M&A:** valuation range, synergy-adjusted value, integration cost, time-to-synergy, impairment triggers
- **Expansion:** capex/opex, launch burn, break-even month, localization/regulatory cost

---

## 7) Governance as Policy-as-Code

### القرارات التي تتطلب اعتمادًا صريحًا
- strategic partnership
- acquisition offer
- market entry
- capital commitment
- high-risk outreach
- sensitive data transfer
- live routing policy changes
- production rollout

### Policy checks الإلزامية
- authority matrix
- spend threshold
- compliance readiness
- data sensitivity class
- legal/regional constraints
- rollback existence
- evidence completeness

**قاعدة حوكمة نهائية:** لا قرار/توقيع/تنفيذ حساس صامت.

---

## 8) الهيكل النهائي المقترح للمستودع

```text
repo/
├─ AGENTS.md
├─ CLAUDE.md
├─ .claude/
│  ├─ settings.json
│  ├─ settings.local.json
│  ├─ hooks/
│  ├─ commands/
│  └─ skills/
├─ apps/
├─ services/
├─ domain/
├─ memory/
├─ tests/
├─ docs/
└─ infra/
```

> ملاحظة: يُفعل تدريجيًا دون كسر البنية الحالية، مع ADR لكل انتقال بنيوي كبير.

---

## 9) واجهة وتجربة الاستخدام (Arabic-first Design System)

### Typography
- **IBM Plex Sans Arabic**: الخط الأساسي للمنتج/اللوحات/النماذج
- **29LT Azal**: display font للعناوين البطولية فقط

### قواعد إلزامية
- خطّان كحد أقصى
- Azal للعناوين الكبيرة والحملات فقط
- IBM Plex Sans Arabic لكل النصوص الوظيفية
- RTL-safe افتراضيًا
- اتساق ثنائي اللغة AR/EN

### واجهات الحد الأدنى النهائي
- web product
- admin console
- ops console
- executive dashboard
- approval center
- audit explorer
- security findings board
- partner room
- diligence room
- memory explorer

---

## 10) Team Topology المستهدف

1. Platform & Runtime Squad
2. Trust / Governance / Security Squad
3. Revenue Automation Squad
4. Strategic Growth Squad
5. Corporate Development Squad
6. Executive Systems / PMO Squad

**مبدأ التشغيل:** ownership واضح + SLA واضح + handoff contracts واضحة بين الفرق.

---

## 11) Delivery Discipline (GitHub/Release)

### Branch model
- `main`
- `release/*`
- `feature/*`
- `hotfix/*`

### Required checks
- lint
- type-check
- unit tests
- integration tests
- security checks
- schema validation
- migration safety
- verification tests

### PR template إلزامي
- business context
- linked initiative
- impact
- risk level
- rollback plan
- observability updates
- policy/security impact
- approval needs

### ADRs أولية مطلوبة
- runtime choice
- event versioning
- provider routing
- local-vs-cloud doctrine
- memory design
- verification ledger design
- policy engine design
- multi-tenant boundaries

---

## 12) مسار الإطلاق (Promotion Path)

1. sandbox
2. staging
3. internal canary
4. limited production
5. broad production

**شروط الانتقال الإلزامية:**
- tests pass
- security gate pass
- rollback documented
- observability ready
- cost guardrails approved
- evidence logs complete
- required approvals present

---

## 13) خارطة التنفيذ المرحلية

| المرحلة | المدة | المخرجات الرئيسية |
|---|---|---|
| 0) Doctrine | 0–2 أسبوع | operating doctrine + action classes + local/cloud + verification/release/memory doctrines |
| 1) Repo-native OS | 2–6 أسابيع | AGENTS/CLAUDE/.claude + hooks/commands/skills + conventions + memory bootstrap |
| 2) Memory + Routing + Local | 6–10 أسابيع | provider abstraction + benchmark harness + local inference adapter + second brain + scorecards |
| 3) Verification + Security | 10–14 أسبوع | verification ledger + contradiction detection + security gate v1 + pre-release attack lane |
| 4) Revenue + Partnerships core | 3–6 أشهر | lead intelligence + outreach + proposal + partnership scout/structuring/economics |
| 5) CorpDev + Expansion | 6–9 أشهر | target screener + diligence + valuation + negotiation + expansion playbooks |
| 6) Executive OS | 9–12 شهر | executive cockpit + board memos + capital allocation + PMI/synergy + stop-loss governance |

---

## 14) KPI Framework النهائي

### Revenue
- pipeline velocity
- win rate
- deal cycle compression
- margin on won deals

### Partnerships
- partner-sourced ARR
- partner payback
- scout-to-sign time
- concentration risk

### M&A
- screened→shortlisted rate
- diligence cycle time
- offer→close rate
- synergy realization %

### Expansion
- launch readiness time
- break-even month
- compliance lead time
- stop-loss trigger rate

### Execution
- on-time initiative delivery
- escalation resolution time
- critical path slippage

### Governance
- HITL coverage for sensitive decisions
- approval latency
- policy violation rate
- audit completeness score

### Learning
- forecast error by agent
- recommendation acceptance rate
- ROI on accepted recommendations
- contradiction rate in tool execution

---

## 15) معايير اكتمال النظام (Definition of Done)

يُعد الشكل النهائي متحققًا عندما يصبح النظام:
- يفهم الكودبيس والعمليات من داخله
- لا يعتمد على prompts مرتجلة
- يختار النموذج الأنسب لكل مهمة
- يحافظ على الخصوصية عبر local inference عند الحاجة
- يحتفظ بذاكرة منظمة قابلة للفحص
- يميّز claim عن evidence
- يوقف الإطلاق عند الخطر
- يدعم العربية كطبقة أصلية
- يولّد فرص نمو قابلة للتنفيذ
- يرفع جودة القرار التنفيذي
- يتعلم من النتائج الفعلية

---

## 16) أول 5 Deliverables رسمية (بدءًا من الآن)

1. Master Architecture Blueprint
2. AI Operating Constitution
3. Repo Operating Pack (`AGENTS.md`, `CLAUDE.md`, `.claude/*`)
4. Verification & Security Framework
5. 90-Day Execution Matrix

---

## 17) ملحق تنفيذي: 90-Day Execution Matrix (نسخة تشغيل أولية)

| العمل | المالك | SLA | KPI أولي |
|---|---|---|---|
| إصدار AI Operating Constitution | CTO + Head of Platform | 10 أيام | اعتماد رسمي + نشر داخلي |
| تشغيل hooks + policy checks في الريبو | Platform Squad | 14 يوم | 100% تغطية للأوامر الحساسة |
| بناء provider routing scorecard v1 | AI Platform | 21 يوم | خفض تكلفة/طلب + رفع reliability |
| إطلاق verification ledger v1 | Trust/Security | 30 يوم | انخفاض contradiction rate |
| اعتماد release gate متعدد المراحل | Engineering + Security | 30 يوم | صفر ترقيات حساسة دون evidence |
| تفعيل revenue+partnership pilot flows | Growth Squads | 45 يوم | إشارات فرص قابلة للتحويل |
| إطلاق executive weekly memo | PMO + Exec Systems | 7 أيام (دوري) | تقليل زمن القرار التنفيذي |

---

**خلاصة تنفيذية (سطر واحد):**

> Dealix في شكله الرسمي النهائي هو منصة نمو مؤسسية متعددة الوكلاء، تربط القرار التنفيذي بالتنفيذ الموثّق، وتوازن بين السرعة، السيادة، الأمان، والنتائج المالية.
