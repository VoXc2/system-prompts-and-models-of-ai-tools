"""AI trace logging — tracks every AI action for governance and cost control."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class AITrace(TenantModel):
    """Audit trail for every AI invocation."""
    __tablename__ = "ai_traces"

    # Who triggered it
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=True, index=True)

    # What was done
    workflow = Column(String(100), nullable=False, index=True)  # chat, qualify, discover, outreach, content, proposal
    action = Column(String(100), nullable=False)  # think, generate, classify, score, summarize
    status = Column(String(50), default="success", index=True)  # success, error, timeout, filtered

    # AI provider details
    provider = Column(String(50), nullable=False)  # openai, anthropic, gemini
    model = Column(String(100), nullable=False)  # gpt-4o-mini, claude-sonnet-4-20250514, gemini-2.0-flash
    temperature = Column(Numeric(3, 2))

    # Input/output
    system_prompt = Column(Text)
    user_message = Column(Text)
    response = Column(Text)
    tool_calls = Column(JSONB, default=list)

    # Cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6), default=0)

    # Performance
    latency_ms = Column(Integer)
    retries = Column(Integer, default=0)

    # Governance
    was_filtered = Column(String(50))  # None, guardrail, rate_limit, scope_violation
    human_override = Column(String(50))  # None, approved, rejected, edited
    error_message = Column(Text)

    extra_data = Column("metadata", JSONB, default=dict)
