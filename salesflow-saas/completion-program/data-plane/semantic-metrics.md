# Semantic Metrics Dictionary

> **Version:** 1.0 — 2026-04-16
> **Authority:** Product Lead — every dashboard metric must trace to an entry here.
> **Format:** Metric → Formula → Grain → Source Table → Owner → SLA

---

## Reading Guide

| Column | Definition |
|--------|-----------|
| **Metric** | Business-meaningful name (Arabic + English) |
| **Formula** | Precise calculation definition |
| **Grain** | Lowest level of detail (per tenant / per track / per deal) |
| **Source Table** | Postgres table(s) or service |
| **Owner** | Role responsible for accuracy |
| **Update SLA** | How fresh must the data be in dashboards |

---

## Track 1 — Prospecting

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| P-01 | عدد العملاء المحتملين المُولَّدين / Leads Generated | `COUNT(leads WHERE created_at >= period_start)` | Daily / Tenant | `leads` | Data Engineer | 1 h |
| P-02 | نسبة جودة الخيط / Lead Quality Score | `AVG(lead_score) WHERE created_at >= period_start` | Daily / Tenant | `leads.score` | AI Lead | 1 h |
| P-03 | تكلفة الخيط / Cost Per Lead (SAR) | `SUM(campaign_spend) / COUNT(leads)` | Monthly / Campaign | `campaigns`, `leads` | Product Lead | Daily |
| P-04 | معدل استجابة الاتصال الأول / First Contact Response Rate | `COUNT(leads WHERE first_reply_at IS NOT NULL) / COUNT(leads)` | Weekly / Channel | `leads`, `conversations` | AI Lead | Daily |

---

## Track 2 — Qualification

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| Q-01 | معدل تأهيل الخيوط / Lead-to-Qualified Rate | `COUNT(qualified_leads) / COUNT(leads) * 100` | Weekly / Tenant | `leads` | Product Lead | Daily |
| Q-02 | متوسط وقت التأهيل / Avg. Qualification Time (hours) | `AVG(qualified_at - created_at)` in hours | Weekly / Tenant | `leads` | AI Lead | Daily |
| Q-03 | نسبة الاجتماعات المحجوزة / Meeting Booking Rate | `COUNT(meetings_booked) / COUNT(qualified_leads) * 100` | Weekly / Tenant | `meetings`, `leads` | Product Lead | Daily |
| Q-04 | معدل الحضور / Meeting Attendance Rate | `COUNT(meetings_attended) / COUNT(meetings_booked) * 100` | Weekly / Tenant | `meetings` | Product Lead | Daily |

---

## Track 3 — Proposal

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| PR-01 | عدد العروض المُرسَلة / Proposals Sent | `COUNT(proposals WHERE sent_at >= period_start)` | Weekly / Tenant | `proposals` | Product Lead | 1 h |
| PR-02 | متوسط وقت إنشاء العرض / Avg. Proposal Creation Time (minutes) | `AVG(sent_at - initiated_at)` in minutes | Weekly | `proposals` | AI Lead | Daily |
| PR-03 | معدل فتح العرض / Proposal Open Rate | `COUNT(proposals WHERE opened_at IS NOT NULL) / COUNT(proposals WHERE sent_at IS NOT NULL) * 100` | Weekly | `proposals` | Product Lead | Daily |
| PR-04 | قيمة المسار / Pipeline Value (SAR) | `SUM(deal_value) WHERE deal_stage IN ('proposal', 'negotiation')` | Real-time / Tenant | `deals` | Product Lead | 15 min |

---

## Track 4 — Negotiation

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| N-01 | معدل تغيير السعر / Price Change Rate | `COUNT(deals WHERE final_value != proposed_value) / COUNT(deals)` | Monthly | `deals` | Product Lead | Daily |
| N-02 | متوسط الخصم الممنوح / Avg. Discount Granted (%) | `AVG((proposed_value - final_value) / proposed_value * 100)` | Monthly | `deals` | Product Lead | Daily |
| N-03 | متوسط مدة التفاوض / Avg. Negotiation Duration (days) | `AVG(closed_at - negotiation_started_at)` in days | Monthly | `deals` | AI Lead | Daily |
| N-04 | معدل نجاح التفاوض / Negotiation Win Rate | `COUNT(deals WHERE outcome = 'won') / COUNT(deals WHERE stage_reached = 'negotiation') * 100` | Monthly | `deals` | Product Lead | Daily |

---

## Track 5 — Closing

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| C-01 | معدل الإغلاق / Close Rate | `COUNT(deals WHERE outcome = 'won') / COUNT(deals WHERE stage IN ('closing','negotiation')) * 100` | Monthly / Tenant | `deals` | Product Lead | 1 h |
| C-02 | متوسط حجم الصفقة / Avg. Deal Size (SAR) | `AVG(final_value) WHERE outcome = 'won'` | Monthly | `deals` | Product Lead | Daily |
| C-03 | دورة المبيعات / Sales Cycle Length (days) | `AVG(closed_at - lead_created_at)` in days | Monthly | `deals`, `leads` | Product Lead | Daily |
| C-04 | الإيراد الشهري المتكرر / MRR (SAR) | `SUM(monthly_contract_value) WHERE status = 'active'` | Real-time | `contracts` | Product Lead | 15 min |
| C-05 | الإيراد السنوي المتكرر / ARR (SAR) | `MRR * 12` | Real-time | Computed from C-04 | Product Lead | 15 min |
| C-06 | توقيت التوقيع / Time-to-Signature (hours) | `AVG(signed_at - docusign_sent_at)` in hours | Weekly | `signatures` | AI Lead | Daily |

---

## Track 6 — Post-Sale / Upsell

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| PS-01 | درجة صحة العميل / Customer Health Score | Weighted composite: `(engagement * 0.3) + (nps * 0.3) + (usage * 0.2) + (payment_timeliness * 0.2)` | Weekly / Account | `health_events`, `nps_surveys`, `billing` | AI Lead | Daily |
| PS-02 | معدل الاحتفاظ / Retention Rate | `COUNT(accounts WHERE status='active' at period_end) / COUNT(accounts WHERE status='active' at period_start) * 100` | Monthly | `accounts` | Product Lead | Daily |
| PS-03 | معدل التوسع / Expansion Rate | `SUM(upsell_value) / SUM(base_mrr) * 100` | Monthly | `deals`, `contracts` | Product Lead | Daily |
| PS-04 | صافي نقاط الترويج / NPS | `% Promoters - % Detractors` | Quarterly | `nps_surveys` | Product Lead | Per survey |
| PS-05 | معدل الانسحاب / Churn Rate | `COUNT(accounts WHERE churned_at >= period_start) / COUNT(accounts at period_start) * 100` | Monthly | `accounts` | Product Lead | Daily |
| PS-06 | متوسط قيمة العميل / LTV (SAR) | `(Avg MRR per account) * (1 / Churn Rate)` | Quarterly | Computed | Product Lead | Weekly |

---

## Cross-Track / Platform Metrics

| # | Metric (AR / EN) | Formula | Grain | Source | Owner | SLA |
|---|-----------------|---------|-------|--------|-------|-----|
| X-01 | دقة قرار الوكيل / Agent Decision Accuracy | `COUNT(decisions WHERE human_override = false) / COUNT(decisions) * 100` | Daily | `agent_decisions` | AI Lead | 1 h |
| X-02 | متوسط درجة الثقة / Avg. Confidence Score | `AVG(confidence_score) WHERE agent_role IN ('Recommender', 'Executor')` | Daily | `agent_decisions` | AI Lead | 1 h |
| X-03 | معدل تعارض الأدوات / Tool Contradiction Rate | `COUNT(tool_verifications WHERE contradiction_status != 'none') / COUNT(tool_verifications) * 100` | Daily | `tool_verification_ledger` | AI Lead | 1 h |
| X-04 | وقت الاستجابة للموافقة / HITL Approval Time (hours) | `AVG(resolved_at - created_at) WHERE status = 'approved'` in hours | Weekly | `approval_packets` | Product Lead | Daily |
| X-05 | تغطية الامتثال / Compliance Coverage | `COUNT(actions WHERE opa_policy_passed = true) / COUNT(actions) * 100` | Daily | `opa_decisions_log` | Security Lead | 1 h |
| X-06 | استخدام رموز LLM / LLM Token Usage (per tenant) | `SUM(prompt_tokens + completion_tokens) per tenant per day` | Daily / Tenant | `llm_usage_log` | Platform Engineer | 1 h |

---

## Metric Governance Rules

1. **No metric added to any dashboard without an entry here first.**
2. **Formula must be unambiguous** — specify period_start/end, filters, and aggregation function.
3. **Source table must exist** — no derived metrics from metrics (go back to raw tables).
4. **All new metrics reviewed** by Product Lead + Data Engineer before production.
5. **Breaking metric changes** (formula change) require versioning: `C-04_v2` with deprecation date for `C-04`.
6. **Arabic and English names both required** for all business-facing metrics.
