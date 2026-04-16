## Summary
<!-- 1-3 bullet points describing the change -->

## Business Context
<!-- Why is this change needed? What initiative/decision does it support? -->

## Linked Initiative
<!-- Reference the strategic initiative, ADR, or decision memo -->
- Initiative: 
- ADR: 

## Impact Assessment

### User / Business Impact
<!-- How does this affect users, revenue, or operations? -->

### Risk Level
- [ ] Low — Isolated change, easily reversible
- [ ] Medium — Affects shared systems, requires testing
- [ ] High — Affects production data, billing, or compliance
- [ ] Critical — Requires board/CXO awareness

### Data / Privacy Impact
- [ ] No PII involved
- [ ] PII processed — PDPL compliance verified
- [ ] New data collection — consent flow added
- [ ] Data sharing with partners — governance approval obtained

## Rollback Plan
<!-- How to revert if something goes wrong -->

## Observability
- [ ] Logging added for new paths
- [ ] Metrics/KPIs updated
- [ ] Alerts configured (if applicable)
- [ ] Audit trail entries for strategic actions

## Test Plan
- [ ] Unit tests added/updated
- [ ] Integration tests (if applicable)
- [ ] Manual testing completed
- [ ] Arabic + English tested
- [ ] RTL layout verified (if UI change)

## Checklist
- [ ] Code follows project conventions (see AGENTS.md)
- [ ] No secrets or PII in code
- [ ] Tenant isolation maintained
- [ ] PDPL consent checked (if outbound messaging)
- [ ] Governance engine consulted (if strategic action)
- [ ] ADR created (if architectural change)
