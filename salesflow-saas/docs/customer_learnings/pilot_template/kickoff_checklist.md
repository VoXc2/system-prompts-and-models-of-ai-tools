# Pilot Kickoff Checklist — [CUSTOMER NAME]

> Complete in the 10 business days before pilot start.
> Head of CS owns; Founder reviews.

---

## Week −2

- [ ] Pilot agreement signed (`pilot_agreement_template.md` adapted)
- [ ] DPA signed (`docs/legal/templates/DPA_EN.md`)
- [ ] Success Criteria document signed (`success_criteria.md`)
- [ ] Executive Sponsor + Operational Lead identified and intro'd
- [ ] Invoice sent if paid pilot; receipt confirmed

## Week −1

- [ ] Tenant provisioned in production (region: me-south-1)
- [ ] Named users created with appropriate roles (per RBAC)
- [ ] SSO configured (if Wave B shipped and requested)
- [ ] ZATCA e-invoicing enabled if applicable
- [ ] Integration seeds loaded (industry template if applicable)
- [ ] Arabic locale confirmed default for all users
- [ ] Demo data seeded in sandbox for training
- [ ] Runbook shared with Customer IT (`revenue-activation/deployment/ADMIN_SETUP_GUIDE.md`)

## Kickoff Day

- [ ] 90-minute kickoff call with Sponsor + Ops Lead
- [ ] Success Criteria re-read aloud
- [ ] First Golden Path walked through live
- [ ] Weekly 30-min session scheduled for 12 weeks (same time weekly)
- [ ] Slack/WhatsApp/Email channel for async support agreed
- [ ] Friction Log public link shared so Customer can add entries

## Week +1

- [ ] First Golden Path run by Customer (unassisted) logged
- [ ] First Evidence Pack generated
- [ ] Weekly check-in #1 completed, notes in `friction_log.md`
- [ ] Any P0/P1 issues resolved within SLA

---

## Red Flags to Halt Kickoff

Do NOT go live until resolved:
- Executive Sponsor is a proxy (delegate), not the named sponsor
- Success Criteria unsigned at T-2 days
- Named users not provisioned 48h before kickoff
- Customer pushing for features outside Scope before first run
- Compliance questionnaire unanswered
