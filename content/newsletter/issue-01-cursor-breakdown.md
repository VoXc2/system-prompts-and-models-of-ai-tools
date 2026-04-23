# LeaksLab Weekly — Issue #01
## Inside Cursor's System Prompt: What 8,000 Words of Instructions Reveal

*The first deep-dive analysis. Every Friday, one AI tool. This week: Cursor.*

---

**Reading time**: ~7 minutes

---

### Why Cursor First?

Cursor is currently the most-starred AI coding editor with millions of active users. It is also one of the most architecturally sophisticated — its system prompt is longer than most startup pitch decks.

This week we break it down.

---

### The Structure

Cursor's system prompt has five distinct sections:

1. **Identity & Behavior Rules** — Who the AI is, how it should respond, tone, and limits
2. **Tool Definitions** — 8 specialized tools with full JSON schemas
3. **Code Generation Rules** — Specific instructions for writing, editing, and refactoring
4. **Context Management** — How it handles the codebase, search, and memory
5. **Edge Cases** — What to do when it cannot do something, how to recover

This layered structure is not accidental. It maps directly to how production AI agents are built at scale.

---

### The 8 Tools (This is the Most Interesting Part)

Cursor gives its AI eight tools. Most people focus on the prompt text, but the tools are where the real architecture lives:

| Tool | Purpose | Notable Detail |
|------|---------|----------------|
| `codebase_search` | Semantic search over the codebase | Has explicit ranking instructions |
| `read_file` | Read file contents with line ranges | Forces explicit line number citations |
| `run_terminal_cmd` | Execute shell commands | Requires user approval flag |
| `list_dir` | Directory exploration | Depth-limited to prevent token explosion |
| `grep_search` | Regex/text search | Separate from semantic search by design |
| `edit_file` | Make code changes | Uses diff format, not full rewrites |
| `file_search` | Fuzzy file name lookup | Fuzzy matching for typo tolerance |
| `web_fetch` | Fetch URL content | Rate-limited, output truncated |

**What this reveals**: Cursor deliberately separates semantic search from text search. This is a sophisticated decision — semantic search is expensive and slow, text search is fast and cheap. Using both at the right time is an architectural decision most junior agent builders miss.

---

### The Behavior Rules: Three Things Worth Copying

**1. Explicit refusal to be overly helpful**

Cursor's prompt tells the AI: "Do not be excessively helpful — do exactly what is asked and no more." This prevents scope creep in code changes. Applied to your agents: always define what the agent should NOT do as clearly as what it should.

**2. Line number citations are mandatory**

Every code reference must include a file path and line number. This creates auditability — you can always trace where a suggestion came from. Applied to your agents: require structured output formats that include provenance.

**3. Failure is explicit**

The prompt has a dedicated section for what happens when a tool fails. Rather than letting the AI improvise, it gives explicit fallback instructions. Applied to your agents: always have a defined failure path.

---

### The Pattern That Surprised Me

Most AI tools have a generic "be helpful, be safe, be accurate" preamble. Cursor's prompt skips that almost entirely and goes straight into operational instructions.

This signals a mature product philosophy: the safety layer is handled at the model level (Claude/GPT training), not the prompt level. The prompt is purely operational.

This is why Cursor feels faster and more decisive than many other tools — there is less meta-instruction weighing down every response.

---

### What to Borrow for Your Own Agents

If you are building an AI agent today, here are three patterns from Cursor's prompt worth directly adopting:

1. **Tool separation by speed** — Have a cheap/fast tool and an expensive/accurate tool for the same task. Let context decide which one to use.

2. **Mandatory structured output** — Require your agent to always include file paths, line numbers, or IDs in its responses. Auditability is free if you enforce it from the start.

3. **Explicit no-ops** — Define what the agent should NOT do. This single change will cut your hallucination rate more than any prompt engineering trick.

---

### Next Week

We break down **Manus Agent** — the most architecturally complex prompt in the library, with 15+ tools and an explicit multi-agent orchestration system.

---

*LeaksLab is a community library of AI tool system prompts. Everything analyzed here is from our open GitHub repository: [github.com/VoXc2/system-prompts-and-models-of-ai-tools](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools)*

*Forward this to one engineer who is building AI tools. That is the best way to grow this newsletter.*

---
