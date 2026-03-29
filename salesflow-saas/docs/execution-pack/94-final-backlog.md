# Final Integrated Backlog

## Epic Priority Matrix

### P0 — Must Ship (Foundation)
| Epic | Status | Dependencies |
|------|--------|-------------|
| Multi-tenant auth + RBAC | DONE | — |
| Lead CRUD + scoring | DONE | Auth |
| Deal CRUD + pipeline | DONE | Auth, Leads |
| Conversation hub | DONE | Auth, Leads |
| Sequence engine | DONE | Leads, Conversations |
| AI agent system + governance | DONE | Auth |
| Analytics + velocity | DONE | Deals, Leads |
| PDPL compliance (consent + suppression) | DONE | Leads |
| Audit trail | DONE | Auth |
| Alembic migrations | IN PROGRESS | All models |
| Playbooks (industry) | DONE | — |
| SLA tracking | DONE | Leads, Deals |

### P1 — Must Ship (Value Delivery)
| Epic | Status | Dependencies |
|------|--------|-------------|
| Appointment booking | DONE | Leads |
| Proposal generation | DONE | Deals |
| Contract + e-sign | DONE | Deals, Proposals |
| Social listening | DONE | AI Agents |
| Customer management | DONE | Leads |
| Growth events / attribution | DONE | Leads, Deals |
| Integration management | DONE | Auth |
| Notification system | DONE | Auth |
| WhatsApp Business API | DONE | Conversations |
| Frontend analytics (velocity + SLA) | DONE | Analytics API |

### P2 — Should Ship (Differentiation)
| Epic | Status | Dependencies |
|------|--------|-------------|
| Widget SDK (embeddable forms) | NOT STARTED | Public API |
| Operator console | NOT STARTED | Multi-tenant admin |
| White-label branding | PARTIAL | Tenants |
| Email integration (SMTP/SES) | NOT STARTED | Messages |
| Calendar sync (Google/Outlook) | NOT STARTED | Appointments |
| Reactivation automation | PARTIAL | Sequences |
| Content calendar AI | DONE | AI Agents |
| Voice AI | PARTIAL | AI Agents |
| Webhook subscriptions (outbound) | NOT STARTED | Events |
| Mobile-responsive optimization | PARTIAL | Frontend |

### P3 — Nice to Have (Future)
| Epic | Status |
|------|--------|
| Native mobile app | NOT STARTED |
| Real-time WebSocket updates | NOT STARTED |
| Advanced reporting builder | NOT STARTED |
| Multi-language support beyond Arabic/English | NOT STARTED |
| Marketplace for integrations | NOT STARTED |
| Self-serve API key management | NOT STARTED |
| Organization → Workspace hierarchy | NOT STARTED |
| Advanced ABM with company enrichment | NOT STARTED |

## Immediate Build Sequence

### Week 1: Foundation Lock
1. Complete and commit Alembic migration (**IN PROGRESS**)
2. Commit all execution-pack docs
3. Push to branch
4. Verify all Python files parse clean
5. Verify all frontend pages render

### Week 2: Integration Hardening
1. Email sending integration (SMTP)
2. Google Calendar connector
3. Webhook signature verification for all providers
4. Widget SDK v0.1 (lead capture form)

### Week 3: Operator Console v1
1. Tenant list with health scores
2. Cross-tenant SLA breach view
3. AI cost dashboard
4. Approval queue (cross-tenant)

### Week 4: Testing & Polish
1. Unit tests for critical services (auth, leads, deals, sequences)
2. Integration tests for API routes
3. Load test for public form submit
4. Security audit (OWASP top 10 check)

## Definition of Done
- [ ] Code written and syntax-checked
- [ ] API endpoint responds correctly
- [ ] Frontend page renders with data
- [ ] Audit logging wired
- [ ] PDPL compliance verified (suppression, consent)
- [ ] Arabic labels and RTL verified
- [ ] Committed to git with descriptive message
