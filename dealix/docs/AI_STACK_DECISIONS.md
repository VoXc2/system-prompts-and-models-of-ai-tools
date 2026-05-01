# AI Stack Decisions — Dealix v3

## Current immediate stack

- **FastAPI** — primary API surface.
- **Supabase / Postgres / pgvector** — project + strategic memory (see migration + setup doc).
- **Deterministic internal agent runtime** — `SafeAgentRuntime` patterns in v3 routers; no silent outbound execution.
- **Deterministic Personal Operator** — Arabic briefs, opportunities, drafts with `approval_required`.
- **Sentry / OpenTelemetry** — optional instrumentation in `api/main.py` when `dealix.observability` is present.
- **Project Intelligence (local)** — `scan_project`, `chunk_text`, `naive_search`, CLI `scripts/index_project_memory.py`.

## Next stack (when credentials and policy are ready)

- **Langfuse** — tracing, evals, prompt versioning (dependency already in project).
- **OpenAI Agents SDK** — structured traces, tool calls, guardrails.
- **LangGraph** — durable workflows with human-in-the-loop approvals.
- **LlamaIndex** — RAG over `project_chunks` + `strategic_memory`.
- **WhatsApp Cloud API** — interactive reply buttons (max 3 per message).
- **Gmail drafts API** — outbound only after approval.
- **Google Calendar** — schedule drafts first; create events only after explicit approval.

## Later stack (cost / scale driven)

- **vLLM / Ollama** — when inference cost or latency justifies self-hosting.
- **n8n / MCP** — after internal policy and audit trails are stable.
- **Dify** — prototyping only; not the core production execution path.

## Why this shape

- **Dealix owns** memory schema, PDPL posture, approval contracts, and audit semantics.
- External frameworks are **replaceable execution engines** around the same memory and policy core.
