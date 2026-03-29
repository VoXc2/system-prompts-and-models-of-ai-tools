# Assumptions

## Market Assumptions
1. Saudi B2B SMEs are underserved by existing CRM/sales tools (too complex, not Arabic-first)
2. WhatsApp is the primary business communication channel in Saudi Arabia
3. Managed service model is more attractive than pure SaaS for first 50 clients
4. Clinics, real estate, B2B services, training, and industrial suppliers have the highest ROI potential
5. Arabic-first UX is a competitive moat — most competitors are English-first with translation

## Technical Assumptions
1. PostgreSQL 16 can handle 1000+ tenants in shared-database model at current scale
2. Redis 7 is sufficient for caching, rate limiting, and Celery broker
3. WhatsApp Business API will remain available and cost-effective
4. OpenAI/Anthropic API pricing will remain stable or decrease
5. Alembic can manage schema evolution for 35+ tables without issues
6. Single-region deployment (Saudi Arabia) is sufficient for Phase 1

## Product Assumptions
1. Clients will adopt pipeline velocity as their north star metric
2. AI-drafted content with human approval is acceptable to the market
3. Integration with existing tools (Google Calendar, Outlook) is required for adoption
4. Mobile-responsive web app is sufficient — native mobile app not needed for Phase 1
5. Self-serve onboarding can be completed in under 30 minutes

## Operational Assumptions
1. Dealix team of 3-5 operators can manage 20-30 managed service clients
2. White-label partners will need minimal training (< 2 hours)
3. Social listening can be done via API without browser automation
4. Email deliverability can be maintained via dedicated IPs and warm-up

## Financial Assumptions
1. Average Revenue Per Account (ARPA): 10,000-15,000 SAR/month for managed service
2. Self-serve SaaS ARPA: 1,500-3,000 SAR/month
3. CAC payback period target: < 6 months
4. Gross margin target: > 70% for SaaS, > 50% for managed service

## Risk Assumptions
1. Regulatory: PDPL enforcement will increase — compliance must be proactive
2. Competition: HubSpot/Salesforce may add Arabic support — speed is critical
3. AI: Model quality improvements will help, but governance overhead will remain
4. Scale: Performance bottlenecks will appear around 100K leads per tenant
