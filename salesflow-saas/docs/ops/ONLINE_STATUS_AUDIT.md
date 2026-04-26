# Dealix — Online Status Audit (2026-04-26)

| Check | URL/Command | Result | Evidence | Proves | Does Not Prove | Next Action |
|-------|-------------|--------|----------|--------|----------------|-------------|
| Health | GET /health | ✅ 200 | `{"status":"ok"}` | API running | Feature correctness | None |
| Pricing | GET /api/v1/pricing/plans | ✅ 200 | 4 plans: pilot/starter/growth/enterprise | Plans defined | Plans visible to customers | Verify landing page |
| Checkout | POST /api/v1/pricing/checkout | ❌ Error | `Payment gateway error` | Route exists | **Payment NOT working** | **Sami: add Moyasar keys** |
| Pipeline | POST /api/v1/automation/daily-pipeline/run | ✅ 200 | batch created, drafts=2 | Draft generation works | Drafts not sent | None |
| Founder Outreach | POST /api/v1/founder-outreach/generate | ✅ 200 | 177 words, opt-out=true | Personalized email generation | Email not sent | None |
| Email Generate | POST /api/v1/automation/email/generate | ✅ 200 | Subject generated | Sector emails work | Not sent | None |
| Reply Classifier | POST /api/v1/automation/reply/classify | ⚠️ Partial | Response received | Route exists | Classification accuracy unverified | Test more |
| WhatsApp | GET /api/v1/os/whatsapp-providers | ✅ 200 | 4 providers | Providers configured | Messages not sent via API | Verify sending |
| OS Stages | GET /api/v1/os/stages | ✅ 200 | 10 stages | Pipeline stages defined | Not tested end-to-end | None |

## Summary
- **7/9 endpoints working**
- **1 CRITICAL BLOCKER: Checkout fails — Moyasar payment keys not configured**
- **1 PARTIAL: Reply classifier needs verification**
