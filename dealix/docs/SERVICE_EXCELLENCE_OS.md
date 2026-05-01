# Service Excellence OS — مصنع الخدمات الممتازة

> **القاعدة:** لا خدمة تطلق إنتاجياً إلا إذا حصلت على score ≥80 وتجاوزت 4 quality gates. ولا تتوقف عند الإطلاق — تستمر في التحسين الأسبوعي.

---

## 1. الوحدات

| الوحدة | الدور |
|--------|------|
| `feature_matrix` | 12 must-have feature لكل خدمة + advanced/premium/future. |
| `service_scoring` | 10 أبعاد × 10 نقاط = 100. status: launch_ready / beta_only / needs_work. |
| `quality_review` | 4 gates: proof / approval / pricing / channels. |
| `competitor_gap` | مقارنة structural بـ7 فئات منافسين. |
| `proof_metrics` | الـ metrics المطلوبة + ROI estimate. |
| `research_lab` | brief شهري + hypotheses + experiments. |
| `service_improvement_backlog` | feedback → backlog → prioritization. |
| `launch_package` | landing + sales + demo + onboarding. |

---

## 2. الـ 12 Must-Have Features (لكل خدمة)

1. Self-Serve Intake.
2. AI Recommendation.
3. Data Quality Check.
4. Contactability / Risk Gate.
5. Channel Strategy.
6. Arabic Contextual Drafting.
7. Approval Cards.
8. Execution Mode (draft/export/approved).
9. Proof Pack.
10. Learning Loop.
11. Upsell Path.
12. Service Score.

---

## 3. الـ 10 أبعاد للـ Score

| البُعد | الوزن |
|------|----:|
| Clarity (وضوح الألم) | 10 |
| Speed-to-Value | 10 |
| Automation | 10 |
| Compliance | 10 |
| Proof | 10 |
| Upsell | 10 |
| Uniqueness (Saudi-first) | 10 |
| Scalability (multi-sector) | 10 |
| Ops Daily (autopilot) | 10 |
| Proof Data | 10 |

**Status:**
- ≥80: `launch_ready`
- ≥60: `beta_only`
- <60: `needs_work`

---

## 4. الـ 4 Quality Gates

قبل إطلاق أي خدمة:

1. **Proof gate** — لا proof_metrics → blocked.
2. **Approval gate** — لا approval_policy → blocked.
3. **Pricing gate** — تسعير غير منطقي → blocked.
4. **Channels gate** — تكامل غير آمن (scraping/auto_dm/etc.) → blocked.

`review_service_before_launch(service_id)` يُرجع verdict واحد من:
- `launch_ready`
- `beta_only`
- `needs_work`
- `blocked_at_gate`

---

## 5. Competitor Gap (7 فئات)

| Category | Strengths | Limits |
|----------|-----------|--------|
| CRM عام | تخزين بيانات | ينتظر إدخال يدوي |
| WhatsApp tools | Broadcast | لا approval-first |
| Email assistants | كتابة أسرع | لا تحول الإيميل لـ pipeline |
| LinkedIn tools | إيجاد leads | كثيرها يخالف ToS |
| وكالات | خبرة بشرية | لا تتوسع |
| Revenue intelligence | تحليل calls | تبدأ بعد المكالمة |
| Generic AI agent | مرن | بدون سياق شركة |

**ميزات Dealix:**
- موجّه للسوق السعودي.
- Approval-first.
- Proof Pack شهري.
- Multi-channel orchestration.
- Self-improving Curator.
- PDPL-aware.

---

## 6. Research Lab (شهرياً)

لكل خدمة:
- 6 أسئلة بحث (من اشترى، TTV، اعتراضات، deliverables، metrics، pricing).
- 4-5 hypotheses للتحسين.
- 3 experiments الأولوية (impact/effort).
- Monthly review بـ score حالي + gap + experiments.

---

## 7. Improvement Backlog

- `convert_feedback_to_backlog` — Feedback → backlog item.
- `prioritize_backlog_items` — impact desc, effort asc.
- `recommend_weekly_improvements` — 3 weekly tasks.

---

## 8. Launch Package (per service)

1. **Landing outline** (RTL Arabic): hero, promise, 3-step how-it-works, deliverables, pricing, proof, safety, FAQ, CTA.
2. **Sales script**: 5 discovery questions + pitch + 4 objection handlers + close.
3. **Demo script**: 12-min minute-by-minute Arabic walkthrough.
4. **Onboarding checklist**: first-5-days plan.

---

## 9. Endpoints (`/api/v1/service-excellence/...`)

```
GET  /{id}/feature-matrix
GET  /{id}/feature-classification
GET  /{id}/missing-features
GET  /{id}/score
GET  /{id}/quality-review
GET  /review/all
GET  /{id}/proof-metrics
POST /{id}/roi-estimate
GET  /{id}/gap-analysis
GET  /{id}/research-brief
GET  /{id}/feature-hypotheses
GET  /{id}/experiments
GET  /{id}/monthly-review
GET  /{id}/backlog
POST /{id}/backlog/from-feedback
POST /{id}/backlog/prioritize
GET  /{id}/weekly-improvements
GET  /{id}/launch-package
GET  /{id}/landing-outline
GET  /{id}/sales-script
GET  /{id}/demo-script
GET  /{id}/onboarding-checklist
```

---

## 10. اختبارات

`tests/unit/test_service_excellence.py` — 33 اختبار:
- Feature matrix ≥10 must-haves.
- Score returns valid status.
- Every catalogued service passes the 4 gates.
- ROI estimate returns x-multiples.
- Competitor gap lists advantages + do-not-copy.
- Research brief has ≥5 questions.
- Hypotheses ≥3 + experiments ≤3.
- Backlog conversion + prioritization.
- Launch package complete.
- Demo script = 12 minutes.

---

## 11. Weekly Improvement Loop

```
كل اثنين:
1. شغّل /review/all على كل الـ 12 خدمة.
2. أي خدمة < 80 → افتح backlog item.
3. أي خدمة blocked → إصلاح فوري قبل إطلاق جديد.
4. اختر experiment واحد لكل خدمة.

كل جمعة:
1. سجل النتائج في Service Scorecard.
2. حدّث الـ improvement backlog.
3. أرسل executive brief للمؤسس.
```
