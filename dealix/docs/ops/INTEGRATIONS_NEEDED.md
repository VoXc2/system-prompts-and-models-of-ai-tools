# 🔌 Dealix — Integrations & Subscriptions Needed

**What Sami must still arrange for the system to operate at full capacity.**

Current state: LAUNCHED + selling manually possible.
Missing: automated multi-channel outreach + automated payment + monitoring accounts.

---

## 🔴 P0 — Critical (blocks revenue or multi-channel)

### 1. Moyasar Live Activation
| Item | Detail |
|------|--------|
| **Purpose** | Accept real customer payments automatically |
| **Current status** | `account_inactive_error` |
| **Action** | Complete KYC at https://dashboard.moyasar.com/settings/business |
| **Requirements** | CR or freelance license · National ID/Iqama · IBAN · Business address |
| **Cost** | 2.5% + 1 SAR per transaction |
| **Time to activate** | 1-3 business days |
| **Alternative for today** | Create sandbox `sk_test_...` key — unlocks full technical verification within 10 min |
| **What I do on receipt** | Update Railway env → redeploy → test 1 SAR → verify webhook → mark REVENUE_VERIFIED |

### 2. WhatsApp Business API (Meta Cloud API)
| Item | Detail |
|------|--------|
| **Purpose** | AI responds to leads on WhatsApp (highest-converting Saudi channel) |
| **Current status** | Code integration exists (`integrations/whatsapp.py`) but no credentials |
| **Provider** | Meta WhatsApp Cloud API (direct) or Twilio/360dialog (easier) |
| **Direct path** | https://developers.facebook.com/docs/whatsapp/cloud-api |
| **Required env vars** | `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` |
| **Cost** | Meta: ~$0.04-0.08 per business-initiated conversation (Saudi) · first 1,000 free |
| **Time to activate** | Meta: 2-5 days (business verification). Twilio: same-day |
| **Alternative** | Twilio WhatsApp (faster KYC, slightly more expensive) or 360dialog (Saudi-friendly) |

---

## 🟡 P1 — Important (multi-channel reach)

### 3. Sentry (error monitoring)
| Item | Detail |
|------|--------|
| **Purpose** | Catch production errors before customers complain |
| **Current status** | SDK loaded in backend, `SENTRY_DSN` empty |
| **Signup** | https://sentry.io → Create project "dealix" (Python/FastAPI template) |
| **Cost** | Free tier: 5K errors/month (plenty for Dealix scale) |
| **Time** | 5 minutes |
| **Env var needed** | `SENTRY_DSN=https://<hash>@<org>.ingest.sentry.io/<proj>` |

### 4. UptimeRobot (optional — GitHub Actions already covers)
| Item | Detail |
|------|--------|
| **Purpose** | Redundant monitoring with SMS alerts |
| **Current status** | GitHub Actions scheduled_healthcheck runs every 15 min |
| **Signup** | https://uptimerobot.com |
| **Cost** | Free tier: 50 monitors, 5-min interval |
| **Time** | 5 minutes |
| **Skip if** | You trust GitHub Actions (recommended) |

### 5. HubSpot Free CRM
| Item | Detail |
|------|--------|
| **Purpose** | Replace the manual `pipeline_tracker.csv` once you have 10+ customers |
| **Current status** | Webhook endpoint ready at `/api/v1/webhooks/hubspot` |
| **Signup** | https://www.hubspot.com/products/crm |
| **Cost** | Free for unlimited contacts |
| **Time** | 15 minutes |
| **Env vars needed** | `HUBSPOT_API_KEY`, `HUBSPOT_PORTAL_ID` |

### 6. Calendly Paid Plan (Webhooks)
| Item | Detail |
|------|--------|
| **Purpose** | Auto-notify backend when demo is booked (so we can send confirmation + log in CRM) |
| **Current status** | Free Calendly URL works for booking; webhook endpoint exists at `/api/v1/webhooks/calendly` |
| **Required** | Calendly Standard plan ($10/mo) for webhook access |
| **Time** | 10 minutes setup after plan upgrade |
| **Alternative** | Stay free + rely on email notifications (manual lag) |

---

## 🟢 P2 — Nice to have (scaling)

### 7. PostHog (analytics)
| Item | Detail |
|------|--------|
| **Purpose** | Track funnel events, conversion rates, user behavior |
| **Current status** | SDK loaded, key in Railway (was leaked + rotated) |
| **Signup** | https://posthog.com or self-host |
| **Cost** | Free up to 1M events/month |
| **Time** | 10 minutes |
| **Env vars** | `POSTHOG_API_KEY`, `POSTHOG_HOST` |

### 8. Twitter/X API (for programmatic posting)
| Item | Detail |
|------|--------|
| **Purpose** | Auto-post build-in-public updates |
| **Current status** | Not integrated |
| **Signup** | https://developer.twitter.com |
| **Cost** | Basic: $100/mo · Free tier (read-only) exists |
| **Skip if** | Manual posting by Sami is fine for first 3 months |

### 9. SendGrid / Resend (transactional email)
| Item | Detail |
|------|--------|
| **Purpose** | Send welcome emails, payment confirmations, demo reminders |
| **Current status** | Not integrated — using manual Gmail |
| **Signup** | https://resend.com (simpler) or https://sendgrid.com |
| **Cost** | Resend: free 3K emails/month · SendGrid: free 100/day |
| **Time** | 10 min + DNS records for domain auth |
| **Env var** | `RESEND_API_KEY` or `SENDGRID_API_KEY` |

### 10. Domain: dealix.sa or dealix.ai
| Item | Detail |
|------|--------|
| **Purpose** | Professional URL instead of voxc2.github.io/dealix |
| **Current status** | Landing runs on github.io subdomain |
| **Registrars** | dealix.sa: via SaudiNIC (requires CR) · dealix.ai: any registrar (~$80/year) |
| **Cost** | `.sa`: 120 SAR/year (CR required) · `.ai`: $60-100/year · `.com`: $15/year |
| **DNS** | Point to voxc2.github.io via CNAME + GitHub Pages custom domain setting |
| **Time** | 30 min (once domain purchased) |

### 11. GitHub Actions Secrets
| Item | Detail |
|------|--------|
| **Purpose** | Enable auto-deploy workflow `.github/workflows/railway_deploy.yml` |
| **Current status** | Workflow exists but inactive (needs RAILWAY_TOKEN as secret) |
| **How** | https://github.com/VoXc2/dealix/settings/secrets/actions → Add `RAILWAY_TOKEN` |
| **Value** | The Railway API token you already provided |
| **Time** | 1 minute |
| **Benefit** | Every main push auto-deploys to Railway with smoke test |

---

## 🎁 Optional Power-Ups (post first revenue)

### 12. Apollo.io / Hunter.io (lead enrichment)
Get Saudi business contacts with email + LinkedIn verified.
- Apollo: $49/mo · 600 credits/month
- Hunter: $49/mo · 500 searches

### 13. Loom (demo recording)
Record async product demos to send as alternative to live calls.
- Free up to 25 videos

### 14. Notion (customer-facing wikis)
Create per-customer knowledge bases during onboarding.
- Free personal plan sufficient

### 15. Figma (visual assets)
Design proper Dealix logo, case study graphics, pitch deck visuals.
- Free tier works

---

## 📋 Purchase Priority (if budget is tight)

**Today (~$0):**
- Moyasar sandbox: free
- Sentry: free
- HubSpot Free: free
- GitHub Actions RAILWAY_TOKEN secret: free
- Resend: free

**Week 1 (~$30):**
- Calendly Standard: $10/mo
- Meta WhatsApp: pay-as-you-go (~$20 for first month of testing)

**Month 1 (~$150):**
- Domain dealix.sa: 120 SAR/year
- Apollo.io starter: $49/mo

**Month 3 (after first 3 customers):**
- Upgrade HubSpot to Pro: $100/mo
- Add Loom Business: $12/mo

---

## 🚦 What's Blocking Dealix From Full Autopilot

| Blocker | Unblock | ETA |
|---------|---------|-----|
| Moyasar KYC | Sami submits business docs OR sends sandbox test key | 1-3 days OR instant |
| WhatsApp API | Meta Business verification OR Twilio signup | 2-5 days OR 1 day |
| Sentry DSN | Create project, send DSN to me | 5 min |
| Email sender | Pick Resend/SendGrid, get API key | 15 min |
| Domain | Purchase + DNS update | 30 min (after purchase) |

**Most critical next step:** Moyasar sandbox key. Everything else can wait 7-14 days.

---

## 🔐 How Sami Provides Credentials Safely

**DO NOT paste secrets in chat.** Instead:

### For Railway env vars (fastest):
1. Open Railway → Variables → Raw Editor
2. Paste the new key → Save → Redeploy
3. Tell me "WHATSAPP_ACCESS_TOKEN added to Railway"
4. I verify via env-var query (masked) and test integration

### For GitHub secrets:
1. Open https://github.com/VoXc2/dealix/settings/secrets/actions
2. Add secret → paste value → Save
3. I trigger workflow to verify

### For API keys I need to test (e.g., Sentry DSN, Moyasar test key):
1. Paste in a **temporary** issue comment on GitHub (I read it via API)
2. Delete the comment after I confirm use
3. OR send via encrypted channel (Signal, 1Password shared vault)

**Never send credentials via WhatsApp or email in plain text.**

---

## 🎯 After All Integrations Are Live

The system will:
- ✅ Receive payments via Moyasar automatically
- ✅ Reply to WhatsApp leads in Saudi dialect 24/7
- ✅ Log every error to Sentry with Slack alerts
- ✅ Send welcome emails automatically via Resend/SendGrid
- ✅ Sync leads + conversions to HubSpot CRM
- ✅ Book demos via Calendly with webhook confirmation
- ✅ Auto-deploy from GitHub push via Railway workflow
- ✅ Track full funnel in PostHog

**Total monthly cost at full capacity: ~$250/month**
**Total setup time (if Sami focuses): ~6 hours spread over 2 weeks**
