"""
High-quality prompts library inspired by Karpathy's prompting principles:
- explicit role, explicit task, explicit output format
- chain-of-thought where useful
- few-shot where stable
- bilingual (AR/EN) for the Saudi market

مكتبة prompts عالية الجودة:
- دور واضح، مهمة واضحة، تنسيق إخراج واضح
- سلسلة تفكير عند الحاجة
- أمثلة ثابتة حيث يفيد
- ثنائية اللغة للسوق السعودي
"""

from __future__ import annotations

PAIN_EXTRACTION_PROMPT = """You are a B2B sales analyst for the Saudi market.
Given a lead's message, extract:
1. Pain points (concrete business problems)
2. Urgency signals (0.0–1.0)
3. Likely offer that would fit
4. Recommended next step

Respond in STRICT JSON only:
{{
  "pain_points": [{{"text": str, "category": str, "severity": 0-1}}],
  "urgency_score": float,
  "likely_offer": str,
  "recommended_next_step": str,
  "key_phrases": [str]
}}

Lead message (language: {locale}):
---
{message}
---
"""

ICP_REASONING_PROMPT = """You are an ICP (Ideal Customer Profile) matcher.
Given the lead details and ICP definition, reason step by step then output JSON.

Lead:
{lead_json}

ICP:
{icp_json}

Output STRICT JSON:
{{
  "overall_score": float,  // 0.0 - 1.0
  "industry_match": float,
  "size_match": float,
  "region_match": float,
  "budget_match": float,
  "pain_match": float,
  "reasons": [str],
  "recommendations": [str]
}}
"""

PROPOSAL_GENERATION_PROMPT = """You are a senior proposal writer for an AI consulting firm in Saudi Arabia.
Write a polished, {locale} proposal for the client below.
Tone: confident, consultative, Vision 2030 aware.
Length: ~500 words.
Include: Executive summary, Understanding of needs, Proposed solution, Phases, Pricing (SAR), Next steps.

Client context:
- Company: {company_name}
- Sector: {sector}
- Pain points: {pain_points}
- Target outcomes: {outcomes}
- Budget range (SAR): {budget_min} — {budget_max}
- Preferred start: {start_date}

Write the proposal in {locale}. Use markdown headings.
"""

CONTENT_WRITER_PROMPT = """You are a senior content strategist writing for a Saudi AI consulting firm.
Audience: {audience}
Goal: {goal}
Channel: {channel}
Language: {locale}

Topic: {topic}

Write a {length}-word piece with:
- Hook in first line
- 3–5 clear sections with subheadings
- Concrete Saudi examples where possible
- Closing CTA: {cta}

Return only the finished piece in {locale}. Use markdown.
"""

SECTOR_ANALYSIS_PROMPT = """You are a market analyst.
Analyze the Saudi {sector} sector:
1. Market size and growth
2. Top 5 pain points solvable by AI
3. 5 concrete AI opportunities (practical, buildable)
4. AI readiness (0–1)
5. Key regulations / Vision 2030 alignment
6. 3 recommended go-to-market moves for an AI consulting firm

Return STRICT JSON:
{{
  "market_size_sar": number,
  "growth_rate": float,
  "pain_points": [str],
  "opportunities": [str],
  "ai_readiness": float,
  "regulations": [str],
  "gtm_moves": [str]
}}
"""

QUALIFICATION_QUESTIONS_PROMPT = """You are a discovery call coach.
Given the lead context, generate 5 high-leverage qualification questions in {locale}.
Frame in BANT (Budget, Authority, Need, Timeline) but mix naturally.
Return STRICT JSON: {{"questions": [{{"q": str, "bant": str, "why": str}}]}}

Context:
{context}
"""

COMPETITOR_SUMMARY_PROMPT = """You are a competitive analyst.
Given competitor info, produce a concise summary in {locale}:
- Positioning
- Pricing hints
- Strengths
- Weaknesses we can exploit
- 3 counter-moves

Competitor data:
{data}

Return markdown, max 300 words.
"""

OUTREACH_OPENER_PROMPT = """Write a {channel} outreach opener in {locale} to {name} at {company}.
Reference: {trigger}
Goal: book a 15-min discovery call.
Tone: respectful, consultative, Saudi-business-appropriate.
Max 4 sentences. No fluff, no "I hope this finds you well".
"""

FOLLOWUP_PROMPT = """Write follow-up #{attempt} to the lead.
Previous messages summary: {history}
Lead status: {status}
Language: {locale}

Guidelines:
- Attempt 1: add value (share relevant insight)
- Attempt 2: reference first message + soft CTA
- Attempt 3: break-up message (respectful)

Max 3 sentences. Return plain text.
"""


PROMPTS: dict[str, str] = {
    "pain_extraction": PAIN_EXTRACTION_PROMPT,
    "icp_reasoning": ICP_REASONING_PROMPT,
    "proposal_generation": PROPOSAL_GENERATION_PROMPT,
    "content_writer": CONTENT_WRITER_PROMPT,
    "sector_analysis": SECTOR_ANALYSIS_PROMPT,
    "qualification_questions": QUALIFICATION_QUESTIONS_PROMPT,
    "competitor_summary": COMPETITOR_SUMMARY_PROMPT,
    "outreach_opener": OUTREACH_OPENER_PROMPT,
    "followup": FOLLOWUP_PROMPT,
}


def get_prompt(name: str, **kwargs: object) -> str:
    """Fetch and format a prompt | جلب prompt وتعبئته."""
    template = PROMPTS.get(name)
    if template is None:
        raise KeyError(f"Unknown prompt: {name}")
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise KeyError(f"Missing argument for prompt {name!r}: {e}") from e
