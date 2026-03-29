# AI Agent System

## Architecture

```
Agent Registry (config)
  → Prompt Assets (templates + system prompts)
    → AI Brain (multi-provider wrapper)
      → Structured Output (JSON contracts)
        → Approval Gate (human-in-the-loop)
          → Execution (action taken)
            → Trace Log (audit + cost)
              → Eval (quality check)
```

## Agent Registry

### 20 Revenue Agents

| # | Agent | Scope | Approval Required |
|---|-------|-------|-------------------|
| 1 | **Revenue Orchestrator** | Route incoming to correct agent | No |
| 2 | **Lead Intake Agent** | Parse and normalize incoming leads | No |
| 3 | **Qualification Agent** | Score and qualify leads (0-100) | No |
| 4 | **Routing Agent** | Match lead to best agent/team | No |
| 5 | **Follow-up Draft Agent** | Draft follow-up messages | Yes (first time per lead) |
| 6 | **Meeting Prep Agent** | Prepare meeting briefings | No |
| 7 | **Proposal Draft Agent** | Generate proposal content | Yes |
| 8 | **Reactivation Agent** | Draft reactivation messages for dormant leads | Yes |
| 9 | **Content Research Agent** | Research topics, competitors, trends | No |
| 10 | **Hook & Angle Agent** | Generate content hooks and angles | No |
| 11 | **Social Listening Agent** | Analyze social posts for relevance/ICP match | No |
| 12 | **Comment Draft Agent** | Draft comments for social posts | Yes (always) |
| 13 | **Attribution Analyst Agent** | Analyze channel performance, suggest optimization | No |
| 14 | **Executive Summary Agent** | Generate weekly/monthly executive reports | No |
| 15 | **Compliance Review Agent** | Check content for PDPL/regulatory issues | No |
| 16 | **Reliability Monitor Agent** | Detect anomalies in system health | No |
| 17 | **Operator Copilot Agent** | Assist operators with tenant management | No |
| 18 | **Client Success Agent** | Identify at-risk clients, suggest actions | No |
| 19 | **Expansion Opportunity Agent** | Identify upsell/cross-sell opportunities | No |
| 20 | **Workflow QA Agent** | Check sequence quality, suggest improvements | No |

## Agent Definition Template

### Example: Qualification Agent
```yaml
name: Qualification Agent
id: qualification_agent
role: Score and qualify inbound leads based on ICP fit and buying signals
scope:
  - Read lead data (name, phone, email, source, extra_data)
  - Read tenant's industry and ICP criteria
  - Read playbook qualification_criteria
allowed_tools:
  - read_lead
  - read_playbook
  - update_lead_score
disallowed_actions:
  - Send messages
  - Delete data
  - Access other tenants
input_contract:
  lead_id: UUID
  tenant_id: UUID
output_contract:
  score: integer (0-100)
  qualification_status: "qualified" | "unqualified" | "needs_info"
  reasoning: string
  signals: list[string]
  suggested_next_action: string
approval_gate: none
confidence_threshold: 0.7
trace_required: true
success_metric: "qualified leads that convert to deals within 30 days"
failure_behavior: "Return score=50, status=needs_info, log error"
escalation: "If confidence < 0.5, flag for human review"
```

## Structured Output Contracts

### Lead Scoring Output
```json
{
  "$schema": "lead_scoring_v1",
  "score": 75,
  "qualification_status": "qualified",
  "reasoning": "Strong ICP match: healthcare industry, 50+ employees, expressed interest in pipeline management",
  "signals": [
    "Industry match: healthcare (Tier A)",
    "Company size: 50+ (target range)",
    "Expressed pain: losing leads",
    "Budget indicator: asked about pricing"
  ],
  "suggested_next_action": "Schedule discovery call within 24h",
  "confidence": 0.85
}
```

### Comment Draft Output
```json
{
  "$schema": "comment_draft_v1",
  "content": "نقطة مهمة جداً! في تجربتنا مع العيادات...",
  "tone": "professional",
  "account_type": "brand",
  "relevance_score": 85,
  "icp_match": "strong",
  "reasoning": "Post discusses healthcare operations challenges, direct ICP match",
  "requires_approval": true
}
```

### Proposal Content Output
```json
{
  "$schema": "proposal_content_v1",
  "title": "عرض إعداد نظام إدارة الإيرادات",
  "executive_summary": "...",
  "scope_items": [
    {"description": "...", "amount": 15000}
  ],
  "total": 45000,
  "timeline_days": 14,
  "terms": "...",
  "confidence": 0.8
}
```

## AI Brain Wrapper

```python
class AIBrain:
    async def think(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: dict = None,  # JSON schema for structured output
        tenant_id: str = None,
        workflow: str = None,
        action: str = None,
    ) -> AIResponse:
        # 1. Select provider (primary → fallback)
        # 2. Make API call
        # 3. Parse response (validate against schema if provided)
        # 4. Create AITrace record
        # 5. Return structured result
```

## Provider Fallback Logic
```
Primary: OpenAI (gpt-4o-mini) — fast, cheap, good for most tasks
Fallback 1: Anthropic (claude-sonnet) — for complex reasoning
Fallback 2: OpenAI (gpt-4o) — for critical tasks needing highest quality

Trigger fallback when:
  - Primary returns error
  - Primary timeout > 30s
  - Primary content filtered
  - Task marked as "high_importance"
```

## Cost Tracking
- Every AI call logged with `input_tokens`, `output_tokens`, `cost_usd`
- Daily/weekly/monthly cost aggregation per tenant
- Alert when tenant approaches cost threshold
- Cost dashboard in operator console
