# §3 — Customer Validation Program

> Hard rule: **no Phase 2 feature ships until pilot customers drive the backlog.**
> All customer-facing artifacts live here.

## Contents

| Artifact | Purpose | Owner |
|----------|---------|-------|
| [pilot_agreement_template.md](pilot_agreement_template.md) | Design-partner + paid-pilot contract (draft — counsel reviews before signing) | Founder + Head of CS |
| [pilot_template/success_criteria.md](pilot_template/success_criteria.md) | Per-pilot success definition signed before onboarding | Head of CS |
| [pilot_template/kickoff_checklist.md](pilot_template/kickoff_checklist.md) | 14-point onboarding checklist | Head of CS |
| [friction_log.md](friction_log.md) | Weekly running log of every customer friction | Head of CS |
| [feature_requests.yaml](feature_requests.yaml) | Structured registry of customer-requested features with 3-pilot threshold | Founder |
| [weekly_review_template.md](weekly_review_template.md) | Format for the Wed customer-learnings synthesis | Founder + Head of CS |
| [hypotheses.yaml](hypotheses.yaml) | 12 viability hypotheses tracked to SUPPORTED/FALSIFIED/AMBIGUOUS | Founder |
| [interviews/_template_ar.md](interviews/_template_ar.md) | Arabic 45-min discovery call script + log | Founder |
| [interviews/_template_en.md](interviews/_template_en.md) | English 45-min discovery call script + log | Founder |
| [founder_dashboard.md](founder_dashboard.md) | Weekly Monday printable dashboard (Business Viability Kit §8) | Founder |
| [pricing_discovery.md](pricing_discovery.md) | Van Westendorp + value-based pricing worksheet | Founder |
| [unit_economics.md](unit_economics.md) | Per-customer economics (fill after 3 paying customers) | Founder |
| [defensibility_scorecard.md](defensibility_scorecard.md) | 5-moat scorecard, measured Week 12 + quarterly | Founder |

## Rules

1. **No feature enters the Wave backlog unless it appears in the Friction Log or Feature Requests registry with a customer reference.**
2. **Every pilot's Success Criteria is signed before kickoff.** No verbal commitments.
3. **Founder personally attends ≥1 customer call/week** for 90 days. Customer Proxy Syndrome is a named failure mode (§6).
4. **Friction Log entries must be written within 24h of the conversation.**
5. **If a feature is requested by <3 pilots in ≥30 days, it stays out of the roadmap** (prevents Integration Sprawl — §6).

## Week-12 Phase Gate Inputs

Data used to color the gate (§3 of Execution Waves):
- Signed success criteria completion rates (from `pilot_template/success_criteria.md` per pilot)
- Golden-path completion rate (from Dealix analytics)
- NPS scores (from weekly reviews)
- Reference willingness (captured in friction_log entries)
- Renewal intent (captured in weekly reviews)
