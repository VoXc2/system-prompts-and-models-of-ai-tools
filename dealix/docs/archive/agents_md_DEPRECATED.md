# Agents Reference

Every agent extends `core.agents.base.BaseAgent` and exposes `async def run(**kwargs)`.

---

## Phase 8 — Auto Client Acquisition

### IntakeAgent
**File**: `auto_client_acquisition/agents/intake.py`

Captures leads from any source, normalizes them, detects duplicates.

**Inputs**:
- `payload: dict[str, Any]` — raw lead data
- `source: LeadSource | str` — where it came from

**Output**: `Lead` dataclass with:
- Normalized `contact_phone` (E.164 via `phonenumbers`)
- Normalized `contact_email` (lowercase, validated)
- Detected `locale` (`ar` or `en`) from message text
- `dedup_hash` — SHA-256 of `(email or phone) + company`
- `metadata.is_duplicate` flag

**Sources supported**: `website`, `whatsapp`, `email`, `referral`, `linkedin`, `cold_outreach`, `manual`, `api`.

---

### ICPMatcherAgent
**File**: `auto_client_acquisition/agents/icp_matcher.py`

Scores leads against an Ideal Customer Profile across **5 weighted dimensions**.

**Weights** (sum to 1.0):
- Industry: 0.25
- Size: 0.15
- Region: 0.20
- Budget: 0.20
- Pain: 0.20

**Output**: `FitScore` with per-dimension scores + overall tier (`A`/`B`/`C`/`D`) + recommendations.

**Default ICP**: target industries (tech, real estate, healthcare, education, logistics), GCC regions, SAR 10k–200k budget.

---

### PainExtractorAgent
**File**: `auto_client_acquisition/agents/pain_extractor.py`

**Hybrid extraction**:
1. Fast keyword pass (local, zero-cost) — scans AR+EN keyword dictionary
2. LLM enrichment — routed to **GLM for Arabic**, Claude otherwise

**Output**: `ExtractionResult` with pain points, urgency 0–1, likely offer, recommended next step.

---

### QualificationAgent
**File**: `auto_client_acquisition/agents/qualification.py`

Generates **5 BANT questions** (Budget / Authority / Need / Timeline) and updates lead status.

**LLM-first** with bilingual fallback question sets if LLM fails.

**Status advancement**:
- BANT ≥ 3 → `QUALIFIED`
- BANT ≥ 2 → `DISCOVERY`

---

### BookingAgent
**File**: `auto_client_acquisition/agents/booking.py`

**Priority order**:
1. Calendly — returns scheduling link (self-service)
2. Google Calendar — creates event directly (if service account configured)
3. Manual fallback — returns "team will contact you" message

**Saudi weekend aware** — skips Friday/Saturday when picking default slots.

---

### CRMAgent
**File**: `auto_client_acquisition/agents/crm.py`

HubSpot integration:
- Upserts contact by email (handles 409 conflicts via search-then-update)
- Creates deal with stage mapped from lead status
- Associates deal ↔ contact

Uses tenacity retry with exponential backoff.

---

### ProposalAgent
**File**: `auto_client_acquisition/agents/proposal.py`

Generates proposals via Claude (`Task.PROPOSAL`).

**Region-aware pricing**:
- Saudi Arabia → `PRICING_SA_*` from settings
- Other GCC → `PRICING_GCC_*`
- Global → `PRICING_GLOBAL_*_USD`

**Output**: `Proposal` with markdown body + 30-day validity.

---

### OutreachAgent
**File**: `auto_client_acquisition/agents/outreach.py`

Bilingual cold opener generation per channel (email, WhatsApp, LinkedIn, SMS).

Email variant includes a bilingual subject line builder.

---

### FollowUpAgent
**File**: `auto_client_acquisition/agents/followup.py`

**Cadence**: [0d, 3d, 7d, 14d] by default.

- Attempts 1–2 use canned bilingual scripts.
- Attempts 3+ use LLM with prior-history context.
- Auto-pauses on terminal statuses (won/lost/disqualified).

---

### AcquisitionPipeline
**File**: `auto_client_acquisition/pipeline.py`

Orchestrates the full funnel with **per-step error isolation**. Failures in any step appear in `result.warnings` but never abort the pipeline.

---

## Phase 9 — Autonomous Growth

### SectorIntelAgent
**File**: `autonomous_growth/agents/sector_intel.py`

Curated data for **12 Saudi sectors**. Can optionally enrich with LLM research.

Methods:
- `run(sector, enrich_with_llm=False)` — single sector
- `best_opportunity()` — highest (growth × AI readiness)
- `target_sectors()` — top 5

---

### ContentCreatorAgent
**File**: `autonomous_growth/agents/content.py`

Generates articles, LinkedIn posts, case studies, newsletters, tweet threads.

Arabic content → GLM (for nuance); English content → Claude.

---

### DistributionAgent
**File**: `autonomous_growth/agents/distribution.py`

Plans when to publish across channels using Riyadh-timezone optimal slots.

**Optimal times** (examples):
- LinkedIn: 8am, 12pm, 5pm
- Twitter: 9am, 1pm, 7pm
- Email: 9am
- WhatsApp broadcast: 7pm

---

### EnrichmentAgent
**File**: `autonomous_growth/agents/enrichment.py`

**Three-layer enrichment**:
1. Email domain → sector hints (e.g., `aramco.com` → `oil_gas`)
2. Phone country code → region
3. LLM inference from company name (best-effort)

---

### CompetitorMonitorAgent
**File**: `autonomous_growth/agents/competitor.py`

Summarizes competitor intel into: positioning, pricing hints, strengths, weaknesses, counter-moves.

---

### MarketResearchAgent
**File**: `autonomous_growth/agents/market_research.py`

Uses **Gemini** (`Task.RESEARCH`) for source-dense research with three depth levels (quick/standard/deep).

Output includes summary + bullet points + explicit caveats section.

---

## Prompt library

All prompts live in `core/prompts/karpathy_prompts.py`. Every prompt is **Karpathy-style**: explicit role, explicit task, explicit output format.

Registered prompts: `pain_extraction`, `icp_reasoning`, `proposal_generation`, `content_writer`, `sector_analysis`, `qualification_questions`, `competitor_summary`, `outreach_opener`, `followup`.

Sales scripts (canned bilingual) in `core/prompts/sales_scripts.py`: `opener`, `follow_up_1`, `follow_up_2`, `demo_confirm`, `proposal_cover`.

---

## Extending with a new agent

```python
# auto_client_acquisition/agents/my_agent.py
from core.agents.base import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"

    async def run(self, *, foo: str, **_) -> dict:
        self.log.info("running", foo=foo)
        response = await self.router.run(
            task=Task.REASONING,
            messages=f"Process this: {foo}",
        )
        return {"result": response.content}
```

Register it in `auto_client_acquisition/agents/__init__.py` and optionally add to `pipeline.py`.
