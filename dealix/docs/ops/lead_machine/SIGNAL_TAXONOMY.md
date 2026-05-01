# Dealix Signal Taxonomy — v1

Signals are observable, public evidence that a company/person matches a use case. Every signal has: name, use_case, weight, evidence hint, typical source.

---

## DIRECT_CUSTOMER (Sales) — company fit signals

| Signal | Weight | Evidence hint | Typical source |
|--------|--------|---------------|----------------|
| B2B sales model | 5 | Pricing page, case studies | Company site |
| Arabic market focus | 5 | Arabic site, Saudi customers named | Company site |
| High lead volume | 10 | Multiple form types, many CTAs, traffic signals | Company site |
| Active sales team | 5 | "Meet the team", SDRs, AEs on LinkedIn public | LinkedIn (manual) |
| CRM in use | 5 | HubSpot/Salesforce mentions, chat widget | Tech stack inspection |
| Booking tool in use | 5 | Calendly / HubSpot / Chili Piper visible | Page inspection |
| WhatsApp-heavy sales | 5 | WhatsApp widget, "راسلنا على واتساب" | Company site |
| Multi-branch operation | 3 | Multiple office addresses | Company site |
| Franchise/marketplace | 3 | Merchant onboarding, partner portal | Company site |
| Bilingual audience | 2 | AR + EN site versions | Company site |
| Many inbound forms | 2 | Demo, contact, quote, pricing forms | Company site |

## DIRECT_CUSTOMER — intent signals (buying readiness)

| Signal | Weight | Evidence hint | Typical source |
|--------|--------|---------------|----------------|
| Hiring SDR/BDR/sales | 8 | Open roles at Bayt/GulfTalent/LinkedIn | Job boards |
| Hiring growth/marketing | 5 | Open roles | Job boards |
| Recent funding announcement | 4 | MAGNiTT / Wamda / press | Press |
| New product/feature launch | 4 | Press release, blog | Press / company blog |
| Running paid ads | 3 | Google / Meta ads visible | Ad transparency |
| Content about sales/GTM pain | 3 | Founder posts on LinkedIn/X | Public social |
| Partnership/integration announcement | 2 | Press | Press |
| Complaint about response speed | 2 | Public reviews, social | Reviews / social |

---

## AGENCY_PARTNER signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Marketing / ads agency | 10 | "We manage paid ads" positioning |
| CRM / HubSpot / Salesforce implementer | 10 | Partner badge, case studies |
| Shopify / Salla / Zid agency | 8 | E-commerce implementation services |
| Web / landing page service | 5 | Landing pages in portfolio |
| Retainer clients (SMEs) | 8 | Case studies show SMB clients |
| Automation / workflow consulting | 5 | Service page mentions automation |
| Saudi / GCC client base | 6 | Arabic testimonials, Saudi case studies |
| Owns client distribution | 5 | Partner directory, client logos |
| Open to new revenue streams | 4 | Recent content about growth, new services |

---

## IMPLEMENTATION_PARTNER signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| RevOps / sales ops consultant | 10 | Positioning |
| CRM migration services | 8 | Service page |
| Automation / Zapier / Make expert | 6 | Portfolio |
| Listed on HubSpot/Salesforce partner directory | 8 | Public partner registry |

---

## REFERRAL_PARTNER signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Operates in Saudi business network | 8 | Events, speaking, podcast appearances |
| Owns SMB or founder audience | 6 | Newsletter, community |
| Known for intros / connector role | 5 | Public reputation |

---

## STRATEGIC_PARTNER signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| E-commerce platform (Salla/Zid/Shopify) | 10 | Platform operator w/ app store |
| CRM vendor w/ Arabic market | 10 | CRM operator |
| Payment gateway (Moyasar, Tap, PayTabs) | 8 | Gateway |
| Marketplace w/ merchant base | 8 | B2B marketplace |
| Accelerator / incubator | 6 | Known programs: Misk, Wadi, Sanabil |

---

## CONTENT_COLLABORATION signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Saudi business newsletter | 8 | Substack / personal site |
| Podcast on SaaS / AI / GTM | 8 | Spotify / Anghami |
| Founder with large AR audience on LI/X | 6 | Followers + engagement |
| Runs Saudi startup community | 6 | Slack / WhatsApp / Discord |

---

## INVESTOR_OR_ADVISOR signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Active MENA VC / angel | 10 | MAGNiTT profile, recent deals |
| Portfolio includes sales/marketing tech | 8 | Public portfolio page |
| KSA mandate (Sanabil, STV, Raed, Wamda Capital) | 10 | Fund thesis |
| Posts thesis on AI/GTM | 5 | Public blog/social |

---

## SUPPLIER_OR_INTEGRATION signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Tool/vendor that saves Dealix time | 8 | Relevance to lead-machine |
| Saudi-native tool (Wafeq, Malaa, Merit) | 6 | KSA vendor |

---

## B2C_AUDIENCE signals

| Signal | Weight | Evidence hint |
|--------|--------|---------------|
| Ecommerce checkout | 8 | Shopping cart flow |
| Appointment booking | 6 | Clinic / salon / training |
| WhatsApp-heavy sales | 8 | WhatsApp as primary channel |
| Local-service demand | 5 | Area-specific targeting |

---

## Anti-signals (reduce score or mark disqualified)

| Anti-signal | Effect |
|-------------|--------|
| Government / public entity (complex procurement) | deprioritize unless explicit |
| No public contact surface | can't open outreach → backlog |
| Recent layoffs or distress press | risk: slow to close |
| Competes directly with Dealix | disqualify |
| Non-Arabic, non-GCC only | deprioritize vs KSA ICP |

---

## Risk levels (per lead)

- **LOW** — company-level public data only, no personal contact
- **MEDIUM** — named business contact from public source (LinkedIn public page, company "About")
- **HIGH** — personal phone / personal email / cold direct marketing to individual
- **BLOCKED** — sensitive personal data, private data, no lawful source, or platform-prohibited sending method

Never contact HIGH or BLOCKED without human approval per [LEAD_MACHINE_SPEC.md](./LEAD_MACHINE_SPEC.md).
