"""
Decision Plane — AI reasoning layer.

Built on: Responses API, Structured Outputs, function calling, MCP connectors,
          Agents SDK tracing + guardrails.

Responsibilities:
- Structured decision outputs with JSON Schema enforcement
- Model routing (Codex, GPT, Opus, Sonnet) by task class
- Tool verification before execution
- Guardrail evaluation on every agent action
- Tracing of all decisions with correlation IDs
"""
