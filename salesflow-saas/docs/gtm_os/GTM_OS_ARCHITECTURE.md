# Dealix GTM OS — Architecture

## Overview
```
Company Input → Research → Enrichment → ICP Detection → Opportunity Mapping
→ Channel Strategy → Message Generation → Compliance Check
→ Human Approval / Safe Automation → CRM Tracking → Learning Loop
```

## Layers

### A. Data Layer
Collects from allowed sources only:
- Uploaded company files
- Public websites
- Google Programmable Search / Tavily
- Official APIs
- CRM data
- Inbound messages
- Manual imports

### B. Intelligence Layer
13 specialized agents understand companies, markets, and opportunities.

### C. Compliance Layer
Decides: allowed / manual_required / opt_in_required / prohibited

### D. Execution Layer
Only safe actions: drafts, CRM tasks, scorecards, content packs, approved campaigns.

### E. Learning Layer
Tracks replies, demos, conversions. Updates ICP, scoring, messages, channels weekly.

## 13 Agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| Supervisor | Orchestrates all | CompanyInput | Full GTM Pack |
| Company Research | Understands company | Name/URL/sector | CompanyIntelligence |
| Web Search | Searches allowed sources | Query | SearchResults |
| Enrichment | Adds data | CompanyInput | EnrichedCompany |
| ICP Strategist | Determines ideal customers | CompanyIntelligence | ICPList |
| Partnership Strategist | Maps partnership types | CompanyIntelligence | PartnershipMap |
| Channel Strategy | Picks best channel | Company + Compliance | ChannelPlan |
| Message Generation | Writes Arabic messages | Company + Channel | OutreachMessage |
| Compliance | Enforces platform rules | Channel + Action | Decision |
| Campaign Orchestrator | Builds sequences | Company + Messages | CampaignSequence |
| Negotiation | Handles objections | Reply + Context | NegotiationResponse |
| CRM & Revenue | Tracks status | Events | StatusUpdate |
| Learning | Improves system | Results | UpdatedStrategy |

## Automation Boundaries

| Level | What | Examples |
|-------|------|---------|
| Fully Automated | Internal processing | Research, scoring, drafts, CRM tasks, reports |
| Semi-Automated | Approved channels | Email with opt-out, inbound chatbot, WhatsApp templates |
| Manual Required | Risky channels | LinkedIn DMs, Instagram DMs, phone calls |
| Prohibited | Policy violation | LinkedIn scraping, WhatsApp blast, fake accounts |

## Safety Rules
- LinkedIn: NO scraping/bots/automated DMs
- X: NO unsolicited automated replies/mentions
- WhatsApp: opt-in only, stop on "إيقاف"
- Instagram: inbound/official API only
- TikTok: content + official ads/lead forms only
