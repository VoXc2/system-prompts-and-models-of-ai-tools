# مصفوفة التنفيذ — 90 يوم (Tier 1)

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> تحدد هذه المصفوفة ما يجب إنجازه خلال 90 يوماً لتحويل Dealix من "جاهز تقنياً" إلى "جاهز مؤسسياً".

---

## النموذج

| Phase | Window | Focus |
|-------|--------|-------|
| **A** — Freeze & Verify | أسبوع 1-2 | تجميد + تحقق + إزالة تناقضات |
| **B** — Live Surface | أسبوع 3-6 | أسطح تشغيلية حية |
| **C** — Trust & Workflow Proof | أسبوع 7-10 | إثبات الثقة والتحكم |
| **D** — Saudi Enterprise Ready | أسبوع 11-12 | جاهزية مؤسسية سعودية |
| **E** — Dominance Prep | أسبوع 13 | تحضير للهيمنة |

---

## Phase A — Freeze & Verify (أسبوع 1-2)

**الهدف:** وقف إضافة أفكار جديدة، إقفال ما بُني، إزالة التناقضات.

| # | المهمة | المالك | معايير الإغلاق | الأولوية | الحالة |
|---|--------|--------|---------------|---------|--------|
| A1 | Current vs Target register | Architecture | جدول واحد موحد لكل subsystem | P0 | **Done** (technology-radar-tier1.md) |
| A2 | Consistency audit | Engineering | 0 contradictions in docs | P0 | In Progress |
| A3 | Command/hook/layout audit | Engineering | `architecture_brief.py` passes | P0 | **Done** (resolve-paths.sh) |
| A4 | Fix agent count (18→19) | Docs | ARCHITECTURE.md updated | P0 | In Progress |
| A5 | Fix completion % (90%→nuanced) | Docs | module-map.md updated | P0 | In Progress |
| A6 | Fix feature flags contradiction | Engineering | Consistent across docs | P1 | In Progress |
| A7 | Docs truth pass | All | Every doc uses Implemented/Partial/Planned/Pilot | P1 | In Progress |
| A8 | Enterprise readiness checklist v1 | PM | Checklist published | P0 | **Done** (this doc + closure checklist) |

---

## Phase B — Live Surface Closure (أسبوع 3-6)

**الهدف:** تحويل الوثائق إلى أسطح تشغيلية حية.

| # | المهمة | المالك | معايير الإغلاق | الأولوية | الحالة |
|---|--------|--------|---------------|---------|--------|
| B1 | Executive Room skeleton | Frontend | Dashboard page with KPIs | P0 | Planned |
| B2 | Approval Center e2e path | Full-stack | ApprovalRequest → review → execute flow working | P0 | Partial (backend ready) |
| B3 | Evidence Pack Viewer | Frontend | View evidence pack for any decision | P1 | Planned |
| B4 | Actual vs Forecast dashboard | Frontend | Revenue actual vs forecast chart | P0 | Planned |
| B5 | Partner Scorecard live | Full-stack | Score view for active partners | P1 | Planned |
| B6 | Tool Verification Ledger | Backend | Searchable tool receipt list | P1 | Partial (receipts exist) |
| B7 | Complete 1 e2e flow: lead→qualify→propose→approve→send | Full-stack | Working demo | P0 | Partial |

---

## Phase C — Trust & Workflow Proof (أسبوع 7-10)

**الهدف:** إثبات أن المنصة تتحكم وتنفذ بأمان.

| # | المهمة | المالك | معايير الإغلاق | الأولوية | الحالة |
|---|--------|--------|---------------|---------|--------|
| C1 | 1 durable workflow pilot | Backend | Prospecting flow running end-to-end | P0 | Partial (durable_flow.py exists) |
| C2 | 1 approval workflow with SLA | Full-stack | WhatsApp outbound with 2h SLA | P0 | Partial (outbound_governance exists) |
| C3 | 1 contradiction-aware tool flow | Backend | Tool receipt flags contradictions | P1 | Planned |
| C4 | 1 evidence pack reproducibility test | QA | Same input → same evidence pack | P1 | Planned |
| C5 | 1 policy gate demo | Demo | Class A/B/C decisions visible | P0 | Partial |
| C6 | Full CI/CD pipeline | DevOps | Test + lint + build + deploy | P1 | Planned |
| C7 | CODEOWNERS + branch protection | DevOps | Enforced on main | P1 | Planned |

---

## Phase D — Saudi Enterprise Ready (أسبوع 11-12)

**الهدف:** جعل المنصة قابلة للعرض على عميل مؤسسي حساس.

| # | المهمة | المالك | معايير الإغلاق | الأولوية | الحالة |
|---|--------|--------|---------------|---------|--------|
| D1 | Compliance matrix (live) | Compliance | مصفوفة تحكم PDPL + NCA + NIST | P0 | **Done** (saudi-compliance doc) |
| D2 | Risk matrix (live) | Security | مصفوفة مخاطر محدثة | P0 | **Done** (saudi-compliance doc) |
| D3 | Audit narrative | Compliance | قصة تدقيق مكتوبة | P0 | **Done** (saudi-compliance doc) |
| D4 | Trust narrative | Security | سرد ثقة | P0 | **Done** (trust-fabric doc) |
| D5 | Governance narrative | PM | سرد حوكمة | P0 | **Done** (MASTER_OPERATING_PROMPT) |
| D6 | Arabic-first operating examples | Engineering | 3+ examples in Arabic | P1 | Partial |
| D7 | SDAIA registration prep | Legal | Application draft | P0 | Planned |
| D8 | DPIA for AI services | Legal | Assessment document | P0 | Planned |

---

## Phase E — Dominance Preparation (أسبوع 13)

**الهدف:** تجهيز المنتج ليكون difficult to replace.

| # | المهمة | المالك | معايير الإغلاق | الأولوية | الحالة |
|---|--------|--------|---------------|---------|--------|
| E1 | Packaged tiers | Product | 3 pricing tiers defined | P1 | Partial (pricing strategy exists) |
| E2 | ROI narrative | Sales | Quantified ROI story | P1 | Partial (metrics defined) |
| E3 | Executive sales deck inputs | Marketing | Deck outline + data | P2 | Planned |
| E4 | Feature moat map | Product | What's hard to replicate | P2 | Planned |
| E5 | Competitor wedge map | Strategy | Key differentiators vs competitors | P2 | Planned |
| E6 | First reference architecture | Architecture | Architecture for first enterprise customer | P1 | Planned |

---

## تعريف "كل شيء تمام"

حتى تقولوا فعلاً إن الوضع صار تمام، لازم تكون هذه كلها صحيحة:

| # | الشرط | المقياس |
|---|-------|---------|
| 1 | كل الوثائق مترابطة ومتسقة | 0 contradictions |
| 2 | كل الأوامر تبدأ من جذر الريبو | `architecture_brief.py` passes |
| 3 | المسارات الستة موصولة بالكود | كل track له ≥1 working path |
| 4 | Trust Plane حي | approval + verification + evidence + audit path working |
| 5 | Phase 1 محكومة بأدلة | لا ادعاءات بدون evidence code |
| 6 | لا خلط بين core/optional/pilot | Technology radar clear |

---

## Dashboard

```
Phase A: ████████████████████░░░░░ 80%  (5/8 done)
Phase B: ████░░░░░░░░░░░░░░░░░░░░ 15%  (1/7 partial)
Phase C: ███░░░░░░░░░░░░░░░░░░░░░ 10%  (3/7 partial)
Phase D: ██████████████░░░░░░░░░░ 55%  (5/8 done)
Phase E: ██░░░░░░░░░░░░░░░░░░░░░░  5%  (1/6 partial)
```

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../MASTER_OPERATING_PROMPT.md)
- رادار التقنية: [`governance/technology-radar-tier1.md`](governance/technology-radar-tier1.md)
- ADR: [`adr/0001-tier1-execution-policy-spikes.md`](adr/0001-tier1-execution-policy-spikes.md)
- Enterprise Closure: [`enterprise-closure-master-checklist.md`](enterprise-closure-master-checklist.md)
