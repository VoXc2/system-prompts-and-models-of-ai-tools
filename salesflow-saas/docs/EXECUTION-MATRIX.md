# Dealix Sovereign Growth OS — Execution Matrix

Complete mapping: **Agent → Purpose → Inputs → Memory → Tools → Events In → Events Out → Decision Rules → Outputs → KPIs → Owner → SLA → HITL Gate**

---

## Family 1: Opportunity & Growth Intelligence

### 1. Partnership Scout Agent

| Field | Value |
|---|---|
| **Agent** | `partnership_scout` |
| **Purpose** | Discover and score potential partners by industry, region, channel fit |
| **Inputs** | Industry sector, target region, strategic criteria, CRM data (existing partners, customer segments) |
| **Memory** | Previous scans, partner interaction history, rejected partners with reasons |
| **Tools** | AI router (think_json), CRM read, market data sources |
| **Events In** | `signal.partner_interest_detected`, `signal.market_shift_detected` |
| **Events Out** | `partnership.opportunity_detected` (fit ≥ 70), routes to `alliance_structuring` (fit ≥ 85) |
| **Decision Rules** | Score partners 0–100 on: strategic fit, revenue potential, geographic alignment, channel complementarity, risk profile |
| **Outputs** | Ranked partner list (JSON), fit scores, recommended partnership model, estimated ARR impact |
| **KPIs** | Partners discovered/month, fit-score accuracy vs outcome, scout-to-sign conversion rate |
| **Owner** | Growth Squad |
| **SLA** | Scan results within 24h of trigger |
| **HITL Gate** | None (discovery only) |

---

### 2. Alliance Structuring Agent

| Field | Value |
|---|---|
| **Agent** | `alliance_structuring` |
| **Purpose** | Design partnership structures with P&L simulation |
| **Inputs** | Partner profile from scout, industry benchmarks, existing partnership templates |
| **Memory** | Previous partnership structures, negotiation outcomes, revenue share benchmarks |
| **Tools** | AI router, financial modeling, term sheet generator |
| **Events In** | `partnership.opportunity_detected` (fit ≥ 85) |
| **Events Out** | `partnership.model_recommended`, `partnership.term_sheet_ready` |
| **Decision Rules** | Select model (referral/rev-share/JV/white-label/tech/distribution) based on partner size, strategic value, risk tolerance |
| **Outputs** | Decision Memo (AR/EN), financial model (3-year P&L), term sheet draft, risk register |
| **KPIs** | Structure-to-sign rate, forecast vs actual partner revenue, time from structure to sign |
| **Owner** | Growth Squad |
| **SLA** | Structure recommendation within 48h |
| **HITL Gate** | Director approval for rev-share/JV; CXO for strategic alliances |

---

### 3. Expansion Playbook Agent

| Field | Value |
|---|---|
| **Agent** | `expansion_playbook` |
| **Purpose** | Build GTM + Pricing + Channel + Compliance plan for new markets |
| **Inputs** | Target market, country, product line, competitive landscape |
| **Memory** | Previous expansion results, localization learnings, compliance requirements by jurisdiction |
| **Tools** | AI router, market data, regulatory databases |
| **Events In** | `growth.market_expansion_candidate`, `signal.market_shift_detected` |
| **Events Out** | `growth.playbook_generated`, `growth.capex_opex_modeled`, `growth.regulatory_clearance_required` |
| **Decision Rules** | TAM ≥ threshold → model economics → compliance feasibility → GTM fit → launch/no-launch |
| **Outputs** | Full playbook (market analysis, GTM, pricing, channels, compliance, financial model), Decision Memo |
| **KPIs** | Playbook-to-launch rate, launch-to-breakeven time, forecast accuracy (revenue/cost) |
| **Owner** | Growth Squad |
| **SLA** | Playbook draft within 5 business days |
| **HITL Gate** | Director for CAPEX > 500K SAR; CXO for new country entry |

---

## Family 2: Corporate Development & M&A

### 4. M&A Target Screener Agent

| Field | Value |
|---|---|
| **Agent** | `ma_screener` |
| **Purpose** | Screen acquisition targets using multi-dimensional fit scoring |
| **Inputs** | Industry, revenue range, strategic criteria, product adjacency requirements |
| **Memory** | Previously screened targets, rejection reasons, successful acquisitions |
| **Tools** | AI router, company databases, financial data sources |
| **Events In** | `signal.acquisition_candidate_detected`, manual trigger |
| **Events Out** | `ma.target_detected` (fit ≥ 65), routes to `dd_analyst` (fit ≥ 80) |
| **Decision Rules** | Score on: strategic fit, revenue adjacency, product adjacency, geography fit, customer overlap, integration complexity, regulatory risk |
| **Outputs** | Ranked target list, fit scores, synergy areas, risk flags |
| **KPIs** | Screened-to-shortlisted %, screening throughput, false-positive rate |
| **Owner** | Corp Dev Squad |
| **SLA** | Screening results within 48h |
| **HITL Gate** | None (screening only) |

---

### 5. Due Diligence Analyst Agent

| Field | Value |
|---|---|
| **Agent** | `dd_analyst` |
| **Purpose** | Manage preliminary due diligence (financial, operational, legal, team) |
| **Inputs** | Target company data, screener results, public financial data |
| **Memory** | DD frameworks, red flag patterns, industry risk benchmarks |
| **Tools** | AI router, financial analysis, compliance checker |
| **Events In** | `ma.target_detected` (fit ≥ 80) |
| **Events Out** | `ma.dd_started`, `ma.dd_risk_flagged` (if red flags), routes to `valuation_synergy` (overall ≥ 70) |
| **Decision Rules** | Score 4 dimensions (financial, operational, legal, team) 0–100; flag red flags; gate: ≥ 70 to proceed |
| **Outputs** | DD report, red/green flags, overall score, recommendation |
| **KPIs** | DD cycle time, red-flag detection accuracy, late-stage surprise rate |
| **Owner** | Corp Dev Squad |
| **SLA** | Preliminary DD within 5 business days |
| **HITL Gate** | Director if red flags > 2; CXO if critical red flag |

---

### 6. Valuation & Synergy Agent

| Field | Value |
|---|---|
| **Agent** | `valuation_synergy` |
| **Purpose** | Estimate fair value via DCF + multiples, calculate synergies |
| **Inputs** | Target financials, DD results, comparable companies, synergy hypotheses |
| **Memory** | Valuation precedents, synergy realization rates, industry multiples |
| **Tools** | AI router, DCF calculator, comparable analysis |
| **Events In** | DD completion (overall ≥ 70) |
| **Events Out** | `ma.valuation_ready` (requires CXO approval) |
| **Decision Rules** | DCF + multiples → average → synergy adjustment → offer range (min/sweet/max) |
| **Outputs** | Valuation report (DCF, multiples, synergies, integration costs, IRR, payback), Decision Memo |
| **KPIs** | Valuation accuracy vs final price, synergy realization rate, IRR forecast accuracy |
| **Owner** | Corp Dev Squad |
| **SLA** | Valuation within 3 business days of DD completion |
| **HITL Gate** | CXO approval mandatory; Board for > 10M SAR |

---

### 7. Executive Negotiator Copilot Agent

| Field | Value |
|---|---|
| **Agent** | `executive_negotiator` |
| **Purpose** | Prepare negotiation scenarios, BATNA, ZOPA, closing strategies |
| **Inputs** | Valuation, target profile, counterparty info, our position/constraints |
| **Memory** | Previous negotiation outcomes, tactic effectiveness, BATNA precedents |
| **Tools** | AI router, scenario simulator |
| **Events In** | `ma.valuation_ready` |
| **Events Out** | `ma.offer_strategy_ready` (requires Director approval) |
| **Decision Rules** | Map leverage → BATNA → ZOPA → 3 scenarios (aggressive/balanced/conservative) → recommend |
| **Outputs** | Negotiation playbook (leverage, BATNA, ZOPA, 3 scenarios, closing tactics, red lines) |
| **KPIs** | Negotiation outcome vs target, deal terms achieved, cycle time |
| **Owner** | Corp Dev Squad |
| **SLA** | Strategy ready within 48h of valuation |
| **HITL Gate** | Director for offer strategy; CXO for final offer terms |

---

### 8. Post-Merger Integration Agent

| Field | Value |
|---|---|
| **Agent** | `post_merger_integration` |
| **Purpose** | Manage 30/60/90 day PMI plan across all functions |
| **Inputs** | Acquired company data, deal terms, synergy targets, team info |
| **Memory** | PMI playbooks, integration learnings, function-specific checklists |
| **Tools** | AI router, project management, milestone tracker |
| **Events In** | `ma.deal_signed` |
| **Events Out** | `ma.integration_kickoff`, `ma.integration_milestone` (x3), `execution.sla_breached` |
| **Decision Rules** | Phase gate: Day 30 (stabilize) → Day 60 (integrate) → Day 90 (optimize) |
| **Outputs** | PMI plan (systems, teams, customers, brand, operations), risk register, KPIs |
| **KPIs** | Integration on-time rate, synergy realization pace, customer retention, team retention |
| **Owner** | Corp Dev Squad + PMO |
| **SLA** | Plan within 48h of deal signing; milestone checks at 30/60/90 |
| **HITL Gate** | CXO for integration exceptions; Board for synergy shortfall > 20% |

---

## Family 3: Governance & Execution

### 9. Strategic PMO Agent

| Field | Value |
|---|---|
| **Agent** | `strategic_pmo` |
| **Purpose** | Convert decisions into executable initiatives with SLAs, owners, milestones |
| **Inputs** | Approved Decision Memos, strategic events, board directives |
| **Memory** | Initiative history, SLA performance, dependency patterns, bottleneck patterns |
| **Tools** | AI router, project decomposition, dependency mapper |
| **Events In** | `governance.hitl_approved`, any approved Decision Memo |
| **Events Out** | `execution.initiative_created`, `execution.sla_breached`, `execution.escalation_triggered` |
| **Decision Rules** | Break into work packages → assign owners → set milestones → define SLAs → monitor daily |
| **Outputs** | Initiative list (name, owner, milestones, SLA, deps, KPIs), status dashboard |
| **KPIs** | Initiative on-time rate, SLA breach rate, escalation resolution time, initiative-to-outcome rate |
| **Owner** | PMO Squad |
| **SLA** | Initiative plan within 24h of approval; SLA check daily |
| **HITL Gate** | None for creation; CXO for SLA override |

---

### 10. Sovereign Growth Intelligence Agent

| Field | Value |
|---|---|
| **Agent** | `sovereign_growth` |
| **Purpose** | Executive dashboard — board-level strategic synthesis (READ ONLY) |
| **Inputs** | All strategic events, all pending approvals, all initiative statuses |
| **Memory** | Previous briefs, board feedback, strategic priorities |
| **Tools** | AI router, event bus reader |
| **Events In** | All domains (read-only subscription) |
| **Events Out** | None (aggregator only) |
| **Decision Rules** | Synthesize → rank opportunities by impact × confidence → flag risks by severity → aggregate pipeline |
| **Outputs** | Executive brief (highlights, top opportunities, top risks, pipeline, recommendations) |
| **KPIs** | Brief accuracy, recommendation acceptance rate, decision latency reduction |
| **Owner** | Executive Systems |
| **SLA** | Daily brief by 08:00 Riyadh time; board pack 48h before meeting |
| **HITL Gate** | None (information only) |

---

## State Machines

### Partnership State Machine
```
detected → enriched → scored → shortlisted → structure_drafted →
business_case_ready → approval_pending → negotiation_live →
signed → launched → performance_review → expanded | terminated
```

### M&A State Machine
```
detected → screened → shortlisted → intro_initiated →
diligence_prep → diligence_in_progress → valuation_completed →
ic_review_pending → board_review_pending → offer_submitted →
signed → closed → integrated → synergy_tracking → exit_review
```

### Expansion State Machine
```
market_candidate → attractiveness_assessed → entry_mode_selected →
economics_modeled → compliance_cleared → launch_prepared →
launch_live → stabilization → scale_up | stop_loss
```

---

## Agent Interaction Flow

```
Signal Sources (CRM/ERP/Market/Internal)
    │
    ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Partnership     │    │ M&A Screener     │    │ Expansion       │
│ Scout           │    │                  │    │ Playbook        │
│ (fit ≥ 70)      │    │ (fit ≥ 65)       │    │                 │
└────────┬────────┘    └────────┬─────────┘    └────────┬────────┘
         │ fit ≥ 85            │ fit ≥ 80               │
         ▼                     ▼                        │
┌─────────────────┐    ┌──────────────────┐             │
│ Alliance        │    │ DD Analyst       │             │
│ Structuring     │    │ (score ≥ 70)     │             │
└────────┬────────┘    └────────┬─────────┘             │
         │                     ▼                        │
         │             ┌──────────────────┐             │
         │             │ Valuation &      │             │
         │             │ Synergy          │             │
         │             └────────┬─────────┘             │
         │                     ▼                        │
         │             ┌──────────────────┐             │
         │             │ Executive        │             │
         │             │ Negotiator       │             │
         │             └────────┬─────────┘             │
         │                     │                        │
         ▼                     ▼                        ▼
┌──────────────────────────────────────────────────────────────┐
│                  GOVERNANCE ENGINE                            │
│  Policy Gates → Approval Matrix → HITL → Audit Trail         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  STRATEGIC PMO                                │
│  Decision → Initiatives → Milestones → SLAs → Monitoring     │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              SOVEREIGN GROWTH INTELLIGENCE                    │
│  Board Brief → Opportunities → Risks → Pipeline → Actions    │
└──────────────────────────────────────────────────────────────┘
```

---

## Governance Controls Summary

| Decision Type | Required Role | Risk Memo | Compliance | Financial Impact | Rollback |
|---|---|---|---|---|---|
| Referral partnership | Manager | No | No | No | No |
| Rev-share partnership | Director | Yes | No | Yes | No |
| JV / Strategic alliance | CXO | Yes | Yes | Yes | Yes |
| LOI submission | CXO | Yes | Yes | Yes | Yes |
| Acquisition offer | Board | Yes | Yes | Yes | Yes |
| Market entry (< 500K) | Director | Yes | Yes | Yes | No |
| Market entry (> 500K) | CXO | Yes | Yes | Yes | Yes |
| Stop-loss trigger | CXO | Yes | No | No | No |
| Bulk outreach | Manager | No | Yes (PDPL) | No | No |
| Data sharing with partner | Director | No | Yes | No | No |

---

*Generated by Dealix Sovereign Growth OS — Architecture v1.0*
