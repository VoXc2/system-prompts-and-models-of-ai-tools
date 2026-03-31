# Dealix (ديل اي اكس) — Launch Blockers

> العوائق المعروفة قبل الإطلاق — يجب حلها أولاً
> Last updated: 2026-03-31

---

## BLOCKERS / عوائق حقيقية

### 1. WhatsApp Business API Credentials
- **Status:** BLOCKED
- **Owner:** Product Owner
- **Details:**
  - يتطلب التحقق من Meta Business Manager
  - Steps: Create Meta Business account → Verify business → Apply for WhatsApp Business API → Get approved → Generate API token
  - Timeline: 3-14 business days for Meta verification
  - **Workaround for soft launch:** Use direct WhatsApp links (wa.me) without API automation
- **Impact:** Without this, automated WhatsApp messages (follow-ups, notifications, deal updates) will not work
- **Resolution:** Submit Meta Business verification ASAP

### 2. Domain Setup
- **Status:** BLOCKED
- **Owner:** Technical Lead
- **Details:**
  - Domain not yet purchased (dealix.sa or dealix.com.sa)
  - `.sa` domains require Saudi Commercial Registration (سجل تجاري)
  - Alternative: Use `.com` domain initially (dealix.com)
  - DNS propagation takes 24-48 hours after configuration
- **Impact:** No production URL, no SSL, no email
- **Resolution:** Purchase domain, configure DNS records

### 3. SSL Certificate
- **Status:** BLOCKED (depends on Domain)
- **Owner:** Technical Lead
- **Details:**
  - Cannot generate SSL without domain pointing to server
  - Options: Let's Encrypt (free, auto-renew) or Cloudflare (free tier with proxy)
  - Recommended: Cloudflare for CDN + SSL + DDoS protection
- **Impact:** Site will show "Not Secure" warning, forms won't work properly
- **Resolution:** Automatically resolved once domain is configured

### 4. Production .env with Real Secrets
- **Status:** BLOCKED
- **Owner:** Technical Lead
- **Details:**
  - Current `.env.example` has placeholder values
  - Must generate: SECRET_KEY (64+ random chars), real DB password, API keys
  - See `PRODUCTION-ENV-CHECKLIST.md` for complete list
- **Impact:** Application cannot run securely in production
- **Resolution:** Generate all secrets, store securely (not in git)

---

## NOT BLOCKERS / ليست عوائق

### Payment Gateway Integration
- **Why not a blocker:** Dealix v1 is a CRM/affiliate management platform. Revenue comes from SaaS subscriptions managed externally. In-app payment processing is a Phase 2 feature.
- **Timeline:** Post-launch (Month 3-4)
- **Current workaround:** Bank transfer + manual confirmation

### AI Agent Advanced Features
- **Why not a blocker:** Core CRM, lead management, and commission tracking work without AI. AI features (smart follow-up suggestions, lead scoring) are enhancement-level, not core.
- **Timeline:** Phase 2-3 roadmap
- **Current workaround:** Manual lead prioritization

### Multi-Tenant / White-Label Support
- **Why not a blocker:** Launch is single-brand (Dealix). Multi-tenant architecture can be added later.
- **Timeline:** Phase 3+

### Mobile App
- **Why not a blocker:** Frontend is fully responsive and works on mobile browsers. Native app is a growth-phase investment.
- **Timeline:** Phase 3+
- **Current workaround:** Progressive Web App (PWA) can be enabled quickly

### Advanced Analytics / BI Dashboard
- **Why not a blocker:** Basic dashboard with KPIs is built. Advanced drill-downs and export are nice-to-haves.
- **Timeline:** Phase 2

### Unifonic SMS Integration
- **Why not a blocker:** While SMS is configured in the codebase, WhatsApp is the primary channel in Saudi Arabia. SMS is supplementary.
- **Timeline:** Can be enabled at any point by adding Unifonic credentials
- **Current workaround:** WhatsApp + Email cover the notification needs

---

## Resolution Priority / أولوية الحل

| Priority | Blocker | Estimated Time | Dependencies |
|---|---|---|---|
| 1 | Domain Setup | 1-2 days | سجل تجاري for .sa |
| 2 | SSL Certificate | 1 hour | Domain must be configured |
| 3 | Production .env | 2 hours | Domain + hosting details |
| 4 | WhatsApp API | 3-14 days | Meta Business verification |

---

## Soft Launch Option / خيار الإطلاق التجريبي

If WhatsApp API verification is delayed, a **soft launch** is possible with:
- Domain + SSL + Production .env resolved
- WhatsApp replaced with manual wa.me links
- Limited to 10-20 affiliates for testing
- Full launch once WhatsApp API is approved

> القرار: هل نطلق تجريبياً بدون WhatsApp API أو ننتظر؟
> Decision needed: Soft launch without WhatsApp API or wait?
