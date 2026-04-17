# Master Remaining Scope Map — Dealix Tier-1 Completion

> **Status**: Active  
> **Updated**: 2026-04-17  
> **Rule**: Core System = done. Remaining = Productization + Operability + Revenue Enablement.

---

## Summary of What's Done

| Layer | Status |
|-------|--------|
| Governance docs (26+) | Done |
| Backend models (3 Tier-1) | Done |
| Backend services (6 Tier-1 + all real DB) | Done |
| Backend APIs (8 Tier-1, all wired) | Done |
| Frontend components (9 Tier-1, all wired to APIs) | Done |
| Structured output schemas (17 Pydantic) | Done (defined, not yet enforced) |
| Architecture brief (40/40) | Done |
| Revenue activation docs | Done |
| CODEOWNERS | Done |

---

## 1. Backend Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| Runtime enforcement inventory | Every endpoint needs approval_class + sensitivity + reversibility | Target |
| Enforce ApprovalPacket schema on Class B actions | No free-form approval payloads | Target |
| Auto-assemble evidence pack on deal close | Currently manual only | Target |
| Wire LeadScoreCard to lead qualification agent | 17 schemas defined, 0 used | Target |
| correlation_id propagation through OpenClaw gateway | Needed for trust audit trail | Target |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Idempotency keys for all side-effect endpoints | Prevent duplicate actions on retry | Target |
| Connector health probes (live WhatsApp/Stripe check) | Currently only tracks status, no probe | Target |
| Telemetry: trace propagation + structured logs | Needed for production observability | Target |
| Saudi compliance live validation (actual consent coverage check) | Currently seeds controls as PARTIAL | Target |

### Strategic Later
| Item | Why | Status |
|------|-----|--------|
| OPA policy engine | Replace/augment policy.py when rules exceed 50 | Watch |
| OpenFGA authorization | When RBAC insufficient for relationship-based access | Watch |
| Temporal for durable workflows | When partner/DD/signature flows need crash-proof execution | Watch |
| Compensation/rollback logic | Required before Temporal adoption | Target |

---

## 2. Frontend Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| Loading/empty/error states for all 9 components | Professional UX | Partial |
| Demo mode vs live mode indicator | Prevent confusion between demo and production | Target |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Executive readability polish | Layout for CEO, not engineer | Partial |
| Print/export modes for executive surfaces | Board pack export | Target |
| Arabic/RTL typography polish | Professional Arabic rendering | Partial |
| State badges for approval severity | Visual trust indicators | Target |

### Strategic Later
| Item | Why | Status |
|------|-----|--------|
| Role-personalized surfaces (CEO vs Operator vs Admin) | Different views per role | Target |
| Timeline views for approvals and commitments | Historical decision tracking | Target |
| Embedded playbooks in UI | Inline guidance for users | Target |

---

## 3. Documentation Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| Customer onboarding guide | For pilot clients | Partial (deployment guide exists) |
| Admin setup guide | For client IT team | Target |
| Executive quickstart | For CEO first use | Target |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Operator guide | Day-to-day operations | Target |
| FAQ (operational) | Common questions | Target |
| Implementation checklist | Pre-deployment verification | Partial |

### Strategic Later
| Item | Why | Status |
|------|-----|--------|
| Deployment models document | Cloud/on-prem/hybrid options | Target |
| Integration playbooks per connector | WhatsApp, Salesforce, Stripe setup | Partial |
| Incident handbook | Production incident response | Target |

---

## 4. Marketing Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| One-line positioning | What Dealix is in one sentence | Partial (market-dominance-plan.md) |
| ICP definition | Who to sell to | Done (FIRST_3_CLIENTS_PLAN.md) |
| Why not CRM / RPA / copilot | Competitive differentiation | Done (market-dominance-plan.md) |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Homepage copy | Public website | Target |
| Trust/compliance page | Enterprise buyer requirement | Target |
| Saudi/GCC readiness page | Regional differentiation | Target |
| Use-case pages | Sector-specific value | Partial (presentations exist) |

### Strategic Later
| Item | Why | Status |
|------|-----|--------|
| Industry pages | Vertical GTM | Target |
| Category creation narrative | Thought leadership | Target |
| Analyst positioning pack | For Gartner/Forrester | Target |

---

## 5. Sales Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| Pilot scope template | For first 3 clients | Done (FIRST_3_CLIENTS_PLAN.md) |
| Demo script | Executive simulation | Done (FIRST_3_CLIENTS_PLAN.md) |
| Pricing sheet | 3-tier pricing | Done (FIRST_3_CLIENTS_PLAN.md) |
| Outreach scripts | WhatsApp/LinkedIn/Email | Done (whatsapp-sequences.json) |
| Objection handling | Common objections + responses | Done (FIRST_3_CLIENTS_PLAN.md) |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| ROI calculator | Quantified value for prospects | Target |
| Security/compliance brief | For enterprise procurement | Partial |
| Case study template | After first pilot | Done (FIRST_3_CLIENTS_PLAN.md) |

---

## 6. Customer Success Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| Kickoff checklist | First day with client | Done (LIVE_DEPLOYMENT_GUIDE.md) |
| First 14 days success plan | Pilot monitoring | Done (LIVE_DEPLOYMENT_GUIDE.md) |
| Post-pilot conversion script | Convert to paid | Done (FIRST_3_CLIENTS_PLAN.md) |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Weekly adoption review | Ongoing engagement | Partial |
| Monthly ROI review | Value demonstration | Target |
| Support severity model | SLA for client support | Target |

---

## 7. Release Remaining

### Must Now
| Item | Why | Status |
|------|-----|--------|
| CI backend tests passing | Current blocker | In Progress (pinned deps) |
| Architecture brief in CI | Governance gate | Done (in CI YAML) |
| CODEOWNERS enforced | Protect sensitive paths | Done |

### Should Next
| Item | Why | Status |
|------|-----|--------|
| Branch protection on main | Prevent direct push | Target (GitHub settings) |
| Required CI checks | Block merge on failure | Target (GitHub settings) |
| Secret scanning | Prevent credential leaks | Target (GitHub settings) |
| Release readiness matrix as PR gate | Block RC without evidence | Target |

### Strategic Later
| Item | Why | Status |
|------|-----|--------|
| OIDC for cloud access | Eliminate long-lived secrets | Watch |
| Artifact attestations | Build provenance | Watch |
| Canary deployment | Gradual rollout | Target |
| Audit log streaming | Long-term retention | Target |

---

## Priority Summary

### 🔴 Must Fix Now (blocks launch/sale)
1. CI backend tests passing
2. Runtime enforcement on Class B paths
3. Schema enforcement on approval/evidence outputs
4. Auto-assemble evidence on deal close

### 🟡 Should Do Next (improves quality/trust)
5. Frontend loading/empty/error states
6. Telemetry + correlation propagation
7. Connector live health probes
8. Saudi compliance live validation
9. Branch protection + required checks

### 🟢 Strategic Later (expands market/moat)
10. OPA/OpenFGA/Temporal adoption
11. Role-personalized surfaces
12. Industry GTM pages
13. OIDC + artifact attestations
14. Renewal/expansion automation
